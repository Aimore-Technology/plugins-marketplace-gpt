#!/usr/bin/env python3
"""Bound a scan and prepare durable recovery state; no scheduler, lock or I/O."""

import copy
import hashlib
import json
import re
from datetime import datetime, timedelta

from email_presentation import blocks, properties
from runtime_records import read_identity
from notion_checks import object_result, page_id


def timestamp(value):
    at = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if at.tzinfo is None:
        raise ValueError('Use actual timezone-aware clock observations')
    return at


def key(item):
    fields = [item[k] for k in ('source_key', 'step', 'version', 'input_digest')]
    if any(not isinstance(v, str) or not v.strip() for v in fields):
        raise ValueError('Work identity requires source, step, version and input digest')
    return hashlib.sha256(json.dumps(fields, separators=(',', ':')).encode()).hexdigest()


def reconcile(data):
    """Retire stale waiting pointers from original terminal tasks, not old prose.

    This reconciles queue bookkeeping only. Unknown attempts are never released,
    and cancellation never becomes evidence that a provider accepted anything.
    """
    original = blocks(data['checkpoint_page'], 'scan-checkpoint-v1')[1]
    result = copy.deepcopy(original)
    if page_id(original['root_id']) != page_id(data['root_id']):
        raise ValueError('Checkpoint belongs to another installation')
    tasks = {}
    for page in data['task_pages']:
        actual = object_result(page)
        identity = page_id(actual['id'])
        ancestors = re.findall(r'<(?:parent-page|ancestor-\d+-page)\b[^>]*url="([^"]+)"', actual['text'].split('<content>', 1)[0])
        if page_id(data['root_id']) not in {page_id(v) for v in ancestors}:
            raise ValueError('Terminal task is outside this checkpoint installation')
        if identity in tasks:
            raise ValueError('Ambiguous canonical task observations')
        tasks[identity] = properties(page)
    changes = []
    for identity, item in result['items'].items():
        if item.get('state') != 'waiting' or not item.get('receipt_ref'):
            continue
        task_id = page_id(item['receipt_ref'])
        task = tasks.get(task_id)
        if not task or task.get('State') not in {'Completed', 'Cancelled'}:
            continue
        if (task.get('ContentVersion') != item.get('version') or task.get('ResumeStep') != item.get('step')
                or item.get('source_key') not in {read_identity(task.get('TaskId')), read_identity(task.get('SourceKey'))}):
            raise ValueError('Terminal task does not match the stale checkpoint identity/version/step')
        item.update(state='completed' if task['State'] == 'Completed' else 'cancelled',
                    canonical_state=task['State'])
        changes.append({'key': identity, 'task_page_id': task_id, 'canonical_state': task['State']})
    retained = []
    for work in original.get('work_items', []):
        work_key = key(work)
        prior = result['items'].get(work_key, {})
        if not work.get('waiting') or work.get('unknown_attempt') or prior.get('state') == 'unknown':
            retained.append(work)
            continue
        matches = [(identity, task) for identity, task in tasks.items()
                   if task.get('State') in {'Completed', 'Cancelled'}
                   and task.get('ContentVersion') == work['version']
                   and task.get('ResumeStep') == work['step']
                   and work['source_key'] in {read_identity(task.get('TaskId')), read_identity(task.get('SourceKey'))}]
        if len(matches) > 1:
            raise ValueError('Multiple canonical tasks match a stale waiting work item')
        if not matches:
            retained.append(work)
            continue
        task_id, task = matches[0]
        result['items'][work_key] = {**prior, 'state': task['State'].lower(),
                                    'canonical_state': task['State'], 'receipt_ref': task_id,
                                    **{k: work[k] for k in ('source_key', 'step', 'version')}}
        if not any(c['key'] == work_key for c in changes):
            changes.append({'key': work_key, 'task_page_id': task_id, 'canonical_state': task['State']})
    if 'work_items' in original:
        result['work_items'] = retained
    return {'status': 'CheckpointReconciled', 'checkpoint': result, 'changes': changes,
            'scope': 'Prospective queue bookkeeping only; preserve original checkpoint history; no provider, approval or count change'}


def run_id(data):
    """An ordinary cycle log label, never a privileged host/session identity."""
    value = data.get('run_id', (data.get('executor') or {}).get('current_id'))
    if value is None:
        # Stable for repeated admission checks of this original cycle. Callers
        # may instead create a UUID at entry and persist it with the same start.
        value = 'run-' + hashlib.sha256(json.dumps(
            [page_id(data['root_id']), data['started_at']], separators=(',', ':')).encode()).hexdigest()[:32]
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Use a nonempty local run label; no native identity is required')
    return value


