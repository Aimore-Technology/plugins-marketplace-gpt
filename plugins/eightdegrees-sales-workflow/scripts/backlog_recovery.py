"""Resume durable incoming work; source persistence is not a completed handoff."""
from email_presentation import properties
from intake_handoff import source_key
from notion_checks import object_result, page_id
from runtime_records import read_identity
import re
from urllib.parse import unquote


def task_source_key(row):
    """Decode only Notion's exact leading-email rendering, never arbitrary links."""
    value = read_identity(row.get('SourceKey'))
    if not isinstance(value, str):
        return value
    linked = re.fullmatch(r'\[([^\[\]]+)\]\(mailto:([^()]+)\):(inbound|outbound):([^\s<>\\`():]+)', value)
    if linked and linked[1] == unquote(linked[2]):
        return linked[1] + ':' + linked[3] + ':' + linked[4]
    return value


def plan(data):
    root = page_id(data['root_id'])
    if data.get('sources_complete') is not True or data.get('tasks_complete') is not True:
        raise ValueError('Read complete current source/task discovery before claiming absence')
    sources = {}
    for capture in data['source_pages']:
        source = object_result(capture)
        identity = source_key(capture)
        if identity in sources:
            raise ValueError('Duplicate original source identity; reconcile without creating another')
        # Source pages must retain the actual current installation ancestor.
        ancestors = re.findall(r'<(?:parent-page|ancestor-\d+-page)\b[^>]*url="([^"]+)"', source['text'].split('<content>', 1)[0])
        if root not in {page_id(v) for v in ancestors}:
            raise ValueError('Original source belongs to another installation')
        sources[identity] = (capture, source)
    existing_tasks = data['tasks']
    work, waiting, terminal, blockers = [], [], [], []
    for event in data['events']:
        if event.get('kind') != 'mail':
            continue
        identity = event['source_key']
        matched = [row for row in existing_tasks if task_source_key(row) == identity]
        source = sources.get(identity)
        if source:
            source_id = page_id(source[1]['id'])
            def original_source_id(row):
                try:
                    return page_id(row.get('SourceURL', ''))
                except (ValueError, TypeError):
                    return None
            inconsistent = [row for row in existing_tasks
                            if original_source_id(row) == source_id and task_source_key(row) != identity
                            or row in matched and original_source_id(row) not in {None, source_id}]
            if inconsistent:
                blockers.extend({'source_key': identity, 'code': 'TaskSourceIdentityConflict',
                    'reason': 'Original task source key and saved source pointer disagree; retain both originals',
                    'resume_step': row.get('ResumeStep') or 'VerifyCustomer',
                    'evidence_ref': row.get('url', row.get('PageId')),
                    'recovery': 'Repair the original task identity from its original source; do not create another task'}
                    for row in inconsistent)
                continue
        active = [row for row in matched if row.get('State') not in {'Completed', 'Cancelled'}]
        if active:
            for row in active:
                pointer = {'source_key': identity, 'task_id': row.get('url', row.get('PageId')),
                           'step': row['ResumeStep'], 'version': row['ContentVersion'],
                           'input_digest': event['input_digest']}
                if row.get('State') == 'WaitingForOperator' and not row.get('AcceptedSubmission'):
                    waiting.append(pointer)
                else:
                    work.append(pointer | {'action': 'ResumeOriginalTask'})
            continue
        if matched:
            terminal.append({'source_key': identity, 'action': 'ReadOriginalHandoffResult',
                             'task_ids': [r.get('url', r.get('PageId')) for r in matched]})
            continue
        if source:
            capture, original = source
            work.append({'source_key': identity, 'source_page_id': page_id(original['id']),
                         'source_version': properties(capture).get('ContentVersion'),
                         'version': properties(capture).get('ContentVersion') or event['version'],
                         'input_digest': event['input_digest'],
                         'step': 'RecoverSourceHandoff', 'action': 'ReuseSavedSource',
                         'owner': 'eightdegrees-email-scanning', 'create_source': False})
        else:
            work.append({'source_key': identity, 'step': 'ReadMessageBody',
                         'version': event['version'], 'input_digest': event['input_digest'],
                         'action': 'ReadAuthorizedMessageThenSaveSource', 'create_source': True})
    return {'status': 'BacklogRecoveryPlanned', 'work': work, 'waiting': waiting,
            'terminal_handoffs': terminal, 'blocks': blockers, 'ready_count': len(work),
            'scope': 'Pointers only; persist source-to-successor handoff before acknowledging original event; no approval or send'}
