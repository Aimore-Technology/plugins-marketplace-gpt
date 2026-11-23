"""Separate real timer/guard evidence from saved business progress and failures."""
import hashlib
import json
from scan_cycle import timestamp


def summarize(data):
    start, end = timestamp(data['started_at']), timestamp(data['ended_at'])
    if end < start:
        raise ValueError('Cycle clock regressed')
    discovery, guard = data['discovery'], data['guard']
    steps, blocks, waits = data.get('steps', []), data.get('blocks', []), data.get('waits', [])
    if any(s.get('state') not in {'completed', 'waiting', 'blocked', 'unknown'}
           or not s.get('receipt_ref') for s in steps):
        raise ValueError('Executed steps require actual persisted results, not plan success')
    if any(not b.get('code') or not b.get('reason') or not b.get('resume_step') or not b.get('evidence_ref') for b in blocks):
        raise ValueError('Each blocker requires exact evidence/reason and a recovery step')
    ready = discovery.get('ready_count', len(discovery.get('ready', [])))
    completed = [s for s in steps if s['state'] in {'completed', 'waiting'}]
    if ready and not completed and not blocks:
        raise ValueError('Ready backlog without progress needs a concrete blocker, never silent no-change')
    timer = data.get('timer_evidence') or {}
    trigger_verified = bool(timer.get('task_id') and timer.get('run_ref') and timer.get('observed_at'))
    passed = guard.get('status') in {'EligibleForScheduledCycle', 'ScanEnabled'}
    if not passed:
        state = 'GuardBlocked'
    elif blocks and not completed:
        state = 'Blocked'
    elif completed:
        state = 'Progressed'
    elif waits:
        state = 'WaitingForOperator'
    elif discovery.get('status') == 'ScanIdle' and discovery.get('coverage_complete') is True and not ready:
        state = 'ScanIdle'
    else:
        state = 'DiscoveryIncomplete'
    previous = data.get('previous_notice_keys', [])
    notices = []
    for block in blocks:
        key = hashlib.sha256(json.dumps([block.get('source_key'), block['code'],
                                        block['resume_step'], block.get('revision')], sort_keys=True).encode()).hexdigest()
        if key not in previous:
            notices.append({'key': key, 'block': block})
    return {'status': 'CycleMetricsPrepared', 'record': {
        'record_type': 'scan-cycle-metrics-v1', 'state': state,
        'timer_trigger_verified': trigger_verified, 'guard_passed': passed,
        'business_progress': bool(completed), 'events_discovered': data.get('events_discovered', 0),
        'backlog_count': discovery.get('pending_count', ready), 'ready_count': ready,
        'steps_executed': len(steps), 'steps_progressed': len(completed),
        'waiting_review_count': len(waits), 'blocks': blocks,
        'elapsed_seconds': (end-start).total_seconds(),
        'next_recovery': data.get('next_recovery', []),
        'rule_version': data['rule_version'], 'rule_sha256': data['rule_sha256'],
        'timer_evidence': timer or None}, 'notify': notices,
        'scope': 'Original observations only; timer trigger or guard pass is never business success'}