def work_scope(item):
    scope = item.get('scope')
    if scope is None:
        return None  # Legacy unknown scope remains conservative.
    if (not isinstance(scope, dict) or set(scope) - {'global', 'location_id', 'contact_id', 'channel', 'context_key'}
            or 'global' in scope and type(scope['global']) is not bool
            or any(not isinstance(v, str) or not v.strip() for k, v in scope.items() if k != 'global')
            or scope.get('channel', '*') not in {'*', 'email', 'sms', 'crm', 'calendar'}
            or bool(scope.get('location_id')) != bool(scope.get('contact_id'))
            or not scope.get('global') and not scope.get('contact_id')):
        raise ValueError('Work scope needs an observed CRM customer or explicit global barrier')
    return copy.deepcopy(scope)


def conflicts(barrier, item):
    left, right = work_scope(barrier), work_scope(item)
    if left and left.get('global') or right and right.get('global'):
        return True
    if not left or not right:
        # A legacy unscoped attempt reserves its original work, not every
        # unrelated customer/project/channel. Explicit global barriers stay global.
        return bool(barrier.get('source_key') and barrier.get('source_key') == item.get('source_key'))
    if (left['location_id'], left['contact_id']) != (right['location_id'], right['contact_id']):
        return False
    # An unknown attempt may reserve a shared customer count across contexts.
    if barrier.get('unknown_attempt'):
        return (not left.get('channel') or not right.get('channel')
                or '*' in {left.get('channel'), right.get('channel')}
                or left['channel'] == right['channel'])
    return all(not left.get(k) or not right.get(k) or '*' in {left[k], right[k]} or left[k] == right[k]
               for k in ('channel', 'context_key'))


def recovery_ready(item, prior, now):
    wake = item.get('recovery_wakeup')
    if wake is not None:
        if (not isinstance(wake, dict) or set(wake) != {'evidence_ref', 'revision'}
                or any(not isinstance(v, str) or not v.strip() for v in wake.values())):
            raise ValueError('Recovery wake-up requires original evidence and its actual revision')
        if wake != prior.get('last_recovery_wakeup'):
            return True
    due = item.get('recovery_due_at')
    return bool(due and timestamp(due) <= now and due != prior.get('last_recovery_due_at'))


