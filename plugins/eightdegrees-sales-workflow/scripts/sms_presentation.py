#!/usr/bin/env python3
"""Plan related SMS status repairs from actual captures; never request a message."""

import copy
import hashlib
import json
import re
from datetime import datetime

from email_presentation import blocks, current_patch, properties
from notion_checks import object_result, page_body, page_id

OWNER = 'eightdegrees-sms-follow-up'
ROLES = {'notification', 'result', 'data_task', 'data_action', 'data_run', 'send_run', 'cycle'}
PENDING = {'AwaitingPhone', 'PendingApproval', 'ProviderAccepted', 'Unknown'}
NETWORK = {'SentToNetwork', 'Delivered'}


def notification(capture):
    body = page_body(capture)
    values = []
    for raw in re.findall(r'```json\s*\n(.*?)\n```', body, re.S):
        try:
            value = json.loads(raw)
        except ValueError:
            continue
        if isinstance(value, dict) and value.get('contract') == 'sms-notification-v1':
            values.append(value)
    if len(values) != 1:
        raise ValueError('Read one original frozen notification')
    return values[0]


def plan(data):
    pages = data['pages']
    if set(pages) != ROLES:
        raise ValueError('Read all seven related original SMS pages')
    props = {k: properties(v) for k, v in pages.items()}
    ids = {k: page_id(object_result(v)['id']) for k, v in pages.items()}
    if len(set(ids.values())) != len(ids):
        raise ValueError('Distinct related SMS pages cannot alias')
    frozen = notification(pages['notification'])
    _, attempt = blocks(pages['notification'], 'sms-send-attempt')
    _, receipt = blocks(pages['notification'], 'sms-provider-result')
    old_outcome_block, old = blocks(pages['notification'], 'sms-current-outcome')
    cycle_block, cycle = blocks(pages['cycle'], 'sms-cycle-current-state')
    body_digest = hashlib.sha256(frozen['body'].encode()).hexdigest()
    version = frozen['content_version']
    if (page_id(frozen['task_id']) != ids['notification'] or frozen['body_sha256'] != body_digest
            or page_id(old['task_id']) != ids['notification'] or old['content_version'] != version
            or old.get('payload_sha256') != body_digest
            or attempt['attempt_id'] != old['attempt_id'] or receipt['attempt_id'] != old['attempt_id']
            or attempt['payload_sha256'] != body_digest or receipt['payload_sha256'] != body_digest
            or any(attempt[k] != frozen[k] for k in ('body', 'recipient', 'device_id', 'content_version'))):
        raise ValueError('Original notification, attempt, receipt and outcome differ')
    initial = object_result(receipt['provider_result'])
    original_id = initial.get('id', initial.get('Id'))
    current = object_result(data['provider_status'])
    message = current.get('id', current.get('Id'))
    status = current.get('status', current.get('Status'))
    if (message != original_id or message != old['message_id']
            or status not in PENDING | NETWORK | {'Failed'}
            or current.get('deviceId', frozen['device_id']) != frozen['device_id']):
        raise ValueError('Read the exact original provider request status')
    previous = old['provider_status']
    if (previous == 'Delivered' and status != 'Delivered'
            or previous == 'SentToNetwork' and status not in NETWORK
            or previous == 'Failed' and status != 'Failed'):
        raise ValueError('Conflicting provider regression; reconcile, never overwrite or resend')
    if (page_id(cycle['cycle_page_id']) != ids['cycle']
            or page_id(cycle['task_page_id']) != ids['data_task']
            or page_id(cycle['action_page_id']) != ids['data_action']
            or page_id(cycle['run_page_id']) != ids['data_run']
            or cycle['current_outcome']['message_id'] != message
            or page_id(cycle['current_outcome']['task_id']) != ids['notification']
            or props['notification']['CycleId'] != cycle['cycle_id']
            or props['data_task']['CycleId'] != cycle['cycle_id']):
        raise ValueError('SMS cycle does not bind these original task/action/run pages')
    for role, action in [('notification', 'result'), ('data_task', 'data_action')]:
        p = props[role]
        step = 'SendNotificationSms' if role == 'notification' else 'PrepareSmsFollowUp'
        if (p.get('OwnerSkill') != OWNER or p['ContentVersion'] != version
                or p.get('ResumeStep') != step or p.get('StepId') != step
                or page_id(p['ActionPageURL']) != ids[action]):
            raise ValueError('Original task route/version/action differs')
    for role, task in [('send_run', 'notification'), ('data_run', 'data_task')]:
        if props[role].get('Skill') != OWNER or props[role]['RunId'] != props[task]['RunId']:
            raise ValueError('Related SMS run identity differs')
    if props['data_task']['State'] != 'Completed':
        raise ValueError('Input acceptance must finish under its original owner first')
    at = datetime.fromisoformat(data['observed_at'].replace('Z', '+00:00'))
    prior_at = datetime.fromisoformat(old['observed_at'].replace('Z', '+00:00'))
    if at.tzinfo is None or at < prior_at:
        raise ValueError('Observation cannot predate the saved outcome')
    outcome = copy.deepcopy(old)
    outcome.update(provider_status=status, sent=status in NETWORK,
                   reserved=status in PENDING, provider_delivered=status == 'Delivered')
    outcome['provider'] = outcome['provider'] | {'status': status}
    if outcome != old:
        outcome['observed_at'] = data['observed_at']
    updated_cycle = copy.deepcopy(cycle)
    updated_cycle.update(current_outcome=outcome, last_request_id=message,
                         last_provider_status=status, pending_status=status)
    # Never recompute global counts, re-open a stopped cycle, release an unknown
    # slot or infer network-send time from the time this status was queried.
    if status in NETWORK:
        if cycle.get('reserved_count') not in (0, 1):
            raise ValueError('Ambiguous reservations need count reconciliation')
        if cycle.get('pending_request_id') not in (None, message) or (
                cycle.get('reserved_count') == 1 and cycle['current_outcome']['provider_status'] in NETWORK):
            raise ValueError('Another reservation cannot be released by this known request')
        if cycle['current_outcome']['provider_status'] not in NETWORK:
            if (cycle.get('reserved_count') != 1 or cycle.get('count_verified') is not True
                    or type(cycle.get('known_this_executor_sent')) is not int):
                raise ValueError('A newly observed network send must reconcile its one reserved count')
            updated_cycle['known_this_executor_sent'] += 1
        updated_cycle.update(reserved_count=0, unknown_attempt=False, pending_request_id=None)
    stopped = cycle.get('stop') is True or cycle.get('manual_pause') is True
    if stopped:
        updated_cycle.update(active=False, next_due=None)
    language = data.get('language', 'en')
    if language not in {'en', 'zh-CN'}:
        raise ValueError('Use the saved workspace language')
    text = 'SMS ' + status + ' \u00b7 ' + message + '.'
    if language == 'zh-CN':
        text += ' ' + ('\u672c\u8be2\u76d8\u540e\u7eed\u77ed\u4fe1\u5df2\u505c\u6b62\u3002' if stopped else '\u540e\u7eed\u5b89\u6392\u89c1\u539f\u901a\u77e5\u5468\u671f\u3002')
        text += ' \u65e0\u9700\u91cd\u590d\u5ba1\u6279\u6216\u63d0\u4ea4\uff1b\u624b\u673a\u5b9e\u9645\u6536\u4ef6\u53e6\u884c\u8bb0\u5f55\u3002'
    else:
        text += ' ' + ('Future SMS stopped for this enquiry.' if stopped else 'Use the registered cycle for next due work.')
        text += ' No new approval or resubmission; handset receipt is separate.'
    updates = []
    for role in ('notification', 'data_task'):
        desired = {'Result': text}
        if role == 'notification' and props[role]['State'] == 'InProgress' and status in NETWORK:
            desired['State'] = 'Completed'
        desired = {k: v for k, v in desired.items() if props[role].get(k) != v}
        if desired:
            updates.append({'role': role, 'command': 'update_properties', 'properties': desired})
    for role in ('result', 'data_action'):
        body = page_body(pages[role])
        edits = []
        for names in ({'current status', '\u5f53\u524d\u72b6\u6001'}, {'processing result', '\u5904\u7406\u7ed3\u679c'}):
            edit = current_patch(body, names, text)
            if edit:
                edits.append(edit)
        if role == 'result':
            saved_block, result = blocks(pages[role], 'sms-current-outcome')
            if result.get('message_id') != message or page_id(result['task_id']) != ids['notification']:
                raise ValueError('Result page identifies another request')
            if result != outcome:
                edits.append({'old_str': saved_block, 'new_str': json_block(outcome)})
        if edits:
            updates.append({'role': role, 'command': 'update_content', 'content_updates': edits})
    if old != outcome:
        updates.append({'role': 'notification', 'command': 'update_content', 'content_updates': [
            {'old_str': old_outcome_block, 'new_str': json_block(outcome)}]})
    if cycle != updated_cycle:
        updates.append({'role': 'cycle', 'command': 'update_content', 'content_updates': [
            {'old_str': cycle_block, 'new_str': json_block(updated_cycle)}]})
    for role in ('data_run', 'send_run'):
        p = props[role]
        if p.get('State') in {'Cancelled', 'Paused'} or (p.get('State') == 'Error' and not (
                role == 'send_run' and status == 'Failed' and p.get('CurrentStep') == 'Failed')):
            raise ValueError('Explicitly paused/cancelled/error run requires its owner, not presentation repair')
        final = role == 'data_run' or status in NETWORK
        desired = {'Summary': text}
        if p['State'] != 'Completed':
            desired.update(State='Completed' if final else 'InProgress',
                           CurrentStep='RegistrationCompleted' if role == 'data_run' else status)
        # A Failed/Unknown request is not made successful by closing a scan.
        if status == 'Failed' and role == 'send_run':
            desired.update(State='Error', CurrentStep='Failed')
        desired = {k: v for k, v in desired.items() if p.get(k) != v}
        if desired:
            updates.append({'role': role, 'command': 'update_properties', 'properties': desired})
    entity_id = page_id(data.get('maintenance_task_id', ids['notification']))
    if 'maintenance_task_id' in data and entity_id in ids.values():
        raise ValueError('Maintenance must not impersonate a related original')
    return {'status': 'SMSPresentationPlanned', 'entity_id': entity_id, 'notification_task_id': ids['notification'],
            'page_ids': ids, 'content_version': version, 'message_id': message, 'updates': updates,
            'projection_page_ids': list(ids.values()),
            'scope': 'Original related SMS status only; no request, approval, payload, count reset or stop expansion'}


def json_block(value):
    return '```json\n' + json.dumps(value, ensure_ascii=False, indent=2) + '\n```'


def verify(data):
    result = plan(data)
    if set(data['saved_pages']) != ROLES:
        raise ValueError('Read back all related original pages')
    issues = []
    for role, original in data['pages'].items():
        body, props = page_body(original), properties(original)
        for update in result['updates']:
            if update['role'] == role:
                props.update(update.get('properties', {}))
                for edit in update.get('content_updates', []):
                    if body.count(edit['old_str']) != 1:
                        raise ValueError('Ambiguous original exact anchor')
                    body = body.replace(edit['old_str'], edit['new_str'], 1)
        saved = data['saved_pages'][role]
        if (page_id(object_result(saved)['id']) != result['page_ids'][role]
                or properties(saved) != props or page_body(saved) != body):
            issues.append(role + ': current result or protected content differs')
    return {k: v for k, v in result.items() if k != 'updates'} | {
        'status': 'NeedsCorrection' if issues else 'SMSPresentationVerified', 'issues': issues}
