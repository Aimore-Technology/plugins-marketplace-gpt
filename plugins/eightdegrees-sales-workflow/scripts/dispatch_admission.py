"""Bind exact outgoing arguments to one saved queue admission; no provider I/O."""

import copy
import hashlib
import json
import re

from email_presentation import blocks
from notion_checks import object_result, page_body, page_id
from reply_transport import verify
from scan_cycle import advance, timestamp
import sms_authority


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def payload(data):
    call, channel = data['call'], data['channel']
    tool, args = call['tool'], call['args']
    if channel == 'email':
        transport = data['transport']
        if transport.get('phase', 'draft') != 'draft':
            raise ValueError('Dispatch needs the current unsent stored draft')
        result = verify(transport)
        if (result['status'] != 'StoredReplyVerified' or not tool.endswith('send_draft')
                or args != {'draft_id': result['draft_id']}):
            raise ValueError('Only the exact verified stored draft can be dispatched')
        task, version = result['entity_id'], result['content_version']
    elif channel == 'sms':
        notification = data['notification']
        result = sms_authority.verify(notification)
        frozen = notification['payload']
        if page_id(frozen['root_id']) != page_id(data['scan']['root_id']):
            raise ValueError('SMS notification belongs to another scan installation')
        if (not tool.endswith('request_sms') or set(args) != {'body', 'recipient', 'deviceId', 'idempotencyKey'}
                or any(args[a] != frozen[b] for a, b in [('body', 'body'), ('recipient', 'recipient'), ('deviceId', 'device_id')])):
            raise ValueError('SMS call differs from the saved notification')
        if len(args['body']) > 70 or not isinstance(args['idempotencyKey'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,100}', args['idempotencyKey']):
            raise ValueError('AndroidSync conservative preflight: body <=70 characters; key [A-Za-z0-9_-]{8,100}')
        task, version = result['entity_id'], result['content_version']
    else:
        raise ValueError('Unsupported dispatch channel')
    return page_id(task), version


def prepare(data):
    scan = data['scan']
    if scan.get('policy') not in {'one-cycle-approved-work', 'scheduled-approved-work'}:
        raise ValueError('This scan cannot prepare a customer dispatch')
    selection = advance(scan)
    if selection['status'] != 'ScanCyclePlanned' or len(selection['work']) != 1:
        raise ValueError('No current queue admission; do not prepare a send')
    work = selection['work'][0]
    task, version = payload(data)
    steps = {'email': {'SendApprovedReply', 'SendGeneralReply'}, 'sms': {'SendNotificationSms'}}
    if (work['action'] != 'owner_step' or work['key'] != data['work_key'] or work['step'] not in steps[data['channel']]
            or version != work['version'] or page_id(data['task_page_id']) != task):
        raise ValueError('Dispatch task/phase/version differs from current queue admission')
    return {'status': 'DispatchAdmissionPrepared', 'record': {
        'record_type': 'dispatch-admission-v1', 'root_id': page_id(scan['root_id']),
        'run_page_id': page_id(data['run_page_id']), 'invocation_id': scan['executor']['current_id'],
        'task_page_id': task, 'channel': data['channel'], 'work': work,
        'admitted_at': scan['now'], 'deadline': selection['deadline'],
        'call_sha256': digest(data['call'])}, 'scope': 'Persist/read back before preparing executable arguments; not approval'}


def release(data):
    original = prepare(data)['record']
    saved = object_result(data['saved_run'])
    page_body(data['saved_run'])
    if (saved.get('metadata', {}).get('type') != 'page' or page_id(saved['id']) != original['run_page_id']
            or blocks(data['saved_run'], 'dispatch-admission-v1')[1] != original):
        raise ValueError('Read back this exact prospective admission on its original run before dispatch')
    now = timestamp(data['now'])
    if now < timestamp(original['admitted_at']) or (now - timestamp(original['admitted_at'])).total_seconds() > 120:
        raise ValueError('Admission expired; obtain fresh queue observations and persist a new admission')
    current = data['current_scan']
    if (current['now'] != data['now'] or current['root_id'] != data['scan']['root_id']
            or current['started_at'] != data['scan']['started_at']
            or current['executor']['current_id'] != original['invocation_id'] or current.get('policy') != data['scan'].get('policy')):
        raise ValueError('Current dispatch observations belong to another clock/scan/policy')
    fresh = advance(current)
    if (fresh['status'] != 'ScanCyclePlanned' or not fresh['work'] or fresh['work'][0] != original['work']):
        raise ValueError('Stop, ownership, budget, work or version changed after admission')
    return {'status': 'DispatchArgumentsPrepared', 'call': copy.deepcopy(data['call']),
            'call_sha256': original['call_sha256'], 'admission': original,
            'scope': 'Exact admission-bound call only; retain fresh approval/stop/window/count/attempt checks; no host interception'}
