"""Resume durable incoming work; source persistence is not a completed handoff."""
from email_presentation import properties
from intake_handoff import source_key
from notion_checks import object_result, page_id
from runtime_records import read_identity


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
        import re
        ancestors = re.findall(r'<(?:parent-page|ancestor-\d+-page)\b[^>]*url="([^"]+)"', source['text'].split('<content>', 1)[0])
        if root not in {page_id(v) for v in ancestors}:
            raise ValueError('Original source belongs to another installation')
        sources[identity] = (capture, source)
    existing_tasks = data['tasks']
    work, waiting, terminal = [], [], []
    for event in data['events']:
        if event.get('kind') != 'mail':
            continue
        identity = event['source_key']
        matched = [row for row in existing_tasks if read_identity(row.get('SourceKey')) == identity]
        active = [row for row in matched if row.get('State') not in {'Completed', 'Cancelled'}]
        source = sources.get(identity)
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
            'terminal_handoffs': terminal, 'ready_count': len(work),
            'scope': 'Pointers only; persist source-to-successor handoff before acknowledging original event; no approval or send'}
