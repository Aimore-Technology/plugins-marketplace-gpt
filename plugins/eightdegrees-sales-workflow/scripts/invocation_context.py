"""Pin a public plugin invocation across compaction; never control another task."""

from datetime import datetime, timedelta
import json
from pathlib import Path

from email_presentation import blocks
from notion_checks import page_id

COMMANDS = json.loads((Path(__file__).resolve().parents[1] / 'references/commands.json').read_text())


def timestamp(value):
    at = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if at.tzinfo is None:
        raise ValueError('Use timezone-aware actual invocation times')
    return at


def prepare(data):
    command = data['command']
    if command not in COMMANDS:
        raise ValueError('Pin one exact supported public command')
    for key in ('invocation_id', 'executor_id'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError('Use actual current invocation/executor identities')
    seconds = data.get('budget_seconds', 900)
    if type(seconds) is not int or not 120 <= seconds <= 900:
        raise ValueError('Keep the original bounded invocation budget')
    start = timestamp(data['started_at'])
    record = {'record_type': 'invocation-context-v1', 'role': 'plugin-executor',
              'command': command, 'policy': COMMANDS[command]['policy'],
              'root_id': page_id(data['root_id']), 'invocation_id': data['invocation_id'],
              'executor_id': data['executor_id'], 'started_at': data['started_at'],
              'deadline': (start + timedelta(seconds=seconds)).isoformat(),
              'budget_seconds': seconds,
              'receipt_page_ids': [page_id(x) for x in data.get('receipt_page_ids', [])]}
    return {'status': 'InvocationContextPrepared', 'record': record,
            'scope': 'Recovery identity and receipt pointers only; no cached permission or provider state'}


def resume(data):
    if ('context_page' in data) == ('context_record' in data):
        raise ValueError('Use one original saved page or local invocation record')
    record = blocks(data['context_page'], 'invocation-context-v1')[1] if 'context_page' in data else data['context_record']
    expected = prepare(record)['record']
    if record != expected:
        raise ValueError('Saved invocation context differs from its frozen command/budget')
    for key in ('command', 'invocation_id', 'executor_id'):
        if record[key] != data[key]:
            raise ValueError('Resume this invocation only; do not restart or control a peer Session')
    if page_id(data['root_id']) != record['root_id']:
        raise ValueError('Invocation root changed')
    if timestamp(data['started_at']) != timestamp(record['started_at']):
        raise ValueError('Use the actual original invocation start; never reset the budget')
    now = timestamp(data['now'])
    if now < timestamp(record['started_at']):
        raise ValueError('Invocation clock regressed')
    expired = now >= timestamp(record['deadline'])
    return {'status': 'InvocationResumeChecked', 'role': record['role'],
            'command': record['command'], 'policy': record['policy'],
            'remaining_seconds': max(0, (timestamp(record['deadline']) - now).total_seconds()),
            'closeout_only': expired, 'receipt_pages_to_read': record['receipt_page_ids'],
            'peer_session_control_allowed': False, 'external_actions_allowed': False,
            'scope': 'Resume current execution only; read original receipts and fresh guards, never resend to repair publication'}
