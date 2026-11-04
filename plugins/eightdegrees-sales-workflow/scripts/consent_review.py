"""One canonical row, readable narrative and one native Consent checkbox."""

from email_presentation import blocks, properties
from notion_checks import object_result, page_body, page_id

CONTRACT = 'email-review-v4'


def needs_publication(row):
    """Select incomplete native review projections, never infer consent."""
    return (row.get('Mode') == 'Automatic' and row.get('State') not in {'Completed', 'Cancelled'}
            and row.get('OwnerSkill') == 'eightdegrees-sales-reply'
            and row.get('ResumeStep') == 'SendApprovedReply'
            and {'ActionFormVersion', 'ReviewText', 'ActionPageURL', 'Category'} <= row.keys()
            and row.get('ActionFormVersion') in {None, '', CONTRACT}
            and (row.get('ActionFormVersion') != CONTRACT or row.get('Category') != 'SendApproval'
                 or not row.get('ReviewText') or not row.get('ActionPageURL')))


def narrative(package, historical=False):
    from email_flow import validate, window_text, LABELS
    m, text = validate(package)
    labels = package['labels']
    lines = ['From: '+m['from_address'], 'To: '+m['to']]
    lines += [key+': '+m[key.lower()] for key in ('Cc', 'Bcc') if m.get(key.lower())]
    lines += [labels['subject']+': '+m['subject'], '', text.decode('utf-8').rstrip('\n'), '']
    if historical and package.get('window'):
        lines += ['Window: '+window_text(package['window']), labels['consent_help']]
    else:
        language = 'zh-CN' if labels['subject'] == LABELS['zh-CN']['subject'] else 'en'
        lines.append(LABELS[language]['consent_help'])
    return '\n'.join(lines)


def render(package):
    from email_flow import validate
    validate(package)
    if page_id(package['task_page_id']) != page_id(package['action_page_id']):
        raise ValueError('One-click review lives on its canonical task, without a separate action page')
    binding = {'record_type': 'action-binding', 'ApprovalContract': CONTRACT,
               'TaskPageId': package['task_page_id'], 'ActionPageId': package['task_page_id'],
               'OwnerSkill': 'eightdegrees-sales-reply', 'ResumeStep': 'SendApprovedReply',
               'StepId': 'SendApprovedReply', 'Category': 'SendApproval', 'Mode': 'Automatic',
               'ContentVersion': package['content_version'], 'OperatorId': package['operator_id'],
               'PackageSha256': package['package_sha256'],
               'DraftBindingSha256': package['draft_verification']['draft_binding_sha256'],
               'ConsentProperty': 'Consent', 'ReviewProperty': 'ReviewText', 'ResumeContractVersion': 'resume-v1'}
    return {'status': 'SingleEmailReviewRendered', 'binding': binding,
            'task_records': [binding, package], 'properties': {
                'ReviewText': narrative(package), 'Consent': '__NO__',
                'State': 'WaitingForOperator', 'InputSubmitted': '__NO__',
                'Result': package['labels']['consent_help'],
                'ActionFormVersion': CONTRACT, 'ContentVersion': package['content_version'],
                'Mode': 'Automatic', 'Category': 'SendApproval',
                'OwnerSkill': 'eightdegrees-sales-reply', 'ResumeStep': 'SendApprovedReply',
                'OperatorId': package['operator_id'], 'SourceKey': package['source_key'],
                'SourceURL': 'https://app.notion.com/p/'+page_id(package['source_page_id']),
                'StepId': 'SendApprovedReply',
                'ResumeContractVersion': 'resume-v1',
                'date:NextDue:start': None, 'date:SendNotBefore:start': None,
                'date:SendNotAfter:start': None,
                'ActionPageURL': 'https://app.notion.com/p/'+page_id(package['task_page_id'])},
            'scope': 'Publish on the canonical task; show ReviewText and Consent in one native view; no separate form or Submit'}


