"""One inquiry package, one human decision, one dispatch check. No connector I/O."""
import base64
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from api_result import confirm
from email_presentation import blocks, properties
from notion_checks import page_body, page_id, object_result
from reply_transport import manifest, verify
from workflow_checks import visible_markdown

CONTRACT = 'email-review-v2'
LABELS = json.loads((Path(__file__).resolve().parents[1]/'assets/email-review-labels.json').read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def moment(text):
    value = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if value.utcoffset() is None:
        raise ValueError('Send times need explicit offsets')
    return value


def validate(package):
    if package.get('record_type') != CONTRACT:
        raise ValueError('This is not a combined email review; old Confirm decisions never authorize sending')
    m, html = manifest({'manifest': package['manifest']})
    for key in ('source_page_id', 'task_page_id', 'action_page_id', 'root_id'):
        page_id(package[key])
    if (page_id(m['task_page_id']) != page_id(package['task_page_id'])
            or m['content_version'] != package['content_version']
            or package['source_key'] != m['from_address']+':inbound:'+m['reply_message_id']
            or not package.get('operator_id')):
        raise ValueError('Reply differs from its original source/task/version/operator')
    window = package['window']
    ZoneInfo(window['timezone'])
    if moment(window['not_before']) >= moment(window['not_after']):
        raise ValueError('Invalid visible send window')
    if package.get('package_sha256') != digest({k: v for k, v in package.items() if k != 'package_sha256'}):
        raise ValueError('Frozen local package changed; prepare a new version for review')
    return m, html


def prepare(data):
    """Bind previously prepared draft, source receipt, preview and material snapshot."""
    transport = data['transport']
    m, _ = manifest(transport)
    if 'write_result' not in transport:
        raise ValueError('Use the original draft API acknowledgement, not a raw MIME readback')
    draft = verify(transport)
    if draft['status'] != 'StoredReplyVerified':
        raise ValueError('Draft write is unknown')
    source = confirm({**data['source_write'], 'service': 'notion', 'expected_id': data['source_page_id']})
    if source['status'] != 'APIWriteConfirmed':
        raise ValueError('Persist the original source before offering its reply review')
    preview = data['review_ready']
    if (preview.get('status') != 'EmailReviewReady'
            or page_id(preview['task_page_id']) != page_id(m['task_page_id'])
            or preview['content_version'] != m['content_version']
            or preview['html_sha256'] != m['html_sha256']
            or preview['draft_binding_sha256'] != draft['draft_binding_sha256']):
        raise ValueError('Use the prepared same-version copy/preview acknowledgements')
    package = {k: copy.deepcopy(data[k]) for k in ('root_id', 'source_page_id', 'source_key',
               'action_page_id', 'operator_id', 'window')}
    if type(data.get('material', True)) is not bool:
        raise ValueError('Record whether this reply actually provides project materials')
    package.update(material=data.get('material', True), receipt_template='send-receipt-v2', record_type=CONTRACT, task_page_id=m['task_page_id'], content_version=m['content_version'],
                   manifest=copy.deepcopy(m), draft_verification=draft,
                   source_snapshot_id=data.get('source_snapshot_id'),
                   material_sources=copy.deepcopy(data.get('material_sources', [])),
                   crm_target=copy.deepcopy(data.get('crm_target')),
                   preview_page_id=preview.get('preview_page_id', preview['copy_page_id']),
                   labels=LABELS.get(data.get('language', 'en'), LABELS['en']))
    package['package_sha256'] = digest(package)
    validate(package)
    return {'status': 'SingleEmailReviewPrepared', 'package': package,
            'required_human_decisions': 1, 'next_step': 'SendApprovedReply',
            'send_allowed': False, 'scope': 'Publish one combined review; no prior content-review task or sending authority'}


def window_text(window):
    zone = ZoneInfo(window['timezone'])
    return ' / '.join(moment(window[k]).astimezone(zone).isoformat() for k in ('not_before', 'not_after'))+' ('+window['timezone']+')'


def render(data):
    package = data['package']; m, html = validate(package)
    labels = package['labels']
    binding = {'record_type': 'action-binding', 'ApprovalContract': CONTRACT,
               'TaskPageId': package['task_page_id'], 'ActionPageId': package['action_page_id'],
               'OwnerSkill': 'eightdegrees-sales-reply', 'ResumeStep': 'SendApprovedReply',
               'StepId': 'SendApprovedReply', 'Category': 'SendApproval', 'Mode': 'Automatic',
               'ContentVersion': package['content_version'], 'OperatorId': package['operator_id'],
               'ResumeContractVersion': 'resume-v1', 'PackageSha256': package['package_sha256'],
               'DraftBindingSha256': package['draft_verification']['draft_binding_sha256'],
               'Choices': {labels[k]: v for k, v in [('approve', 'Approve'), ('return', 'Return'),
                                                   ('pause', 'Pause'), ('cancel', 'Cancel')]},
               'SubmissionLabel': labels['submit']}
    window = package['window']
    lines = ['## '+labels['status'], '', labels['ready'], '',
             'From: `'+m['from_address']+'`', 'To: `'+m['to']+'`',
             'Cc: `'+(m.get('cc') or '(none)')+'`', 'Bcc: `'+(m.get('bcc') or '(none)')+'`', '',
             labels['receipt'], '',
             'Window: `'+window_text(window)+'`', '',
             '<mention url="https://app.notion.com/p/'+page_id(package['preview_page_id'])+'" />', '',
             '## Email subject', '', m['subject'], '', '## Email HTML', '', '```html',
             html.decode('utf-8'), '```', '', '## '+labels['input'], '', labels['meaning'], '']
    lines += ['- [ ] '+labels[k] for k in ('approve', 'return', 'pause', 'cancel')]
    lines += ['', '### '+labels['comments'], '', labels['placeholder'], '', '- [ ] '+labels['submit'], '',
              '## '+labels['result'], '', labels['waiting'], '', '<details>', '<summary>Workflow records</summary>', '',
              '```json', json.dumps(binding, ensure_ascii=True, indent=2), '```', '',
              '```json', json.dumps(package, ensure_ascii=True, indent=2), '```', '</details>']
    return {'status': 'SingleEmailReviewRendered', 'content': '\n'.join(lines)+'\n', 'binding': binding,
            'scope': 'One page and one decision group; approval includes this exact draft and visible window'}


def accept(data):
    """Read the original task/action once; validate only the submitted decision."""
    for name in ('task', 'action'):
        observed = object_result(data[name])
        if observed.get('metadata', {}).get('type') != 'page' or page_id(observed['id']) != page_id(data[name+'_id']):
            raise ValueError('Use the actual registered task and action captures')
        page_body(data[name])
    task = properties(data['task'])
    package = blocks(data['action'], CONTRACT)[1]
    binding = blocks(data['action'], 'action-binding')[1]
    m, html = validate(package)
    action_id = page_id(data['action_id'])
    if (page_id(data['task_id']) != page_id(package['task_page_id'])
            or page_id(task['ActionPageURL']) != action_id or page_id(package['action_page_id']) != action_id
            or task.get('ContentVersion') != package['content_version']
            or task.get('ResumeStep') != 'SendApprovedReply' or task.get('OwnerSkill') != 'eightdegrees-sales-reply'
            or task.get('Mode') != 'Automatic'
            or binding.get('Mode') != 'Automatic' or binding.get('Category') != 'SendApproval'
            or binding.get('OwnerSkill') != 'eightdegrees-sales-reply'
            or binding.get('ResumeStep') != 'SendApprovedReply'
            or binding.get('OperatorId') != package['operator_id']
            or task.get('State') in {'Completed', 'Cancelled'}
            or task.get('OperatorId') != package['operator_id']
            or data['operator_id'] != package['operator_id']
            or binding.get('ApprovalContract') != CONTRACT
            or page_id(binding['TaskPageId']) != page_id(package['task_page_id'])
            or page_id(binding['ActionPageId']) != action_id
            or binding.get('ContentVersion') != package['content_version']
            or binding.get('PackageSha256') != package['package_sha256']
            or binding.get('DraftBindingSha256') != package['draft_verification']['draft_binding_sha256']):
        raise ValueError('Current task/action/operator/version does not bind this combined review')
    body = page_body(data['action'])
    for label, value in [('From', m['from_address']), ('To', m['to']), ('Cc', m.get('cc', '')),
                         ('Bcc', m.get('bcc', '')), ('Window', window_text(package['window']))]:
        if re.findall(r'^'+label+r': ([^\n]*)$', body.split('## Email subject', 1)[0], re.M) != ['`'+(value or '(none)')+'`']:
            return {'status': 'EmailRevisionRequired', 'send_allowed': False,
                    'reason': 'Visible recipient/window changed; prepare that new package before approval'}
    def section(name):
        headings = list(re.finditer(r'^## ([^\n]+)\n', visible_markdown(body), re.M))
        matches = [v for v in headings if v[1] == name]
        if len(matches) != 1:
            raise ValueError('Missing/duplicate review section: '+name)
        selected = matches[0]
        end = next((v.start() for v in headings if v.start() > selected.start()), len(body))
        return body[selected.end():end].strip('\n')
    if section('Email subject') != m['subject'] or section('Email HTML') != '```html\n'+html.decode('utf-8')+'\n```':
        return {'status': 'EmailRevisionRequired', 'send_allowed': False,
                'reason': 'Editable copy changed; prepare the updated draft/version before accepting approval'}
    checked = re.findall(r'^\s*- \[[xX]\] ([^\n]+)', visible_markdown(body), re.M)
    labels = package['labels']
    expected_choices = {labels[k]: v for k, v in [('approve', 'Approve'), ('return', 'Return'),
                                                ('pause', 'Pause'), ('cancel', 'Cancel')]}
    if binding.get('Choices') != expected_choices or binding.get('SubmissionLabel') != labels['submit']:
        raise ValueError('Combined review choices were changed')
    selected = [choice for label, choice in expected_choices.items() if label in checked]
    if checked.count(labels['submit']) > 1 or len(selected) != 1:
        raise ValueError('Submit exactly one decision; saving a draft or old Confirm is not send approval')
    comment = re.search(r'^### '+re.escape(labels['comments'])+r'\n([\s\S]*?)(?=^- \[|^## |\Z)', body, re.M)
    comments = comment[1].strip() if comment else ''
    if comments == labels['placeholder']:
        comments = ''
    if selected[0] == 'Return' and not comments:
        raise ValueError('Return needs useful revision instructions')
    decision = {'contract': CONTRACT, 'decision': selected[0], 'task_id': package['task_page_id'],
                'action_page_id': package['action_page_id'], 'operator_id': package['operator_id'],
                'content_version': package['content_version'], 'package_sha256': package['package_sha256'],
                'observed_at': data['now'], 'comments': comments}
    moment(data['now'])
    input_sha = digest({k: v for k, v in decision.items() if k != 'observed_at'})
    reused = checked.count(labels['submit']) == 0
    if reused:
        if not data.get('allow_consumed'):
            raise ValueError('No new submitted decision')
        prior = blocks(data['task'], 'email-decision-v2')[1]
        if (prior.get('input_sha256') != input_sha or prior.get('decision', {}).get('decision') != selected[0]
                or {k: v for k, v in prior.get('decision', {}).items() if k != 'observed_at'}
                != {k: v for k, v in decision.items() if k != 'observed_at'}):
            raise ValueError('Consumed approval changed or is not recorded on the original task')
    return {'status': 'EmailDecisionAccepted', 'record_type': 'email-decision-v2',
            'decision': decision, 'package': package, 'input_sha256': input_sha,
            'reused_accepted_snapshot': reused, 'send_allowed': False,
            'scope': 'One observed decision; persist it and the original attempt before dispatch'}


def dispatch(data):
    """Single final local gate using one fresh task/action/control observation."""
    if not isinstance(data.get('send_tool'), str) or not data['send_tool'].endswith('send_draft'):
        raise ValueError('Use the installed Gmail send_draft tool only')
    if data['policy'] not in {'one-cycle-approved-work', 'scheduled-approved-work', 'owner-workflow'}:
        raise ValueError('This invocation cannot send')
    accepted = accept({**data, 'allow_consumed': True})
    if accepted['status'] != 'EmailDecisionAccepted' or accepted['decision']['decision'] != 'Approve':
        return {'status': 'EmailDispatchDeferred', 'send_allowed': False, 'reason': 'No current combined Approve decision'}
    package = accepted['package']; controls = data['controls']
    if data['sender_account'] != package['manifest']['from_address']:
        raise ValueError('Current authorized sender differs from this approved draft')
    required = ('scan_enabled', 'channel_enabled', 'no_reply_or_stop', 'attempt_clear', 'approval_current', 'date_allowed')
    if any(controls.get(key) is not True for key in required):
        return {'status': 'EmailDispatchDeferred', 'send_allowed': False, 'reason': 'Current stop/channel/approval/attempt control blocks this item'}
    now, window = moment(data['now']), package['window']
    if not moment(window['not_before']) <= now <= moment(window['not_after']):
        return {'status': 'EmailDispatchDeferred', 'send_allowed': False, 'reason': 'Outside the approved window'}
    if data.get('attempt_status') not in {None, 'RejectedBeforeDispatch', 'NoEffectVerified'}:
        return {'status': 'EmailDispatchDeferred', 'send_allowed': False, 'reason': 'Preserve the existing accepted/pending/unknown attempt; never resend'}
    if not data.get('attempt_id'):
        raise ValueError('Prepare a stable attempt ID before dispatch')
    if data['accepted_input_sha256'] != accepted['input_sha256']:
        raise ValueError('Input changed after acceptance')
    persisted = confirm({**data['attempt_write'], 'service': 'notion', 'expected_id': package['task_page_id']})
    if persisted['status'] != 'APIWriteConfirmed':
        raise ValueError('Persist decision and original attempt before calling Gmail')
    return {'status': 'EmailDispatchPrepared', 'send_allowed': True,
            'call': {'tool': data['send_tool'], 'args': {'draft_id': package['manifest']['draft_id']}},
            'package_sha256': package['package_sha256'], 'attempt_id': data['attempt_id'],
            'scope': 'Exact approved draft only; store original Gmail response, then enqueue standing-authorized SMS'}


def complete(data):
    """Close the email handoff from its original provider and own write receipts."""
    from provider_handoff import verify as handoff
    package = data['package']; validate(package)
    proof = handoff({'operation': 'email', 'manifest': package['manifest'],
                     'draft_verification': package['draft_verification'],
                     'request': {'draft_id': package['manifest']['draft_id']}, 'response': data['response']})
    for role in ('source', 'task', 'action'):
        expected = package[{'source': 'source_page_id', 'task': 'task_page_id', 'action': 'action_page_id'}[role]]
        result = confirm({**data['writes'][role], 'service': 'notion', 'expected_id': expected})
        if result['status'] != 'APIWriteConfirmed':
            return {'status': 'EmailRecordingPending', 'handoff_complete': True, 'retry_send_allowed': False,
                    'message_id': proof['message_id'], 'repair': role}
    followup = data.get('followup_write')
    followup_saved = followup is not None and confirm({**followup, 'service': 'notion'})['status'] == 'APIWriteConfirmed'
    crm = data.get('crm_write')
    crm_saved = crm is not None and confirm({**crm, 'service': 'crm'})['status'] == 'APIWriteConfirmed'
    return {'status': 'EmailHandoffRecorded', 'handoff_complete': True, 'retry_send_allowed': False,
            'message_id': proof['message_id'], 'provider_status': proof['provider_status'],
            'sms_registration_required': package.get('material') is True,
            'sms_registration_saved': followup_saved,
            'crm_recording_required': bool(package.get('crm_target')), 'crm_recording_saved': crm_saved,
            'pending_steps': (['register-followup'] if package.get('material') is True and not followup_saved else [])
                + (['record-crm-receipt'] if package.get('crm_target') and not crm_saved else []),
            'scope': 'Provider handoff and own API receipts; independent CRM/SMS recovery never resends the email'}
