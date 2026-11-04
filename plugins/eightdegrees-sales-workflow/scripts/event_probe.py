#!/usr/bin/env python3
"""Select changed/due input before business work; offline, never a send permit."""

import copy
import hashlib
import json

from email_presentation import blocks
from notion_checks import object_result, page_id
from scan_cycle import key, timestamp

CONTRACT = 'scan-event-index-v1'
KINDS = {'mail', 'stop', 'submission', 'control', 'source', 'timer', 'recovery'}
REQUIRED = {'mail', 'actions', 'control', 'scheduled', 'recovery'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def event(value):
    if value['kind'] not in KINDS or not isinstance(value.get('evidence_ref'), str) or not value['evidence_ref']:
        raise ValueError('Each event needs a supported kind and original source/evidence pointer')
    identity = key(value)
    if value.get('due_at') is not None:
        timestamp(value['due_at'])
    if value['kind'] == 'timer' and not value.get('due_at'):
        raise ValueError('A clock event needs its actual due time')
    return identity, copy.deepcopy(value)


def probe(data):
    """Normalize real lightweight observations, not model guesses about changes.

    New observations and events are committed together only after the caller
    persists candidate_index and confirms its API acknowledgement. Merely observing a source never handles
    its event. The index contains identities/digests, not cached permissions.
    """
    from scan_control import gate
    entry = gate(data)
    if entry['status'] != 'ScanEnabled':
        return entry

    root, now = page_id(data['root_id']), timestamp(data['now'])
    scope = data['scope_sha256']
    if not isinstance(scope, str) or len(scope) != 64 or any(c not in '0123456789abcdef' for c in scope):
        raise ValueError('Bind discovery to the canonical saved configuration digest')
    required = data['required_feeds']
    if (not isinstance(required, list) or len(required) != len(set(required))
            or not REQUIRED.issubset(required) or any(not isinstance(n, str) or not n for n in required)):
        raise ValueError('Declare mail, actions, control, scheduled and recovery plus configured dependency feeds')
    original = {'record_type': CONTRACT, 'root_id': root, 'scope_sha256': scope,
                'feeds': {}, 'pending': {}, 'handled': {}}
    if data.get('index_page') is not None:
        saved = object_result(data['index_page'])
        if saved.get('metadata', {}).get('type') != 'page' or not page_id(saved.get('id', '')):
            raise ValueError('Use the original registered event-index page fetch')
        original = blocks(data['index_page'], CONTRACT)[1]
        if page_id(original['root_id']) != root:
            raise ValueError('Event index belongs to another installation')
    scope_changed = original['scope_sha256'] != scope
    index = copy.deepcopy(original)
    # Retain pending work even when a configuration digest changes. Rebaseline
    # the changed feeds from real snapshots; never erase a durable backlog or
    # pretend old cursors establish new-scope coverage.
    index['scope_sha256'] = scope
    if scope_changed:
        for feed in index['feeds'].values():
            feed.setdefault('scope_sha256', original['scope_sha256'])
    pending, handled = index['pending'], index['handled']
    # Acknowledgements come from saved owner results, never from probe success.
    for ack in data.get('acknowledgements', []):
        identity = ack['key']
        if identity not in pending or ack.get('state') not in {'completed', 'waiting'} or not ack.get('receipt_ref'):
            raise ValueError('Acknowledge only a pending event using its durable owner result')
        if ack['state'] == 'waiting' and not ack.get('wake_ref'):
            raise ValueError('A waiting result must retain its registered action/timer/recovery wake-up pointer')
        handled[identity] = {'source_key': pending[identity]['source_key'], 'step': pending[identity]['step'],
                             'version': pending[identity]['version'], 'receipt_ref': ack['receipt_ref'],
                             'state': ack['state'], **({'wake_ref': ack['wake_ref']} if 'wake_ref' in ack else {})}
        del pending[identity]
    # Current validated preparation remains recovery demand without row edits.
    # Supplemental task records do not certify missing feed coverage.
    for record in data.get('ready_task_records', []):
        for raw_event in record['events']:
            if raw_event.get('kind') not in {'recovery', 'timer'}:
                raise ValueError('Ready task supplementation is recovery/timing, never synthetic approval')
            identity, value = event(raw_event)
            # A producer may already have registered the same ready phase with
            # its richer original input digest. Do not create a second trigger.
            if any((v['source_key'], v['step'], v['version']) ==
                   (value['source_key'], value['step'], value['version']) for v in pending.values()):
                continue
            if identity not in handled:
                if identity in pending and pending[identity] != value:
                    raise ValueError('Preserve the original ready task event')
                pending[identity] = value
    observations = data['observations']
    if set(observations) - set(required):
        raise ValueError('Undeclared observation feed')
    missing, recovery = [], []
    for name in required:
        observation = observations.get(name)
        if observation is None:
            missing.append(name)
            recovery.append({'feed': name, 'reason': 'No current observation',
                             'action': 'Read the registered feed within its authorized scope', 'scope': name})
            continue
        observed = timestamp(observation['observed_at'])
        if observed > now or (now - observed).total_seconds() > 900:
            raise ValueError('Use fresh actual discovery observations, not a cached empty response')
        if type(observation.get('complete')) is not bool or observation.get('mode') not in {'snapshot', 'delta'}:
            raise ValueError('Discovery coverage and snapshot/delta mode must be explicit')
        failure = observation.get('failure')
        if failure is not None:
            from connector_capture import normalize
            actual = normalize({'response': failure['original'], 'capture_ref': failure['capture_ref'],
                                'observed_at': failure['observed_at']})
            if actual != failure or not actual['failed'] or observation['complete']:
                raise ValueError('Preserve the exact failed capture; failure cannot establish complete coverage')
        old = index['feeds'].get(name, {'cursor': None, 'revisions': {}})
        feed_scope_changed = old.get('scope_sha256', original['scope_sha256']) != scope
        if feed_scope_changed and observation['mode'] != 'snapshot':
            missing.append(name)
            recovery.append({'feed': name, 'reason': 'Authorized scope digest changed',
                             'action': 'Take a complete scoped snapshot; preserve original pending work/cursors', 'scope': name})
            continue
        if observation['mode'] == 'delta' and (name not in index['feeds'] or 'from_cursor' not in observation
                                              or observation['from_cursor'] != old['cursor']):
            missing.append(name)
            recovery.append({'feed': name, 'reason': 'Delta cursor missing or expired',
                             'action': 'Read a bounded scoped snapshot, then commit its actual cursor', 'scope': name})
            continue  # Lost/expired cursor needs this feed's bounded recovery.
        if observation.get('page_cursor') != old.get('resume_cursor'):
            missing.append(name)
            recovery.append({'feed': name, 'reason': 'Incomplete saved pagination',
                             'action': 'Continue the actual saved resume cursor', 'scope': name})
            continue  # Continue saved pagination rather than silently skipping a page.
        if not observation['complete']:
            missing.append(name)
            recovery.append({'feed': name, 'reason': 'Connector failed' if failure else 'Pagination incomplete',
                             'action': 'Retry only this failed feed' if failure else 'Continue the returned page cursor',
                             'scope': name,
                             **({'evidence_ref': failure['capture_ref']} if failure else {})})
        records = observation['records']
        ids = [r['id'] for r in records]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Discovery records need unique original identities')
        revisions = dict(old['revisions'])
        snapshot_ids = set(old.get('snapshot_ids', [])) if observation['mode'] == 'snapshot' else set()
        snapshot_ids.update(ids)
        for record in records:
            revision = record['revision']
            if not isinstance(revision, str) or not revision or not isinstance(record['events'], list):
                raise ValueError('Use actual stable input revisions and explicit event lists')
            checked = [event(v) for v in record['events']]
            if revisions.get(record['id']) == revision:
                continue
            for identity, value in checked:
                if identity not in handled:
                    if identity in pending and pending[identity] != value:
                        raise ValueError('An existing event cannot silently change payload, due time or evidence')
                    pending[identity] = value
            revisions[record['id']] = revision
        if observation['mode'] == 'snapshot' and observation['complete']:
            revisions = {i: revisions[i] for i in snapshot_ids}
        # Never advance a pagination cursor across incomplete observations.
        index['feeds'][name] = {'cursor': observation.get('next_cursor') if observation['complete'] else old['cursor'],
                                'revisions': revisions,
                                'scope_sha256': scope if observation['complete'] else old.get('scope_sha256', original['scope_sha256'])}
        if failure:
            index['feeds'][name]['last_failure'] = {k: failure[k] for k in
                ('capture_ref', 'capture_sha256', 'observed_at', 'inspection')}
        elif old.get('last_failure'):
            index['feeds'][name]['last_failure'] = copy.deepcopy(old['last_failure'])
            if observation['complete']:
                index['feeds'][name]['last_failure'].setdefault('recovered_at', observation['observed_at'])
        if not observation['complete']:
            index['feeds'][name]['resume_cursor'] = observation.get('next_cursor', old.get('resume_cursor'))
            if observation['mode'] == 'snapshot':
                index['feeds'][name]['snapshot_ids'] = sorted(snapshot_ids)
    for issue in data.get('ready_task_blocks', []):
        missing.append('recovery')
        recovery.append({'feed':'recovery','scope':issue.get('source_key'),'reason':issue['reason'],
                         'action':'Repair only the original task metadata; retain independent ready work',
                         'evidence_ref':issue['evidence_ref']})
    ready = [dict(value, key=identity) for identity, value in pending.items()
             if not value.get('due_at') or timestamp(value['due_at']) <= now]
    ready.sort(key=lambda v: (0 if v['kind'] in {'stop', 'control'} else 1, v['key']))
    future = [v['due_at'] for v in pending.values() if v.get('due_at') and timestamp(v['due_at']) > now]
    # NeedsBaseline is an observation projection, never a permanent execution
    # lock. Ready backlog may enter source/draft work while unrelated coverage
    # recovers; affected sends still require their fresh source/stop coverage.
    if index.get('baseline') != {'state': 'NeedsBaseline' if missing else 'Complete',
                                 'required_feeds': sorted(required), 'missing_feeds': sorted(set(missing))}:
        index['baseline'] = {'state': 'NeedsBaseline' if missing else 'Complete',
                             'required_feeds': sorted(required), 'missing_feeds': sorted(set(missing))}
    return {'status': 'ScanWorkReady' if ready else 'ScanDiscoveryRequired' if missing else 'ScanIdle',
            'coverage_complete': not missing, 'missing_feeds': missing, 'ready': ready,
            'baseline_state': index['baseline']['state'], 'recovery_actions': recovery,
            'scope_revalidation_required': scope_changed, 'ready_count': len(ready),
            'pending_count': len(pending), 'next_due_at': min(future, key=timestamp) if future else None,
            'candidate_index': index, 'index_sha256': digest(index),
            'persist_required': index != original, 'external_actions_allowed': False,
            'scope': 'Discovery only; persist changed index before cursors using its API acknowledgement, then admit affected owner work with fresh guards'}