def repair_publication(data):
    """Finish a saved v4 review's missing native properties, without approval."""
    task = data['task']
    props = properties(task)
    if props.get('State') in {'Completed', 'Cancelled'}:
        return {'status': 'EmailReviewPublicationUnchanged', 'writes': [], 'send_allowed': False}
    package = blocks(task, CONTRACT)[1]
    rendered = render(package)
    identity = page_id(object_result(task)['id'])
    if (identity != page_id(package['task_page_id']) or blocks(task, 'action-binding')[1] != rendered['binding']
            or props.get('ContentVersion') != package['content_version']):
        raise ValueError('Repair the original current v4 package and binding only')
    expected = rendered['properties']
    keys = ('ReviewText', 'ActionFormVersion', 'Category', 'ActionPageURL', 'OwnerSkill', 'ResumeStep')
    if all(props.get(k) == expected[k] for k in keys):
        return {'status': 'EmailReviewPublicationUnchanged', 'writes': [], 'send_allowed': False}
    if (checked(props.get('Consent')) or props.get('AttemptId') or props.get('Decision') == 'Approve'
            or blocks(task, 'email-decision-v2', required=False)):
        raise ValueError('Preserve existing consent/attempt evidence; do not reset or invent approval during repair')
    message = package['labels']['consent_help']
    expected = {**expected, 'Result': message}
    return {'status': 'EmailReviewPublicationPlanned', 'writes': [
                {'page_id': identity, 'command': 'update_properties', 'properties': expected}],
            'send_allowed': False, 'scope': 'Finish the original saved review projection only; never create another task or consent'}


def checked(value):
    if value is True or value == '__YES__':
        return True
    if value is False or value is None or value == '__NO__':
        return False
    raise ValueError('Use the original typed Notion Consent checkbox, not a truthy string or number')


def accept(data):
    from email_flow import validate, digest, moment
    original = object_result(data['task'])
    if original.get('metadata', {}).get('type') != 'page' or page_id(original['id']) != page_id(data['task_id']):
        raise ValueError('Use the original canonical task capture')
    page_body(data['task']); props = properties(data['task'])
    package = blocks(data['task'], CONTRACT)[1]
    binding = blocks(data['task'], 'action-binding')[1]
    validate(package)
    identity = page_id(package['task_page_id'])
    if (identity != page_id(data['task_id']) or identity != page_id(package['action_page_id'])
            or page_id(props.get('ActionPageURL', '')) != identity
            or props.get('ContentVersion') != package['content_version']
            or props.get('ActionFormVersion') != CONTRACT
            or props.get('State') in {'Completed', 'Cancelled'}
            or props.get('Mode') != 'Automatic' or props.get('Category') != 'SendApproval'
            or props.get('OwnerSkill') != 'eightdegrees-sales-reply'
            or props.get('ResumeStep') != 'SendApprovedReply'
            or props.get('OperatorId') != package['operator_id']
            or data['operator_id'] != package['operator_id']
            or binding != render(package)['binding']):
        raise ValueError('Consent must bind the actual current task/operator/version')
    if props.get('ReviewText') not in {narrative(package), narrative(package, historical=True)}:
        return {'status': 'EmailRevisionRequired', 'send_allowed': False,
                'reason': 'Narrative edited; synchronize a new draft/version and reset Consent before approval'}
    if not checked(props.get('Consent')):
        return {'status': 'EmailConsentPending', 'send_allowed': False,
                'reason': 'Consent unchecked; wait or honor withdrawal for this email only'}
    moment(data['now'])
    decision = {'contract': CONTRACT, 'decision': 'Approve', 'task_id': package['task_page_id'],
                'action_page_id': package['task_page_id'], 'operator_id': package['operator_id'],
                'content_version': package['content_version'], 'package_sha256': package['package_sha256'],
                'observed_at': data['now'], 'comments': ''}
    sha = digest({k: v for k, v in decision.items() if k != 'observed_at'})
    prior = blocks(data['task'], 'email-decision-v2', required=False)
    return {'status': 'EmailDecisionAccepted', 'record_type': 'email-decision-v2',
            'decision': decision, 'package': package, 'input_sha256': sha,
            'reused_accepted_snapshot': bool(prior and prior[1].get('input_sha256') == sha),
            'send_allowed': False,
            'scope': 'Checking Consent submits this exact visible reply; persist decision/attempt before dispatch'}


