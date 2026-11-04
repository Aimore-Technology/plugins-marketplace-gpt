"""Recover a submitted ordinary form's task projection; never accept or execute it."""
import hashlib
import json
import re

from email_presentation import blocks, current_patch, properties
from notion_checks import object_result, page_body, page_id
from workflow_checks import visible_markdown


def observe(data):
    task, props = data['task'], properties(data['task'])
    identity = page_id(object_result(task)['id'])
    if props.get('State') in {'Completed', 'Cancelled'}:
        return {'status': 'TaskSubmissionUnchanged', 'reason': 'Terminal step stays historical', 'writes': []}
    if props.get('ActionFormVersion') != 'task-action-v1':
        raise ValueError('Use the recorded ordinary action form; native email uses email.accept')
    action = data['action']
    action_id = page_id(object_result(action)['id'])
    if action_id != page_id(props['ActionPageURL']):
        raise ValueError('Read the original registered action page')
    binding = blocks(action, 'action-binding')[1]
    original = blocks(task, 'action-binding')[1]
    if page_id(binding['TaskPageId']) != identity or page_id(original['TaskPageId']) != identity:
        raise ValueError('Action belongs to another task')
    if binding.get('ActionPageId') and page_id(binding['ActionPageId']) != action_id:
        raise ValueError('Copied action page is not a submission')
    if original.get('ActionPageId') and page_id(original['ActionPageId']) != action_id:
        raise ValueError('Task binding points at a different action page')
    for name in ('TaskId', 'StepId', 'ContentVersion', 'Category', 'Mode', 'OwnerSkill',
                 'ResumeStep', 'ResumeContractVersion', 'OperatorId'):
        if not binding.get(name) or binding[name] != original.get(name):
            raise ValueError('Current task/action binding differs: ' + name)
        if name not in {'TaskId'} and props.get(name) != binding[name]:
            raise ValueError('Current task property differs: ' + name)
    label = binding.get('SubmissionLabel')
    if binding.get('read_only_result') or not isinstance(label, str) or not label or '\n' in label:
        return {'status': 'TaskSubmissionUnchanged', 'reason': 'Read-only result has no human submission', 'writes': []}
    body = page_body(action)
    starts = list(re.finditer(r'^## (?:Your input|\u60a8\u7684\u8f93\u5165)\s*$', visible_markdown(body), re.M | re.I))
    if len(starts) != 1:
        raise ValueError('Read the single original input section')
    start = starts[0].end()
    end = re.search(r'^## ', visible_markdown(body)[start:], re.M)
    raw = body[start:start + end.start() if end else len(body)].strip()
    todo = re.compile(r'^\s*- \[([ xX])\] ' + re.escape(label) + r'\s*$', re.M)
    controls = list(todo.finditer(visible_markdown(raw)))
    if len(controls) != 1:
        raise ValueError('Missing or repeated actual submission checkbox')
    if controls[0][1].lower() != 'x':
        return {'status': 'TaskSubmissionUnchanged', 'reason': 'Unsubmitted input remains editing', 'writes': []}
    intent = todo.sub('', raw).strip()
    digest = hashlib.sha256(json.dumps([identity, action_id, binding, intent], sort_keys=True,
                                      ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    message = ('\u5df2\u63d0\u4ea4\uff0c\u7b49\u5f85\u5de5\u4f5c\u6d41\u6838\u5bf9\u5e76\u7ee7\u7eed\uff1b\u65e0\u9700\u91cd\u590d\u586b\u5199\u6216\u63d0\u4ea4\u3002\u5c1a\u672a\u6267\u884c\u540e\u7eed\u4e1a\u52a1\u64cd\u4f5c\u3002'
               if data.get('language') == 'zh-CN' else
               'Submitted; queued for validation and continuation. Do not submit again. Later business steps are not complete.')
    action_updates = []
    action_patch = current_patch(body, {'current status', '\u5f53\u524d\u72b6\u6001'}, message)
    if action_patch:
        action_updates.append(action_patch)
    try:
        result_patch = current_patch(body, {'result', '\u5904\u7406\u7ed3\u679c'}, message)
    except ValueError:
        result_patch = None
    if result_patch and re.search(r'\u5c1a\u672a\u63d0\u4ea4|not (?:yet )?submitted', result_patch['old_str'], re.I):
        action_updates.append(result_patch)
    previous = blocks(task, 'observed-action-submission-v1', required=False)
    if (previous and previous[1].get('input_sha256') == digest
            and props.get('InputSubmitted') == '__YES__'
            and props.get('State') in {'ReadyToValidate', 'InProgress'}):
        repair = [{'page_id': action_id, 'command': 'update_content', 'content_updates': action_updates}] if action_updates and props['State'] == 'ReadyToValidate' else []
        return {'status': 'TaskSubmissionProjectionRepair' if repair else 'TaskSubmissionUnchanged',
                'reason': 'Original request already queued; repair only stale presentation', 'writes': repair}
    from email_flow import moment
    moment(data['now'])
    snapshot = {'record_type': 'observed-action-submission-v1', 'task_id': identity,
                'action_page_id': action_id, 'content_version': props['ContentVersion'],
                'input_sha256': digest, 'input_text': intent, 'submission_checked': True,
                'observed_at': data['now'], 'acceptance': False, 'send_allowed': False}
    patch = current_patch(page_body(task), {'current status', '\u5f53\u524d\u72b6\u6001'}, message)
    encoded = '```json\n' + json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n```'
    if previous:
        historical = dict(previous[1], record_type='historical-action-submission-v1')
        updates = [{'old_str': previous[0], 'new_str': '```json\n' + json.dumps(historical, ensure_ascii=False, indent=2) + '\n```\n\n' + encoded}]
        if patch:
            updates.append(patch)
    else:
        if not patch:
            raise ValueError('Missing unique task status anchor for the request snapshot')
        patch['new_str'] += '\n\n' + encoded
        updates = [patch]
    projected = {'InputSubmitted': '__YES__', 'State': 'InProgress' if props.get('State') == 'InProgress' else 'ReadyToValidate',
                 'OperatorInput': 'Submission observed; see original action and version-bound task snapshot.', 'Result': message}
    writes = [{'page_id': identity, 'command': 'update_content', 'content_updates': updates},
              {'page_id': identity, 'command': 'update_properties', 'properties': projected}]
    if action_updates:
        writes.append({'page_id': action_id, 'command': 'update_content', 'content_updates': action_updates})
    return {'status': 'TaskSubmissionQueued', 'task_id': identity, 'snapshot': snapshot,
            'writes': writes,
            'send_allowed': False, 'facts_approved': False,
            'scope': 'Save observation first, then its canonical queue projection; owning skill validates and applies the original request'}
