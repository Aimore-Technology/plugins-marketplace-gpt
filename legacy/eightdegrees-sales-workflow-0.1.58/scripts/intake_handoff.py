"""Require an original durable intake checkpoint before reply preparation; no I/O."""

import hashlib
import copy
import json
import re
from urllib.parse import unquote

from email_presentation import blocks, properties
from notion_checks import object_result, page_body, page_id
from runtime_records import read_identity


def source_key(capture):
    props = properties(capture)
    if props.get('MessageId'):
        account = props['Account']
        linked = re.fullmatch(r'\[([^\[\]]+)\]\(mailto:([^()]+)\)', account)
        if linked:
            if linked[1] != unquote(linked[2]):
                raise ValueError('Conflicting original account label/address')
            account = linked[1]
        if not re.fullmatch(r'[^\s<>\[\]():]+@[^\s<>\[\]():]+', account):
            raise ValueError('Use the exact original mail account')
        direction = props['Direction'].lower()
        if direction not in {'inbound', 'outbound'}:
            raise ValueError('Use the original message direction')
        return account + ':' + direction + ':' + props['MessageId']
    key = read_identity(props.get('SourceKey'))
    if not isinstance(key, str) or not key or re.search(r'[\\\n\r`*<>]|\[[^\]]*\]\(', key):
        raise ValueError('Source identity is unavailable; do not infer it from a title')
    return key


def plan(data):
    """Plan a prospective receipt after reading a persisted original source.

    The returned checkpoint is not saved evidence. Publish it on the current
    intake/scanner run, read it back, then verify; keep the old run unchanged.
    """
    from scan_cycle import key
    root = page_id(data['root_id'])
    source = object_result(data['source_page'])
    identity = source_key(data['source_page'])
    version = properties(data['source_page']).get('ContentVersion')
    if not version or not isinstance(data.get('invocation_id'), str) or not data['invocation_id'].strip():
        raise ValueError('Prospective intake needs the current source version/invocation')
    previous = blocks(data['checkpoint_page'], 'scan-checkpoint-v1')[1]
    if page_id(previous['root_id']) != root:
        raise ValueError('Checkpoint belongs to another installation')
    checkpoint = copy.deepcopy(previous)
    matching = [(k, v) for k, v in checkpoint['items'].items() if v.get('source_key') == identity
                and v.get('step') == 'ReadMessageBody' and v.get('version') == version]
    def refers_to_source(value):
        try:
            return page_id(value) == page_id(source['id'])
        except (ValueError, TypeError):
            return False
    unknown = any(v.get('state') == 'unknown' and (
        v.get('source_key') == identity and v.get('step') == 'ReadMessageBody'
        or refers_to_source(v.get('receipt_ref')))
        for v in checkpoint['items'].values())
    if len(matching) > 1 or unknown:
        raise ValueError('Reconcile ambiguous/unknown intake without consuming it')
    if not matching or matching[0][1].get('state') != 'completed':
        work = {'source_key': identity, 'step': 'ReadMessageBody', 'version': version,
                'input_digest': hashlib.sha256(page_body(data['source_page']).encode()).hexdigest()}
        if matching and matching[0][1].get('input_digest'):
            work['input_digest'] = matching[0][1]['input_digest']
        target = matching[0][0] if matching else key(work)
        checkpoint['items'][target] = dict(work, state='completed', receipt_ref=source['id'])
        checkpoint['invocation_id'] = data['invocation_id']
    candidate = copy.deepcopy(object_result(data['checkpoint_page']))
    old, _ = blocks(data['checkpoint_page'], 'scan-checkpoint-v1')
    candidate['text'] = candidate['text'].replace(old, '```json\n' + json.dumps(checkpoint) + '\n```', 1)
    # Validate the candidate with the same identity/root constraints, while
    # explicitly not claiming that this synthetic candidate was persisted.
    verify({'root_id': root, 'source_page': data['source_page'], 'checkpoint_page': candidate,
            'source_key': identity, 'source_version': version})
    return {'status': 'IntakeCheckpointPlanned', 'checkpoint': checkpoint,
            'source_key': identity, 'source_version': version, 'source_page_id': page_id(source['id']),
            'must_save_and_read_back': True,
            'scope': 'Prospective intake candidate only; no old-page rewrite, completed handoff proof or business effects'}


def verify(data):
    root = page_id(data['root_id'])
    source = object_result(data['source_page'])
    source_id = page_id(source['id'])
    if source.get('metadata', {}).get('type') != 'page':
        raise ValueError('Use the original complete source page')
    body = page_body(data['source_page'])
    ancestors = re.findall(r'<(?:parent-page|ancestor-\d+-page)\b[^>]*url="([^"]+)"', source['text'].split('<content>', 1)[0])
    if root not in {page_id(v) for v in ancestors}:
        raise ValueError('Source page is not in this installation')
    key = source_key(data['source_page'])
    if key != data['source_key'] or properties(data['source_page']).get('ContentVersion') != data['source_version']:
        raise ValueError('Original source key/version differs')
    if 'checkpoint_write' in data:
        from api_result import confirm
        receipt = confirm({**data['checkpoint_write'], 'service': 'notion',
                           'expected_id': data['checkpoint_page_id']})
        if receipt['status'] != 'APIWriteConfirmed':
            raise ValueError('Intake checkpoint write is unknown; recover its original attempt')
        checkpoint = data['checkpoint_record']
    else:
        checkpoint = blocks(data['checkpoint_page'], 'scan-checkpoint-v1')[1]
    if 'checkpoint_write' not in data and object_result(data['checkpoint_page']).get('metadata', {}).get('type') != 'page':
        raise ValueError('Use the original saved intake checkpoint page')
    if page_id(checkpoint['root_id']) != root or not checkpoint.get('invocation_id'):
        raise ValueError('Use the owning intake checkpoint in this installation')
    matches = [v for v in checkpoint['items'].values() if v.get('source_key') == key
               and v.get('step') == 'ReadMessageBody' and v.get('version') == data['source_version']]
    if len(matches) != 1 or matches[0].get('state') != 'completed':
        raise ValueError('Complete and read back intake checkpoint handoff before sales preparation')
    if page_id(matches[0].get('receipt_ref', '')) != source_id:
        raise ValueError('Intake receipt must identify the original source page')
    return {'status': 'IntakeHandoffVerified', 'root_id': root, 'source_page_id': source_id,
            'source_key': key, 'source_version': data['source_version'],
            'checkpoint_page_id': page_id(data['checkpoint_page_id'] if 'checkpoint_write' in data else object_result(data['checkpoint_page'])['id']),
            'verification_basis': 'api-write-ack' if 'checkpoint_write' in data else 'existing-record',
            'checkpoint_invocation_id': checkpoint['invocation_id'],
            'source_body_sha256': hashlib.sha256(body.encode()).hexdigest(),
            'checkpoint_sha256': hashlib.sha256(json.dumps(checkpoint, sort_keys=True,
                separators=(',', ':'), ensure_ascii=True).encode()).hexdigest(),
            'scope': 'Original source and durable completed intake only; no approval, send authority or historical order repair'}
