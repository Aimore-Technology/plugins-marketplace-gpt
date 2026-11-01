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
    budget, reserve, limit = data.get('budget_seconds', 480), data.get('reserve_seconds', 60), data.get('max_items', 12)
    if (type(budget) is not int or not 120 <= budget <= 600 or type(reserve) is not int
            or not 30 <= reserve < budget or type(limit) is not int or not 1 <= limit <= 100):
        raise ValueError('Use a 2-10 minute budget, publication reserve and bounded item count')
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
    for result in data.get('results', []):
        if result.get('state') not in {'completed', 'unknown', 'waiting', 'retry_read'} or not result.get('receipt_ref'):
            raise ValueError('Persisted step result needs actual evidence and an explicit state')
        work_key = result['key']
        if result['state'] == 'unknown' and not result.get('attempt_id'):
            raise ValueError('Unknown external effect needs the original AttemptId')
        if states.get(work_key, {}).get('state') == 'completed' and result['state'] != 'completed':
            raise ValueError('Completed steps cannot be rewound by a later checkpoint')
        states[work_key] = {k: result[k] for k in ('state', 'receipt_ref', 'attempt_id') if k in result}
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
    candidates = {key(v): v for v in previous.get('work_items', [])}
    candidates.update({key(v): v for v in data['items']})
    for item in candidates.values():
        identity = key(item)
        if identity in seen:
            continue
        seen.add(identity)
        prior = states.get(identity, {})
        if prior.get('state') == 'completed':
            continue
        # The persisted unknown overrides a newly constructed "ready" candidate.
        action = 'reconcile' if prior.get('state') == 'unknown' or item.get('unknown_attempt') else 'owner_step'
        if action == 'owner_step' and (item.get('stopped') is True or item.get('waiting') is True):
            continue
        if action == 'owner_step' and item.get('due_at') and timestamp(item['due_at']) > now:
            continue
        pending.append({'key': identity, 'action': action,
                        **{k: item[k] for k in ('source_key', 'step', 'version', 'input_digest')},
                        'attempt_id': prior.get('attempt_id', item.get('attempt_id')),
                        'priority': item.get('priority', 3)})
        if action == 'reconcile' and not pending[-1]['attempt_id']:
            raise ValueError('Unknown candidate must retain the original attempt')
    # Stop observations first, then unknown result reconciliation, accepted
    # submissions/due work, intake, and optional presentation/report maintenance.
    pending.sort(key=lambda x: (0 if x['step'] == 'ObserveStop' else 1 if x['action'] == 'reconcile' else x['priority'], x['key']))
    expired = now >= start + timedelta(seconds=budget - reserve)
    attempted = set(data.get('attempted_keys', []))
    ready = [v for v in pending if v['key'] not in attempted]
    work = [] if expired else ready[:max(0, limit - len(attempted))]
    work_items = [{k: v[k] for k in ('source_key', 'step', 'version', 'input_digest', 'attempt_id', 'unknown_attempt',
                                   'due_at', 'waiting', 'stopped', 'priority') if k in v}
                  for identity, v in candidates.items() if states.get(identity, {}).get('state') != 'completed']
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
            'execution_basis': 'BoundOnDemand' if scoped_single and not native_single else 'ObservedSerializedHost',
            'budget_exhausted': expired or len(attempted) >= limit,
            'deadline': (start + timedelta(seconds=budget)).isoformat(),
            'coverage_complete': complete,
            'requires_next_cycle': bool(work_items) or not complete,
            'external_actions_allowed': False,
            'scope': 'Selection/checkpoint only; each owner still needs fresh authority, coverage, time and attempt checks'}