def observe(data):
    """Discover native checkbox edits without fetching an extra action page."""
    from email_flow import digest
    original = object_result(data['task']); props = properties(data['task'])
    package = blocks(data['task'], CONTRACT)[1]
    from email_flow import validate
    validate(package)
    identity = page_id(original['id'])
    if identity != page_id(package['task_page_id']) or props.get('ActionFormVersion') != CONTRACT:
        raise ValueError('Observe only the current original consent task')
    consent = checked(props.get('Consent'))
    revision = digest({'task': identity, 'package': package['package_sha256'],
                       'consent': consent, 'review': props.get('ReviewText')})
    previous = data.get('previous_revision')
    if previous is not None:
        from email_flow import moment
        if not isinstance(previous, str) or not previous.split(':', 1)[0] or len(previous.split(':', 1)[0]) != 64:
            raise ValueError('Use the original saved actions-feed revision')
        if previous.split(':', 1)[0] == revision:
            revision = previous
        else:
            moment(data['now'])
            revision += ':'+data['now']
    prior = blocks(data['task'], 'email-decision-v2', required=False)
    active = props.get('State') not in {'Completed', 'Cancelled'}
    events = []
    if active and (consent or prior):
        events.append({'kind': 'submission', 'source_key': package['source_key'],
                       'step': 'SendApprovedReply', 'version': package['content_version'],
                       'input_digest': revision, 'task_id': identity,
                       'evidence_ref': 'https://app.notion.com/p/'+identity})
    return {'status': 'EmailConsentObserved', 'record': {'id': identity, 'revision': revision, 'events': events},
            'send_allowed': False, 'scope': 'Current checkbox/narrative revision only, not approval acceptance'}


def read_plan(data):
    """Reuse the actual task-list query; fetch full pages only on real demand."""
    from email_flow import digest, moment
    from backlog_recovery import task_source_key
    now = moment(data['now'])
    if data.get('rows_complete') is not True or not isinstance(data.get('rows'), list):
        raise ValueError('Incomplete task-list coverage cannot prove no changed input')
    previous, pending = {}, []
    if data.get('index_page') is not None:
        index = blocks(data['index_page'], 'scan-event-index-v1')[1]
        if page_id(index['root_id']) != page_id(data['root_id']):
            raise ValueError('Use the original event index for this installation')
        previous = index.get('feeds', {}).get('actions', {}).get('revisions', {})
        pending = list(index.get('pending', {}).values())
    from email_timing import release as release_email_delay
    eligible = [release_email_delay(v) for v in pending]
    demand_keys = {(v.get('source_key'), v.get('step'), v.get('version')) for v in eligible
                   if not v.get('due_at') or moment(v['due_at']) <= now}
    fetch, records, fallback, seen = [], [], [], set()
    for row in data['rows']:
        if row.get('ActionFormVersion') != CONTRACT or row.get('State') in {'Completed', 'Cancelled'}:
            continue
        identity = page_id(row['url'])
        if identity in seen:
            raise ValueError('Duplicate canonical task rows')
        seen.add(identity)
        needed = {'Consent', 'ReviewText', 'ContentVersion', 'SourceKey', 'OwnerSkill', 'ResumeStep', 'Mode'}
        if not needed.issubset(row):
            fallback.append(row['url']); continue
        if (row['OwnerSkill'] != 'eightdegrees-sales-reply' or row['ResumeStep'] != 'SendApprovedReply'
                or row['Mode'] != 'Automatic'):
            fallback.append(row['url']); continue
        consent = checked(row['Consent'])
        source = task_source_key(row)
        if not source or not isinstance(row['ReviewText'], str) or not row['ContentVersion']:
            fallback.append(row['url']); continue
        record_id = 'consent-row:'+identity
        base = digest({'task': identity, 'version': row['ContentVersion'],
                       'consent': consent, 'review': row['ReviewText']})
        old = previous.get(record_id)
        revision = old if old and old.split(':', 1)[0] == base else base+(':'+data['now'] if old else '')
        changed = revision != old
        # A new unchecked row is a wait, not input. Later edits/withdrawals are
        # actual events; ready saved recovery still runs without a new edit.
        events = []
        if changed and (consent or old is not None):
            events.append({'kind': 'submission', 'source_key': source,
                           'step': 'SendApprovedReply', 'version': row['ContentVersion'],
                           'input_digest': revision, 'task_id': identity, 'evidence_ref': row['url']})
        demand = (source, 'SendApprovedReply', row['ContentVersion']) in demand_keys
        if events or demand:
            fetch.append(row['url'])
        records.append({'id': record_id, 'revision': revision, 'events': events})
    return {'status': 'ConsentReadPlanPrepared', 'task_page_urls': sorted(set(fetch+fallback)),
            'row_records': records, 'fallback_task_urls': fallback,
            'page_fetches_required': len(set(fetch+fallback)),
            'unchanged_or_unsubmitted_skipped': len(seen)-len(set(fetch+fallback)),
            'external_actions_allowed': False,
            'scope': 'Current scoped task-list properties select reads only; full current acceptance still gates sending'}


