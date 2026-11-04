"""Confirm an API write, not its stored content. No connector I/O or retries."""

import hashlib
import json
import re

from workflow_checks import inspect_result

SERVICES = {'notion', 'crm', 'gmail', 'androidsync', 'dropbox', 'calendar'}
CONTRACT = 'execution-api-v1'


def _layers(value):
    if not isinstance(value, dict):
        raise ValueError('Preserve the original API response object')
    yield value
    for key in ('structuredContent', 'result', 'data'):
        if isinstance(value.get(key), dict):
            yield from _layers(value[key])
    for block in value.get('content', []) or []:
        if isinstance(block, dict) and block.get('type') == 'text':
            try:
                parsed = json.loads(block['text'])
            except (ValueError, TypeError, KeyError):
                continue
            if isinstance(parsed, dict):
                yield from _layers(parsed)


def _identity(value):
    return value.replace('-', '').lower() if isinstance(value, str) and re.fullmatch(r'[0-9a-fA-F-]{32,36}', value) else value


def confirm(data):
    """Use the original write response, or scoped existence evidence if unknown.

    `entity_id` is the owning workflow page; `expected_id` is the actual API
    record for an update. Creates need a returned record ID. No content field is
    compared. A positive response never triggers a fetch or a resend.
    """
    service, response = data['service'], data['response']
    if service not in SERVICES:
        raise ValueError('Unsupported service')
    layers = list(_layers(response))
    failed = inspect_result(response)['status'] == 'Error' or any(
        inspect_result(layer)['status'] == 'Error' or layer.get('errors')
        or layer.get('status') in {'Failed', 'Error', 'Rejected', 'Timeout', 'Unknown'}
        for layer in layers)
    if any((type(layer.get('statusCode', layer.get('status'))) is int
                and 400 <= layer.get('statusCode', layer.get('status')) < 500
                and layer.get('statusCode', layer.get('status')) != 408)
               or layer.get('status') in {'Rejected', 'Denied'} for layer in layers):
        return {'status': 'NeedsReconciliation', 'retry_allowed': False,
                'reason': 'API explicitly refused this write; an existing record cannot turn refusal into completion'}
    basis = 'api-success'
    if failed or not any(_record_ids(layer) or _success(layer) for layer in layers):
        existence = data.get('existence_response')
        if existence is None:
            return {'status': 'NeedsReconciliation', 'retry_allowed': False,
                    'reason': 'Write failed or is unknown; check only whether the original record exists before any retry'}
        layers = list(_layers(existence))
        if inspect_result(existence)['status'] == 'Error' or any(
                inspect_result(layer)['status'] == 'Error' or layer.get('errors') for layer in layers):
            return {'status': 'NeedsReconciliation', 'retry_allowed': False,
                    'reason': 'Original-record existence is still unknown'}
        # A scoped ID/request marker is required to identify an uncertain create.
        if not data.get('expected_id'):
            raise ValueError('Resolve the original record ID by its saved request marker before confirming existence')
        basis = 'record-exists'
    identities = list(dict.fromkeys(identity for layer in layers for identity in _record_ids(layer)))
    expected = data.get('expected_id')
    if expected:
        matching = [identity for identity in identities if _identity(identity) == _identity(expected)]
        if matching:
            record = matching[0]
        elif not identities and basis == 'api-success' and any(_success(layer) for layer in layers):
            # Some update APIs return success/204 and no record body.
            record = expected
        else:
            return {'status': 'NeedsReconciliation', 'retry_allowed': False,
                    'reason': 'Response does not identify the original target record'}
    elif len(identities) == 1:
        record = identities[0]
    else:
        raise ValueError('Select the actual returned record ID for a batched create; do not guess an ID')
    if not isinstance(record, str) or not record.strip():
        raise ValueError('An actual record ID is required')
    return {'status': 'APIWriteConfirmed', 'service': service, 'record_id': record,
            'entity_id': data.get('entity_id', record), 'purpose': data.get('purpose', 'write'),
            'content_version': data.get('content_version'), 'verification_basis': basis,
            'request_sha256': hashlib.sha256(json.dumps(data.get('request', {}), sort_keys=True,
                separators=(',', ':'), allow_nan=False).encode()).hexdigest(),
            'retry_allowed': False, 'stored_content_verified': False,
            'scope': 'Write acknowledgement/existence only; no stored-body comparison, approval or send permission'}


def _success(layer):
    status = layer.get('statusCode', layer.get('http_status', layer.get('status')))
    return (inspect_result(layer)['status'] == 'Accepted' or layer.get('success') is True or layer.get('status') in {'success', 'Success', 'ok', 'OK', 'completed', 'Completed'}
            or type(status) is int and 200 <= status < 300)


def _record_ids(layer):
    # Only actual result records, not contact/location IDs inside a Note.
    values = [layer[key] for key in ('id', 'Id', 'page_id', 'note_id', 'noteId', 'draft_id', 'file_upload_id')
              if isinstance(layer.get(key), str) and layer[key].strip()]
    for key in ('pages', 'notes'):
        if isinstance(layer.get(key), list):
            values.extend(row['id'] for row in layer[key]
                          if isinstance(row, dict) and isinstance(row.get('id'), str) and row['id'].strip())
    for key in ('note', 'page', 'draft', 'file'):
        if isinstance(layer.get(key), dict):
            values.extend(_record_ids(layer[key]))
    return values


