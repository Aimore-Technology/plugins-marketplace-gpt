"""Construct the complete ready queue from saved events, not a chosen subset."""
import copy
import hashlib
import json
from pathlib import Path

import backlog_recovery
from email_presentation import blocks
from intake_handoff import source_key
from notion_checks import page_id
from scan_control import gate
from scan_cycle import key, timestamp

ROUTES = json.loads((Path(__file__).resolve().parents[1]/'references/task-routes.json').read_text())
SAFE_PREPARATION = {'read', 'draft', 'checkpoint', 'report'}
ESTIMATES = {'ResolveProjectSources': 180, 'ReviewReplyDraft': 60,
             'VerifyCustomer': 60, 'BuildDailyBrief': 90, 'ReadMessageBody': 30}


def ready_task_records(rows, issues=None):
    """Current validated preparation is backlog; never synthesize send approval."""
    records = []
    for row in rows:
        if row.get('Mode') != 'Automatic' or row.get('State') != 'ReadyToValidate':
            continue
        step = row.get('ResumeStep')
        route = ROUTES.get(step, {})
        if route.get('effect') not in SAFE_PREPARATION or route.get('owner') != row.get('OwnerSkill'):
            continue
        identity, version = backlog_recovery.task_source_key(row), row.get('ContentVersion')
        if not identity or not version or not row.get('url'):
            if issues is not None:
                issues.append({'source_key':identity or row.get('url'), 'code':'ReadyTaskMetadataMissing', 'reason':'Ready preparation lacks original source/step/version metadata', 'resume_step':step, 'evidence_ref':row.get('url') or 'current-task-discovery'})
            continue
        due = row.get('date:NextDue:start')
        digest = hashlib.sha256(json.dumps([page_id(row['url']), identity, step, version, due], separators=(',', ':')).encode()).hexdigest()
        event = {'kind': 'recovery', 'source_key': identity, 'step': step, 'version': version,
                 'input_digest': digest, 'evidence_ref': row['url'], 'task_id': row['url'],
                 'estimated_seconds': ESTIMATES.get(step, 90)}
        if due:
            timestamp(due)
            event.update(kind='timer', due_at=due)
        records.append({'id': 'ready-task:'+page_id(row['url']), 'revision': digest, 'events': [event]})
    return records


def build(data):
    entry = gate(data)
    if entry['status'] != 'ScanEnabled':
        return entry
    root, now = page_id(data['root_id']), timestamp(data['now'])
    index = blocks(data['index_page'], 'scan-event-index-v1')[1]
    if page_id(index['root_id']) != root:
        raise ValueError('Use this installation\'s original saved event index')
    events = [dict(v, key=k) for k, v in index['pending'].items()
              if not v.get('due_at') or timestamp(v['due_at']) <= now]
    tasks = data.get('tasks', [])
    items = {key(v): copy.deepcopy(v) for v in data.get('items', [])}
    waiting, blocked, terminal, coverage = [], [], [], []
    for event in events:
        if event['kind'] != 'mail':
            continue
        try:
            selected = [p for p in data.get('source_pages', []) if source_key(p) == event['source_key']]
            result = backlog_recovery.plan({'root_id': root, 'events': [event],
                'sources_complete': data.get('sources_complete') is True,
                'tasks_complete': data.get('tasks_complete') is True,
                'source_pages': selected, 'tasks': tasks})
            for item in result['work']:
                item.setdefault('kind', 'recovery' if item['step'] == 'RecoverSourceHandoff' else 'mail')
                item.setdefault('evidence_ref', event['evidence_ref'])
                item.setdefault('estimated_seconds', ESTIMATES.get(item['step'], 90))
                items.setdefault(key(item), item)
            waiting.extend(result['waiting']); terminal.extend(result['terminal_handoffs'])
            blocked.extend(result.get('blocks', []))
            disposition = ('ready' if result['work'] else 'waiting' if result['waiting'] else
                           'terminal-readback' if result['terminal_handoffs'] else 'blocked')
            coverage.append({'event_key': event['key'], 'disposition': disposition})
        except (ValueError, KeyError, TypeError) as exc:
            blocked.append({'source_key': event['source_key'], 'code': 'MailRecoveryInputIncomplete',
                'reason': str(exc), 'resume_step': event['step'], 'evidence_ref': event['evidence_ref']})
            coverage.append({'event_key': event['key'], 'disposition': 'blocked'})
    for event in events:
        if event['kind'] == 'mail':
            continue
        matches = [r for r in tasks if backlog_recovery.task_source_key(r) == event['source_key']
                   and r.get('ResumeStep') == event['step'] and r.get('ContentVersion') == event['version']]
        if matches and all(r.get('State') in {'Completed', 'Cancelled'} for r in matches):
            terminal.append({'source_key': event['source_key'], 'event_key': event['key'],
                'action': 'ReadOriginalHandoffResult', 'task_ids': [r['url'] for r in matches]})
            coverage.append({'event_key': event['key'], 'disposition': 'terminal-readback'})
            continue
        item = {k: copy.deepcopy(v) for k, v in event.items() if k != 'key'}
        item.setdefault('estimated_seconds', ESTIMATES.get(item['step'], 90))
        items.setdefault(key(item), item)
        coverage.append({'event_key': event['key'], 'disposition': 'ready'})
    if data.get('tasks_complete') is True:
        for record in ready_task_records(tasks, blocked):
            item = record['events'][0]
            if item.get('due_at') and timestamp(item['due_at']) > now:
                continue
            phase = (item['source_key'], item['step'], item['version'])
            if not any((v['source_key'], v['step'], v['version']) == phase for v in items.values()):
                items[key(item)] = item
    return {'status': 'ReadyQueueConstructed', 'root_id': root, 'items': list(items.values()),
            'ready_event_count': len(events), 'accounted_event_count': len(coverage),
            'event_coverage': coverage, 'waiting': waiting, 'blocks': blocked,
            'terminal_readbacks': terminal, 'external_actions_allowed': False,
            'scope': 'Complete queue construction only; original task/approval/stop/attempt checks still apply'}
