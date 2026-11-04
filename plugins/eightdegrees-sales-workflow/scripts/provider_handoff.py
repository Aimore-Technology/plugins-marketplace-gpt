#!/usr/bin/env python3
"""Bind a successful original dispatch response to our verified request, offline."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from notion_checks import object_result
from reply_transport import manifest, binding_fields, content_fields

ACCEPTED = {'ProviderAccepted', 'AwaitingPhone', 'PendingApproval', 'Sent', 'SentToNetwork', 'Delivered'}


def verify(data):
    operation = data['operation']
    response = object_result(data['response'])
    if response.get('success') is False or response.get('error') or response.get('errors'):
        raise ValueError('The original dispatch was explicitly rejected')
    identity = response.get('id', response.get('Id'))
    raw_status = response.get('status', response.get('Status'))
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError('Preserve an unacknowledged/unknown attempt; never fabricate a provider request ID')
    if raw_status is not None and raw_status not in ACCEPTED:
        raise ValueError('The original response does not confirm successful handoff')
    if operation == 'email':
        if raw_status is not None and raw_status not in {'Sent', 'ProviderAccepted', 'Delivered'}:
            raise ValueError('The response is not a Gmail dispatch acknowledgement')
        m, _ = manifest(data)
        draft = data['draft_verification']
        binding = binding_fields(m)
        _, _, digest_key = content_fields(m)
        digest = hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if (draft.get('status') != 'StoredReplyVerified' or draft.get('phase') != 'draft' or draft.get('issues')
                or draft.get('entity_id') != m['task_page_id'] or draft.get('content_version') != m['content_version']
                or draft.get('draft_id') != m['draft_id'] or draft.get('message_id') != m['message_id']
                or draft.get(digest_key) != m[digest_key] or draft.get('draft_binding_sha256') != digest
                or data['request'] != {'draft_id': m['draft_id']}):
            raise ValueError('Dispatch must use the exact current verified draft and its approved binding')
        if response.get('thread_id', response.get('threadId', m['thread_id'])) != m['thread_id']:
            raise ValueError('The original response identifies another thread')
        labels = response.get('label_ids', response.get('labelIds', [])) or []
        if 'DRAFT' in labels:
            raise ValueError('A draft save is not a successful dispatch response')
        raw_status = raw_status or ('Sent' if 'SENT' in labels else 'ProviderAccepted')
        entity, version, payload = m['task_page_id'], m['content_version'], m[digest_key]
        details = {'draft_id': m['draft_id'], 'thread_id': m['thread_id'], digest_key: payload}
    elif operation == 'sms':
        if raw_status == 'Sent':
            raise ValueError('Do not reinterpret an email status as an AndroidSync response')
        frozen, authority, request = data['notification'], data['authority'], data['request']
        payload = hashlib.sha256(frozen['body'].encode()).hexdigest()
        if (authority.get('status') != 'SMSNotificationVerified' or authority.get('issues')
                or authority.get('entity_id') != frozen['task_id']
                or authority.get('content_version') != frozen['content_version']
                or authority.get('body_sha256') != payload or frozen.get('body_sha256') != payload
                or set(request) != {'body', 'recipient', 'deviceId', 'idempotencyKey'}
                or request.get('body') != frozen['body'] or request.get('recipient') != frozen['recipient']
                or request.get('deviceId') != frozen['device_id'] or not request.get('idempotencyKey')):
            raise ValueError('Dispatch must match the frozen authorized SMS request')
        if raw_status is None:
            raise ValueError('Keep the actual AndroidSync acknowledgement status')
        entity, version = frozen['task_id'], frozen['content_version']
        details = {'device_id': frozen['device_id'], 'payload_sha256': payload}
    else:
        raise ValueError('This handoff contract covers Gmail email and AndroidSync SMS only')
    return {'status': 'ProviderHandoffVerified', 'phase': 'handoff', 'entity_id': entity,
            'content_version': version, 'operation': operation, 'message_id': identity,
            'provider_status': raw_status, 'handoff_complete': True, 'send_complete': True,
            'query_original_request': False, 'delivery_verification_required': False,
            'retry_send_allowed': False, **details,
            'scope': 'Original successful dispatch response and verified request binding only; '
                     'no provider re-query, network/delivery claim or permission to resend'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify',))
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.input == '-' else Path(args.input).read_text(encoding='utf-8')
        result = verify(json.loads(source))
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        result = {'status': 'NeedsCorrection', 'issues': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'ProviderHandoffVerified' else 2


if __name__ == '__main__':
    sys.exit(main())