def requirements(resources, operation):
    """Generate receipt obligations for this phase, never future-step outcomes."""
    required = {}
    for resource in resources:
        role = resource['role']
        required[role + ':write'] = {'kind': 'api-write', 'entity_role': role,
                                    'service': 'notion', 'purpose': 'write'}
        if resource['type'] != 'task':
            continue
        step = resource['resume_step']
        required[role + ':route'] = {'kind': 'route', 'entity_role': role, 'resume_step': step}
        effects = []
        if step == 'ReviewReplyDraft' or 'reply-draft' in resource.get('evidence', []):
            effects.append(('gmail', 'reply-draft'))
        if (step in {'SyncApprovedPersona', 'RecordSendReceipt', 'RecordGeneralSendReceipt',
                     'SendApprovedReply', 'SendGeneralReply'}
                or step == 'ReviewCommunication' and operation in {'review', 'recovery'}):
            if resource.get('crm_recording') == 'pending-unmatched':
                if (step not in {'SendApprovedReply', 'SendGeneralReply'}
                        or resource.get('crm_match') != 'none' or resource.get('crm_search_complete') is not True
                        or not re.fullmatch(r'[a-fA-F0-9-]{32,36}', resource.get('crm_pending_task_id', ''))):
                    raise ValueError('Only an actual unmatched inquiry send may defer CRM to its registered recovery task')
                effects.append(('notion', 'crm-pending'))
            else:
                effects.append(('crm', 'crm-note'))
        if step in {'SendApprovedReply', 'RecordMaterialHandoff'}:
            effects.append(('notion', 'material-handoff'))
        if step == 'CreateConfirmedAppointment':
            effects.append(('calendar', 'appointment'))
        for service, purpose in effects:
            required[role + ':' + purpose] = {'kind': 'api-write', 'entity_role': role,
                                             'service': service, 'purpose': purpose,
                                             'content_version': resource['content_version']}
            if purpose == 'crm-pending':
                required[role + ':' + purpose]['expected_record_id'] = resource['crm_pending_task_id']
        if step in {'SendApprovedReply', 'SendGeneralReply', 'SendApprovedSms', 'SendNotificationSms'}:
            required[role + ':provider-handoff'] = {'kind': 'provider-handoff', 'entity_role': role}
        if step == 'SendNotificationSms':
            required[role + ':sms-authority'] = {'kind': 'sms-authority', 'entity_role': role}
    return required


def completion(data, registry):
    """Validate receipt coverage locally; no persisted content re-reading."""
    from notion_checks import completion_gate, page_id
    if data.get('required_checks') != registry.get('required_checks'):
        return {'status': 'Deferred', 'reason': 'Missing frozen receipt obligations'}
    resources = registry.get('api_resources', [])
    if not resources:
        return {'status': 'Deferred', 'reason': 'Original affected resources are missing'}
    resolved = {r['role']: r['entity_id'] for r in resources}
    expected = {name: {**{k: v for k, v in spec.items() if k != 'entity_role'},
                       'entity_id': resolved[spec['entity_role']]}
                for name, spec in requirements(resources, registry['operation']).items()}
    expected['execution-plan'] = {'kind': 'execution-plan',
        'entity_id': next(r['entity_id'] for r in resources if r['type'] == 'run'),
        'plan_sha256': registry['execution_plan_sha256']}
    if expected != data['required_checks']:
        return {'status': 'Deferred', 'reason': 'Current-phase receipt obligations were changed or omitted'}
    gate = completion_gate(data)
    if (gate['status'] != 'EligibleForCompletion'
            or data['invocation_id'] != registry.get('invocation_id')
            or data['publication_version'] != registry.get('publication_version')):
        return {'status': 'Deferred', 'reason': 'Missing/failed/stale write acknowledgements or pre-call checks'}
    versions = {_identity(key): value for key, value in registry.get('task_versions', {}).items()}
    dispatches, authorities = {}, {}
    for item in data['checks']:
        spec, result = data['required_checks'][item['name']], item['result']
        identity = page_id(spec['entity_id'])
        if identity in versions and spec['kind'] != 'api-write' and result.get('content_version') != versions[identity]:
            return {'status': 'Deferred', 'reason': 'Pre-call check belongs to another task version'}
        step = registry.get('task_steps', {}).get(identity)
        if spec['kind'] == 'provider-handoff':
            channel = 'email' if step in {'SendApprovedReply', 'SendGeneralReply'} else 'sms'
            if result.get('operation') != channel:
                return {'status': 'Deferred', 'reason': 'Dispatch acknowledgement belongs to another channel'}
            dispatches[identity] = result.get('payload_sha256', result.get('html_sha256'))
        if spec['kind'] == 'sms-authority':
            authorities[identity] = result.get('body_sha256')
        if spec['kind'] == 'route' and (result.get('owner') != registry['owner_skill'] or result.get('policy') != registry['policy']
                                      or result.get('resume_step') != step):
            return {'status': 'Deferred', 'reason': 'Pre-call route belongs to another owner/policy'}
    if any(not digest or digest != dispatches.get(identity) for identity, digest in authorities.items()):
        return {'status': 'Deferred', 'reason': 'SMS acknowledgement does not match the authorized submitted text'}
    return {'status': 'WithinOwnerScope', 'verification_basis': 'api-success-or-record-exists',
            'scope': 'Receipt coverage and pre-call bindings only; no stored-content comparison or business authorization'}