def advance(data):
    from scan_control import gate
    entry = gate(data)
    if entry['status'] != 'ScanEnabled':
        return entry

    root = page_id(data['root_id'])
    if data.get('policy') not in (None, 'one-cycle-approved-work', 'one-cycle-no-customer-send', 'scheduled-approved-work'):
        return {'status': 'ScanDeferred', 'work': [], 'reason': 'This invocation policy cannot execute queue work', 'external_actions_allowed': False}
    start, now = timestamp(data['started_at']), timestamp(data['now'])
    if now < start:
        raise ValueError('Clock regressed')
    budget, reserve, limit = data.get('budget_seconds', 900), data.get('reserve_seconds', 120), data.get('max_items', 12)
    if (type(budget) is not int or not 120 <= budget <= 900 or type(reserve) is not int
            or not 30 <= reserve < budget or type(limit) is not int or not 1 <= limit <= 100):
        raise ValueError('Use a 2-15 minute budget, publication reserve and bounded item count')
    current_id = run_id(data)
    previous = {'record_type': 'scan-checkpoint-v1', 'root_id': root, 'items': {}, 'streams': {}}
    if data.get('checkpoint_page') is not None:
        previous = blocks(data['checkpoint_page'], 'scan-checkpoint-v1')[1]
        if page_id(previous['root_id']) != root:
            raise ValueError('Checkpoint belongs to a different installation')
        # The old cycle is diagnostic history, not a global execution lock.
        object_result(data['checkpoint_page'])
        if data.get('terminal_task_pages'):
            previous = reconcile({'checkpoint_page': data['checkpoint_page'], 'root_id': root,
                                  'task_pages': data['terminal_task_pages']})['checkpoint']
    states = dict(previous['items'])
    candidates = {key(v): v for v in previous.get('work_items', [])}
    queue = data.get('queue_plan')
    if queue is not None and (queue.get('status') != 'ReadyQueueConstructed' or page_id(queue['root_id']) != root):
        raise ValueError('Use the original constructed queue for this installation')
    # A narrowed caller list must not hide other ready events. Existing items
    # retain their exact scopes, estimates, digests and unknown attempts.
    current_items = list(data['items'])
    known = set(candidates) | {key(v) for v in current_items}
    for item in queue['items'] if queue is not None else []:
        if key(item) not in known:
            current_items.append(item)
            known.add(key(item))
    for item in current_items:
        identity = key(item)
        work_scope(item)
        old = candidates.get(identity, states.get(identity, {}))
        if old.get('scope') is not None and old['scope'] != item.get('scope'):
            raise ValueError('Do not remove or change the original work scope')
        candidates[identity] = item
    for result in data.get('results', []):
        if result.get('state') not in {'completed', 'cancelled', 'unknown', 'waiting', 'retry_read'} or not result.get('receipt_ref'):
            raise ValueError('Persisted step result needs actual evidence and an explicit state')
        work_key = result['key']
        if result['state'] == 'unknown' and not result.get('attempt_id'):
            raise ValueError('Unknown external effect needs the original AttemptId')
        if states.get(work_key, {}).get('state') in {'completed', 'cancelled'} and result['state'] != states[work_key]['state']:
            raise ValueError('Completed steps cannot be rewound by a later checkpoint')
        prior = states.get(work_key, {})
        if prior.get('state') == 'unknown' and (result.get('attempt_id') != prior.get('attempt_id')
                or result['state'] not in {'unknown', 'completed'}):
            raise ValueError('Reconcile only the original unknown attempt; do not clear or replace its reservation')
        states[work_key] = {k: result[k] for k in ('state', 'receipt_ref', 'attempt_id') if k in result}
        for name in ('scope', 'last_recovery_wakeup', 'last_recovery_due_at'):
            if name in prior:
                states[work_key][name] = copy.deepcopy(prior[name])
        if work_key in candidates:
            states[work_key].update({k: candidates[work_key][k] for k in ('source_key', 'step', 'version')})
            candidate = candidates[work_key]
            if candidate.get('scope') is not None:
                states[work_key]['scope'] = work_scope(candidate)
            if result['state'] == 'unknown':
                if candidate.get('recovery_wakeup') is not None:
                    states[work_key]['last_recovery_wakeup'] = copy.deepcopy(candidate['recovery_wakeup'])
                if candidate.get('recovery_due_at') and timestamp(candidate['recovery_due_at']) <= now:
                    states[work_key]['last_recovery_due_at'] = candidate['recovery_due_at']
    streams = dict(previous['streams'])
    for name, stream in data.get('streams', {}).items():
        if not isinstance(stream.get('complete'), bool) or not isinstance(stream.get('durable'), bool):
            raise ValueError('Coverage and durable source persistence must be explicit')
        if not stream['durable']:
            continue  # Never advance a watermark or cursor past unsaved input.
        if stream['complete'] and stream.get('next_cursor') is not None:
            raise ValueError('A paginated stream cannot be both exhausted and have a next page')
        timestamp(stream['cutoff'])
        old = streams.get(name)
        if old and timestamp(stream['cutoff']) < timestamp(old['cutoff']):
            raise ValueError('Source watermark cannot regress')
        streams[name] = {k: stream[k] for k in ('cutoff', 'complete', 'next_cursor') if k in stream}
    pending, seen = [], set()
    # Persist identities so a crash before the next query cannot forget ready
    # work. They are discovery pointers, never cached permission or payloads.
    completed = {(v['source_key'], v['step'], v['version']) for v in states.values()
                 if v.get('state') in {'completed', 'cancelled'} and all(k in v for k in ('source_key', 'step', 'version'))}
    unknown = {(v.get('source_key', candidates.get(k, {}).get('source_key')),
                v.get('step', candidates.get(k, {}).get('step')))
               for k, v in states.items() if v.get('state') == 'unknown'}
    def finished(item):
        return (item['source_key'], item['step'], item['version']) in completed
    barriers = []
    for identity, state in states.items():
        if state.get('state') == 'unknown' and identity not in candidates:
            barriers.append({**state, 'key': identity, 'unknown_attempt': True})
    for item in candidates.values():
        identity = key(item)
        if identity in seen:
            continue
        seen.add(identity)
        prior = states.get(identity, {})
        if prior.get('state') in {'completed', 'cancelled'} or finished(item):
            continue
        if (item['source_key'], item['step']) in unknown and prior.get('state') != 'unknown':
            continue
        # The persisted unknown overrides a newly constructed "ready" candidate.
        action = 'reconcile' if prior.get('state') == 'unknown' or item.get('unknown_attempt') else 'owner_step'
        if action == 'reconcile' or item['step'] in {'ObserveStop', 'RefreshContactRestrictions'}:
            barriers.append({**item, 'key': identity, 'unknown_attempt': action == 'reconcile'})
        if action == 'reconcile' and not recovery_ready(item, prior, now):
            continue
        if action == 'owner_step' and (item.get('stopped') is True or item.get('waiting') is True):
            continue
        if action == 'owner_step' and item.get('due_at') and timestamp(item['due_at']) > now:
            continue
        cost = item.get('estimated_seconds', 90)
        if type(cost) is not int or not 1 <= cost <= 600:
            raise ValueError('Use a bounded estimated duration from the owner phase')
        priority = (0 if item['step'] in {'ObserveStop', 'RefreshContactRestrictions'} else
                    0 if item['step'] == 'RecoverSourceHandoff' else
                    2 if item['step'] == 'SendNotificationSms' else
                    4 if item['step'] in {'RecordMaterialHandoff', 'RefreshEmailOutcome', 'RefreshSmsOutcome'} else
                    1 if item['step'] == 'ReadMessageBody' else item.get('priority', 3))
        pending.append({'key': identity, 'action': action,
                        **{k: item[k] for k in ('source_key', 'step', 'version', 'input_digest')},
                        'attempt_id': prior.get('attempt_id', item.get('attempt_id')),
                        **({'scope': work_scope(item)} if item.get('scope') is not None else {}),
                        'priority': priority, 'estimated_seconds': cost})
        if action == 'reconcile' and not pending[-1]['attempt_id']:
            raise ValueError('Unknown candidate must retain the original attempt')
    # Stop observations first, then unknown result reconciliation, accepted
    # submissions/due work, intake, and optional presentation/report maintenance.
    pending.sort(key=lambda x: (0 if x['step'] in {'ObserveStop', 'RefreshContactRestrictions'} else 1 if x['action'] == 'reconcile' else 2,
                                x['priority'], x['key']))
    expired = now >= start + timedelta(seconds=budget - reserve)
    attempted = set(data.get('attempted_keys', []))
    ready = [v for v in pending if v['key'] not in attempted]
    remaining = max(0, int((start + timedelta(seconds=budget-reserve) - now).total_seconds()))
    # Return only one admission. The caller must re-observe time/stop/activity
    # before choosing another step, rather than execute a stale whole-cycle list.
    # Estimates are not deadlines. Permit at most 15s of estimated work to use
    # the nominal publication reserve, retaining at least 30s. Never extend the
    # work-admission deadline, change a saved budget or release a provider call.
    slack = min(15, reserve - 30)
    fitting = []
    for candidate in ready:
        if (candidate['action'] != 'reconcile' and candidate['step'] not in {'ObserveStop', 'RefreshContactRestrictions'}
                and any(b['key'] != candidate['key'] and conflicts(b, candidate) for b in barriers)):
            continue
        if remaining >= 30 and candidate['estimated_seconds'] <= remaining + slack:
            fitting = [candidate]
            break
        # Unfitting barriers block their scope, not unrelated customer work.
    work = [] if expired or len(attempted) >= limit else fitting[:1]
    work_items = [{k: v[k] for k in ('source_key', 'step', 'version', 'input_digest', 'attempt_id', 'unknown_attempt',
                                   'due_at', 'waiting', 'stopped', 'priority', 'estimated_seconds', 'scope',
                                   'recovery_wakeup', 'recovery_due_at') if k in v}
                  for identity, v in candidates.items() if states.get(identity, {}).get('state') not in {'completed', 'cancelled'} and not finished(v)]
    checkpoint = {'record_type': 'scan-checkpoint-v1', 'root_id': root,
                  'invocation_id': current_id, 'items': states, 'streams': streams,
                  'work_items': work_items,
                  'remaining_keys': [v['key'] for v in pending], 'observed_at': data['now']}
    required_streams = data.get('required_streams', sorted(set(streams) | set(data.get('streams', {}))))
    fresh_streams = data.get('streams', {})
    complete = bool(required_streams) and all(
        fresh_streams.get(name, {}).get('complete') is True and fresh_streams.get(name, {}).get('durable') is True
        for name in required_streams)
    return {'status': 'ScanCyclePlanned', 'work': work, 'checkpoint': checkpoint,
            'elapsed_seconds': (now - start).total_seconds(), 'budget_seconds': budget,
            'publication_reserve_seconds': reserve,
            'timing_status': 'SoftBudgetOverrun' if (now - start).total_seconds() > budget else 'WithinSoftBudget',
            'soft_budget_overrun_seconds': max(0, (now - start).total_seconds() - budget),
            'execution_basis': 'TaskStateAndAttempts',
            'budget_exhausted': expired or len(attempted) >= limit,
            'admission_required_before_next_owner': True, 'seconds_available_for_work': remaining,
            'estimate_slack_seconds': slack,
            'estimated_reserve_use_seconds': max(0, work[0]['estimated_seconds'] - remaining) if work else 0,
            'deferred_for_estimate': bool(ready) and not fitting and not expired,
            'deadline': (start + timedelta(seconds=budget)).isoformat(),
            'coverage_complete': complete,
            'requires_next_cycle': bool(work_items) or not complete,
            'external_actions_allowed': False,
            'scope': 'Selection/checkpoint only; each owner still needs fresh authority, coverage, time and attempt checks'}
