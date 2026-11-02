#!/usr/bin/env python3
"""Bound a scan and prepare durable recovery state; no scheduler, lock or I/O."""

import hashlib
import json
from datetime import datetime, timedelta

from email_presentation import blocks
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


def bound_on_demand(data, root, current_id):
    """A designated conversation can be serial without claiming cloud readiness.

    All fields are observations normalized from current original settings,
    runtime thread/turn and the complete installation scan view. This is not
    a replacement for any native schedule guard or an atomic Notion lock.
    """
    if data.get('policy') not in {'one-cycle-approved-work', 'one-cycle-no-customer-send'}:
        return False
    binding = data['executor'].get('on_demand') or {}
    assigned = binding.get('registered_thread_id')
    return (binding.get('operator_assigned') is True and binding.get('settings_read_verified') is True
            and binding.get('runs_read_complete') is True and isinstance(assigned, str) and bool(assigned)
            and binding.get('current_thread_id') == assigned
            and binding.get('current_thread_status') == 'active'
            and binding.get('current_turn_id') == current_id
            and binding.get('current_turn_status') == 'inProgress'
            and page_id(binding.get('root_id', '')) == root
            and binding.get('scheduler_enabled') is False
            and binding.get('scheduler_state') == 'Stopped'
            and binding.get('schedule_ids') == []
            and 'schedule_pending_attempt' in binding and binding['schedule_pending_attempt'] is None
            and binding.get('other_active_scan_ids') == [])


def advance(data):
    root = page_id(data['root_id'])
    start, now = timestamp(data['started_at']), timestamp(data['now'])
    if now < start:
        raise ValueError('Clock regressed')
    budget, reserve, limit = data.get('budget_seconds', 900), data.get('reserve_seconds', 120), data.get('max_items', 12)
    if (type(budget) is not int or not 120 <= budget <= 900 or type(reserve) is not int
            or not 30 <= reserve < budget or type(limit) is not int or not 1 <= limit <= 100):
        raise ValueError('Use a 2-15 minute budget, publication reserve and bounded item count')
    executor = data['executor']
    current_id = executor['current_id']
    if not isinstance(current_id, str) or not current_id:
        raise ValueError('Use the current actual invocation identity')
    active = executor.get('active_ids')
    if not isinstance(active, list) or any(not isinstance(v, str) or not v for v in active):
        raise ValueError('Supply actual executor observations')
    native_single = executor.get('coverage_complete') is True and executor.get('serialized') is True
    scoped_single = bound_on_demand(data, root, current_id)
    single = (native_single or scoped_single) and not (set(active) - {current_id})
    if not single:
        return {'status': 'ScanDeferred', 'work': [], 'reason': 'Executor ownership not established',
                'external_actions_allowed': False, 'scope': 'Observation only; Notion is not an atomic lock'}
    previous = {'record_type': 'scan-checkpoint-v1', 'root_id': root, 'items': {}, 'streams': {}}
    if data.get('checkpoint_page') is not None:
        previous = blocks(data['checkpoint_page'], 'scan-checkpoint-v1')[1]
        if page_id(previous['root_id']) != root:
            raise ValueError('Checkpoint belongs to a different installation')
        # Do not confuse the recorded expired scan with proof of current ownership.
        object_result(data['checkpoint_page'])
    states = dict(previous['items'])
    candidates = {key(v): v for v in previous.get('work_items', [])}
    candidates.update({key(v): v for v in data['items']})
    for result in data.get('results', []):
        if result.get('state') not in {'completed', 'unknown', 'waiting', 'retry_read'} or not result.get('receipt_ref'):
            raise ValueError('Persisted step result needs actual evidence and an explicit state')
        work_key = result['key']
        if result['state'] == 'unknown' and not result.get('attempt_id'):
            raise ValueError('Unknown external effect needs the original AttemptId')
        if states.get(work_key, {}).get('state') == 'completed' and result['state'] != 'completed':
            raise ValueError('Completed steps cannot be rewound by a later checkpoint')
        states[work_key] = {k: result[k] for k in ('state', 'receipt_ref', 'attempt_id') if k in result}
        if work_key in candidates:
            states[work_key].update({k: candidates[work_key][k] for k in ('source_key', 'step', 'version')})
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
                 if v.get('state') == 'completed' and all(k in v for k in ('source_key', 'step', 'version'))}
    unknown = {(v.get('source_key', candidates.get(k, {}).get('source_key')),
                v.get('step', candidates.get(k, {}).get('step')))
               for k, v in states.items() if v.get('state') == 'unknown'}
    def finished(item):
        return (item['source_key'], item['step'], item['version']) in completed
    for item in candidates.values():
        identity = key(item)
        if identity in seen:
            continue
        seen.add(identity)
        prior = states.get(identity, {})
        if prior.get('state') == 'completed' or finished(item):
            continue
        if (item['source_key'], item['step']) in unknown and prior.get('state') != 'unknown':
            continue
        # The persisted unknown overrides a newly constructed "ready" candidate.
        action = 'reconcile' if prior.get('state') == 'unknown' or item.get('unknown_attempt') else 'owner_step'
        if action == 'owner_step' and (item.get('stopped') is True or item.get('waiting') is True):
            continue
        if action == 'owner_step' and item.get('due_at') and timestamp(item['due_at']) > now:
            continue
        cost = item.get('estimated_seconds', 90)
        if type(cost) is not int or not 1 <= cost <= 600:
            raise ValueError('Use a bounded estimated duration from the owner phase')
        priority = (0 if item['step'] in {'ObserveStop', 'RefreshContactRestrictions'} else
                    2 if item['step'] == 'SendNotificationSms' else
                    4 if item['step'] in {'RecordMaterialHandoff', 'RefreshEmailOutcome', 'RefreshSmsOutcome'} else
                    1 if item['step'] == 'ReadMessageBody' else item.get('priority', 3))
        pending.append({'key': identity, 'action': action,
                        **{k: item[k] for k in ('source_key', 'step', 'version', 'input_digest')},
                        'attempt_id': prior.get('attempt_id', item.get('attempt_id')),
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
    # before choosing another owner, rather than execute a stale whole-cycle list.
    # Estimates are not deadlines. Permit at most 15s of estimated work to use
    # the nominal publication reserve, retaining at least 30s. Never extend the
    # work-admission deadline, change a saved budget or release a provider call.
    slack = min(15, reserve - 30)
    fitting = []
    for candidate in ready:
        if remaining >= 30 and candidate['estimated_seconds'] <= remaining + slack:
            fitting = [candidate]
            break
        # A pending stop or unknown outcome cannot be skipped to send instead.
        if candidate['priority'] == 0 or candidate['action'] == 'reconcile':
            break
    work = [] if expired or len(attempted) >= limit else fitting[:1]
    work_items = [{k: v[k] for k in ('source_key', 'step', 'version', 'input_digest', 'attempt_id', 'unknown_attempt',
                                   'due_at', 'waiting', 'stopped', 'priority', 'estimated_seconds') if k in v}
                  for identity, v in candidates.items() if states.get(identity, {}).get('state') != 'completed' and not finished(v)]
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
            'execution_basis': 'BoundOnDemand' if scoped_single and not native_single else 'ObservedSerializedHost',
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