def view_plan(data):
    from operator_experience import _schema
    source, state = _schema(data['pending_source'])
    page = object_result(data['page']); page_body(data['page'])
    if page.get('metadata', {}).get('type') != 'page':
        raise ValueError('Use the actual Today page')
    required = {'Name': 'title', 'State': 'select', 'Category': 'select',
                'OwnerSkill': 'text', 'ActionFormVersion': 'text'}
    schema = state['schema']
    if any(schema.get(k, {}).get('type') != v for k, v in required.items()):
        raise ValueError('Use the original compatible PendingTasks schema; never change existing types')
    additions = []
    for name, kind, ddl in [('ReviewText', 'text', 'RICH_TEXT'), ('Consent', 'checkbox', 'CHECKBOX')]:
        if name in schema:
            if schema[name].get('type') != kind or schema[name].get('readOnly'):
                raise ValueError('Incompatible/read-only review property: '+name)
        else:
            additions.append('ADD COLUMN "'+name+'" '+ddl)
    configure = ('FILTER "ActionFormVersion" = "email-review-v4" AND "Category" = "SendApproval" '
                 'AND "OwnerSkill" = "eightdegrees-sales-reply" AND "State" != "Completed" AND "State" != "Cancelled"; '
                 'SHOW "Consent", "ReviewText", "Name"; WRAP CELLS true; '
                 'WIDTH "Name" 160, "ReviewText" 560, "Consent" 90')
    return {'status': 'ConsentViewPlanned', 'statements': '; '.join(additions),
            'data_source_id': page_id(source['id']), 'view': {'parent_page_id': page_id(page['id']),
            'data_source_id': page_id(source['id']), 'type': 'table',
            'name': '\u90ae\u4ef6\u5ba1\u6838' if data.get('language') == 'zh-CN' else 'Email Review',
            'show_data_source_title': False, 'configure': configure},
            'scope': 'Reuse the registered view if present; add only missing properties; no task/consent mutations'}


def check_publication(before, after, props):
    """A newly frozen version always starts unchecked, including upgrades."""
    import json, re
    def packages(body):
        result = []
        for raw in re.findall(r'```json\s*\n(.*?)\n```', body, re.S):
            try: value = json.loads(raw)
            except ValueError: continue
            if isinstance(value, dict) and value.get('record_type') == CONTRACT:
                result.append(value)
        return result
    new = packages(after)
    old = packages(before)
    if not new:
        return
    if len(new) != 1:
        raise ValueError('Keep one current canonical consent package')
    if 'Consent' in props and checked(props['Consent']):
        raise ValueError('Workflow publication cannot manufacture human Consent')
    if new != old:
        expected = render(new[0])['properties']
        for name in ('Consent', 'ReviewText', 'ActionFormVersion', 'ContentVersion', 'ActionPageURL'):
            if name not in props or props[name] != expected[name]:
                raise ValueError('A new review version must publish its narrative and reset Consent together: '+name)
