"""Select active input/dependency watches from original settings and task rows."""

from email_presentation import blocks
from notion_checks import page_id

HUMAN = {'ClientMatching', 'DataCompletion', 'ContentReview', 'SendApproval', 'ExecutionExceptions'}
FACT_STEPS = {'ResolveProjectSources', 'ReviewReplyDraft', 'SendApprovedReply'}


def plan(data):
    settings = blocks(data['settings_page'], 'run-settings', required=False)
    # RunSettings has historically used settings_schema_version rather than a tag.
    if settings:
        config = settings[1]
    else:
        import json, re
        from notion_checks import page_body
        found = [json.loads(x) for x in re.findall(r'```json\s*\n(.*?)\n```', page_body(data['settings_page']), re.S)]
        found = [x for x in found if isinstance(x, dict) and 'settings_schema_version' in x]
        if len(found) != 1:
            raise ValueError('Use the original unambiguous RunSettings page')
        config = found[0]
    from scan_control import gate
    entry = gate({'settings': config})
    if entry['status'] != 'ScanEnabled':
        return entry
    if data.get('tasks_complete') is not True:
        raise ValueError('Complete current task discovery is required before omitting watches')
    rows = data['tasks']
    if not isinstance(rows, list):
        raise ValueError('Use the actual complete task rows')
    for row in rows:
        if not row.get('url') or row.get('State') not in {
                'WaitingForOperator', 'NeedsCorrection', 'ReadyToValidate', 'InProgress', 'Completed', 'Cancelled'}:
            raise ValueError('Incomplete task identity/state cannot prove an inactive dependency')
    active = [r for r in rows if r.get('State') not in {'Completed', 'Cancelled'}]
    actions = []
    for row in active:
        if row.get('Category') in HUMAN:
            target = row.get('ActionPageURL')
            if not target:
                raise ValueError('An active human task lacks its original action route; do not claim action coverage')
            actions.append(target)
    fact_rows = [r for r in active if r.get('ResumeStep', r.get('StepId')) in FACT_STEPS
                 or r.get('OwnerSkill') == 'eightdegrees-sales-reply'
                 and r.get('ResumeStep', r.get('StepId')) not in {'RecordSendReceipt', 'RecordMaterialHandoff', 'RefreshEmailOutcome'}]
    fact_ids = {page_id(r['url']) for r in fact_rows}
    replies = list(config.get('sales_replies', {}).values())
    ids = lambda reply: {page_id(reply[k]) for k in ('content_task_page_id', 'send_task_page_id') if reply.get(k)}
    mapped = set().union(*(ids(r) for r in replies)) if replies else set()
    pending_sources = True  # Without the original index, omit no registered source.
    if data.get('index_page') is not None:
        index = blocks(data['index_page'], 'scan-event-index-v1')[1]
        root = config.get('customer_setup', {}).get('notion_root_id')
        if root and page_id(root) != page_id(index['root_id']):
            raise ValueError('Source event index belongs to another installation')
        pending_sources = any(event.get('kind') == 'source' for event in index['pending'].values())
    conservative = bool(fact_ids - mapped) or pending_sources
    contexts = {r.get('context_key') for r in replies if ids(r) & fact_ids}
    watches, excluded = {}, []
    for project in config.get('project_sources', {}).values():
        context = project.get('context_key')
        if not conservative and context and context not in contexts:
            excluded.append({'context_key': context, 'reason': 'No active source-dependent email step'})
            continue
        sources = [project.get('index', {})] + list(project.get('files', {}).values())
        for source in sources:
            if source.get('status') in {'Superseded', 'Archived'}:
                continue
            identity = source.get('file_id')
            if not identity:
                raise ValueError('An active registered dependency lacks its original file ID')
            watch = {k: source[k] for k in ('file_id', 'path', 'rev', 'version') if k in source}
            if identity in watches and watches[identity] != watch:
                raise ValueError('A dependency has conflicting registered revisions or paths')
            watches[identity] = watch
    from queue_construction import ready_task_records
    ready_issues = []
    ready_records = ready_task_records(rows, ready_issues)
    return {'status': 'DiscoveryWatchesPrepared', 'action_page_urls': sorted(set(actions)),
            'ready_task_records': ready_records, 'ready_task_blocks': ready_issues,
            'source_metadata': list(watches.values()), 'excluded_projects': excluded,
            'conservative_source_watch': conservative,
            'mail_scope_unchanged': True, 'external_actions_allowed': False,
            'scope': 'Active discovery reads only; new/changed inputs and dispatch still require fresh actual dependencies and guards'}
