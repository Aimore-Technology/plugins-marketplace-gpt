#!/usr/bin/env python3
"""Validate client requests and interpret host-managed Activepieces MCP results.

This module performs no network calls, reads no credentials and grants no business
approval. The host executes its returned MCP call once. A transport request ID
correlates asynchronous runs; it is not an idempotency key or send permission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, parse_qs
import uuid

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = json.loads((ROOT / 'references/commands.json').read_text())
RETIRED = {'start', 'stop', 'run-auto'}
ID = re.compile(r'^[A-Za-z0-9_-]{1,128}$')
PAGE = re.compile(r'^(?:[a-f0-9]{32}|[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})$', re.I)


class RequestError(ValueError):
    """An actionable client input error that must not dispatch a flow."""


def require(condition, message):
    if not condition:
        raise RequestError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def only(value, allowed, name):
    require(isinstance(value, dict), name + ' must be an object')
    require(not set(value) - set(allowed), name + ' contains unsupported fields')


def capture(value):
    """Unwrap an MCP structured result without treating a status sentence as JSON."""
    if not isinstance(value, dict):
        return value
    if 'structuredContent' in value:
        return value['structuredContent']
    if 'content' in value:
        for block in value['content']:
            if block.get('type') != 'text':
                continue
            body = block.get('text', '')
            for position, char in enumerate(body):
                if char not in '{[':
                    continue
                try:
                    result, _ = json.JSONDecoder().raw_decode(body[position:])
                    return result
                except json.JSONDecodeError:
                    pass
        return {}
    return value


def discover(data):
    """Bind exactly named, enabled callable flows to their actual external IDs."""
    listed = capture(data['flows']).get('flows', [])
    choices = capture(data['options']).get('options', [])
    bindings = {}
    for command in COMMANDS:
        prefix = 'EightDegrees \u00b7 ' + command + ' \u00b7 '
        matches = [flow for flow in listed if flow.get('displayName', '').startswith(prefix)]
        require(len(matches) == 1, 'Missing or ambiguous flow: ' + command)
        flow = matches[0]
        require(flow.get('status') == 'ENABLED' and flow.get('published') is True,
                'Flow is not published and enabled: ' + command)
        require(flow.get('triggerType') == '@activepieces/piece-subflows', 'Flow must be callable: ' + command)
        options = [option for option in choices if option.get('label') == flow['displayName']]
        require(len(options) == 1 and ID.fullmatch(str(options[0].get('value', ''))),
                'Missing or ambiguous callable external ID: ' + command)
        bindings[command] = dict(internalId=flow['id'], externalId=options[0]['value'], name=flow['displayName'])
    require(len({binding['externalId'] for binding in bindings.values()}) == len(COMMANDS), 'Duplicate flow binding')
    return {'status': 'BindingsReady', 'bindings': bindings}


def workspace(value):
    """Read only the registered workspace control row supplied by the host."""
    result = capture(value or {})
    rows = result.get('records', [])
    require(len(rows) == 1, 'Read the unique workspace row in EightDegrees RunSettings first')
    record = rows[0]
    fields = {cell.get('fieldName', key) if isinstance(cell, dict) else key:
              cell.get('value') if isinstance(cell, dict) and 'value' in cell else cell
              for key, cell in record.get('cells', {}).items()}
    require(fields.get('Key') == 'workspace', 'Wrong workspace control row')
    raw = fields.get('ConfigJSON', '{}')
    try:
        config = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError as exc:
        raise RequestError('Workspace configuration is invalid') from exc
    require(isinstance(config, dict), 'Workspace configuration must be an object')
    return fields.get('Initialized') in (True, 'true'), config


def valid_email(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', value))


def valid_path(path, roots):
    return text(path) and '..' not in path and any(isinstance(root, str) and root.startswith('/')
        and (path == root or path.startswith(root.rstrip('/') + '/')) for root in roots)


def validate_init(payload, saved):
    only(payload, ['workspaceLanguage', 'operator', 'gmail', 'dropboxRoots', 'projects',
                   'crmLocationId'], 'init payload')
    merged = {**saved, **payload}
    require(merged.get('workspaceLanguage') in ('zh-CN', 'en'), 'Choose workspaceLanguage explicitly: zh-CN or en')
    operator = merged.get('operator', {})
    only(operator, ['email', 'name', 'crmUserId'], 'operator')
    require(valid_email(operator.get('email')) and text(operator.get('name'))
            and text(operator.get('crmUserId')), 'Provide actual operator email, name and CRM user ID')
    require(text(merged.get('crmLocationId')), 'Provide actual CRM location ID')
    mail = dict(merged.get('gmail', {}))
    only(mail, ['scope', 'afterDate', 'to', 'label'], 'gmail')
    require(mail.get('scope', 'all-new') == 'all-new', 'Gmail scope must be all-new')
    from datetime import datetime, timezone
    mail = {'scope': 'all-new', 'afterDate': mail.get('afterDate') or datetime.now(timezone.utc).isoformat()}
    try:
        instant = datetime.fromisoformat(str(mail.get('afterDate', '')).replace('Z', '+00:00'))
        require(instant.tzinfo is not None, 'gmail.afterDate needs an explicit timezone')
    except ValueError as exc:
        raise RequestError('Provide gmail.afterDate as an ISO timestamp with timezone') from exc
    roots = merged.get('dropboxRoots', [])
    require(isinstance(roots, list) and roots and all(text(root) and root.startswith('/')
            and '..' not in root for root in roots), 'Provide authorized Dropbox roots')
    projects = merged.get('projects', {})
    require(isinstance(projects, dict) and projects, 'Provide the authorized project catalog')
    for key, project in projects.items():
        only(project, ['materialPath', 'revision', 'lots'], 'project')
        require(text(key) and valid_path(project.get('materialPath'), roots), 'Project material path is outside authorized roots')
        require(isinstance(project.get('lots', []), list) and all(text(lot) for lot in project.get('lots', [])), 'Project lots must be strings')
    return {**payload, 'gmail': mail}


def validate_source(payload, command, config):
    only(payload, ['source'] if command == 'add-communication' else ['source', 'projectKey', 'lot'], 'payload')
    source = payload.get('source', {})
    only(source, ['text', 'email', 'phone', 'messageId', 'filePath', 'sourceUrl', 'communicationId',
                  'communicationTime', 'sourceKey', 'name', 'subject'], 'source')
    require(all(isinstance(value, str) for value in source.values()), 'Source fields must be strings')
    require(any(text(source.get(key)) for key in ['text', 'messageId', 'filePath']), 'Provide text, a Gmail message ID or a Dropbox path')
    require(not (source.get('filePath') and (source.get('text') or source.get('messageId'))), 'Choose one source: file or email/text')
    if source.get('messageId'):
        require(bool(ID.fullmatch(source['messageId'])), 'Use the actual Gmail message ID; a thread URL is not a message ID')
    if source.get('filePath'):
        require(command == 'add-communication' and valid_path(source['filePath'], config.get('dropboxRoots', [])),
                'Dropbox file is outside the authorized scope')
    if source.get('email'):
        require(valid_email(source['email']), 'Provide a plain email address')
    if source.get('phone'):
        require(bool(re.fullmatch(r'\+[1-9][0-9]{7,14}', source['phone'])), 'Provide phone in its verified E.164 format')
    if command == 'add-communication' and not source.get('messageId'):
        require(source.get('email') or source.get('phone'), 'Provide the customer email or verified phone')
    if source.get('sourceUrl'):
        parsed = urlsplit(source['sourceUrl'])
        require(parsed.scheme in ('http', 'https') and parsed.hostname and not parsed.username and not parsed.password,
                'Source URL must be an HTTP(S) provenance link without credentials')
    if command == 'reply-draft':
        require(source.get('messageId'), 'Reply drafts require the actual original Gmail message ID')
        project = config.get('projects', {}).get(payload.get('projectKey'))
        require(isinstance(project, dict), 'Choose an exact projectKey from the saved catalog')
        lot = payload.get('lot', '')
        require(isinstance(lot, str) and (not project.get('lots') or lot in project['lots']), 'Choose the exact registered lot')
    return payload


def plan(data):
    """Produce one allowlisted asynchronous MCP dispatch after validating inputs."""
    command = data.get('command')
    require(command in COMMANDS, 'Supported commands: ' + ', '.join(COMMANDS))
    binding = data.get('bindings', {}).get(command, {})
    require(all(ID.fullmatch(str(binding.get(key, ''))) for key in ['internalId', 'externalId']), 'Resolve current flow bindings first')
    require(binding.get('name', '').startswith('EightDegrees \u00b7 ' + command + ' \u00b7 '), 'Flow binding does not match the requested command')
    payload = data.get('payload', {})
    initialized, config = workspace(data.get('settings'))
    if command == 'init':
        payload = validate_init(payload, config)
    elif command == 'report':
        only(payload, [], 'report payload')
    else:
        require(initialized, 'Complete init before submitting business work')
        payload = validate_source(payload, command, config)
    request_id = str(uuid.UUID(data['requestId'])) if data.get('requestId') else str(uuid.uuid4())
    digest = hashlib.sha256(json.dumps({'command': command, 'payload': payload}, sort_keys=True,
                                    ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    args = {'pieceName': '@activepieces/piece-subflows', 'actionName': 'callFlow', 'input': {
        'flowId': binding['externalId'], 'mode': 'advanced',
        'flowProps': {'payload': {**payload, '_clientRequestId': request_id}}, 'waitForResponse': False}}
    return {'status': 'Ready', 'command': command, 'requestId': request_id, 'inputDigest': digest,
            'binding': binding, 'tool': {'name': 'ap_run_action', 'arguments': args}, 'automaticRetry': False}


def candidates(data):
    """Select a bounded set of newly created runs, never an older latest run."""
    request = data['plan']
    created_after = data['createdAfter']
    runs = capture(data['runs']).get('runs', [])
    matches = [run for run in runs if run.get('flowId') == request['binding']['internalId']
               and run.get('environment') == 'PRODUCTION' and run.get('created', '') >= created_after]
    return {'status': 'Lookup', 'runIds': [run['id'] for run in matches[:3]], 'automaticRetry': False}


def observe(data):
    """Display only the run matching both the bound flow and transport request ID."""
    request = data['plan']
    run = capture(data['run'])
    require(run.get('flowId') == request['binding']['internalId'], 'Run belongs to a different flow')
    trigger = next((step.get('output', {}) for step in run.get('steps', []) if step.get('name') == 'trigger'), {})
    payload = trigger.get('data', trigger) if isinstance(trigger, dict) else {}
    require(payload.get('_clientRequestId') == request['requestId'], 'Run belongs to a different request')
    result = {'command': request['command'], 'requestId': request['requestId'], 'flowRunId': run['id'], 'automaticRetry': False}
    if run.get('status') in ('QUEUED', 'RUNNING', 'PAUSED'):
        return {**result, 'status': 'InProgress'}
    if run.get('status') != 'SUCCEEDED':
        return {**result, 'status': 'Failed', 'failedStep': run.get('failedStepName')}
    response = next((step.get('output') for step in reversed(run.get('steps', []))
                     if isinstance(step.get('output'), dict) and step['output'].get('status') in
                     ('review_required', 'report_ready', 'initialization_result')), None)
    require(response is not None, 'Completed run has no verified business response')
    if request['command'] == 'init':
        require(response['status'] == 'initialization_result', 'Unexpected init response')
        ready = response.get('initialized') in (True, 'true')
        return {**result, 'status': 'Initialized' if ready else 'NeedsSetup', 'missing': response.get('missing', [])}
    if request['command'] == 'report':
        require(response['status'] == 'report_ready' and text(response.get('reportText')), 'Missing report result')
        result.update(status='ReportReady', reportText=response['reportText'])
    else:
        review_id = response.get('reviewId')
        require(response['status'] == 'review_required' and bool(ID.fullmatch(str(review_id))), 'Missing actual workbench review ID')
        url = response.get('reviewUrl', '')
        parsed = urlsplit(url)
        require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
                and parsed.path == '/portal/tasks' and parse_qs(parsed.query).get('task') == [review_id],
                'Missing verified workbench review URL')
        result.update(status='ReviewRequired', taskId=review_id, resultUrl=url)
    return result


def run(operation, data):
    """Return bounded client status; invalid inputs never contain an executable call."""
    try:
        return {'discover': discover, 'plan': plan, 'candidates': candidates, 'observe': observe}[operation](data)
    except (RequestError, KeyError, TypeError, ValueError) as exc:
        return {'status': 'NeedsInput', 'message': str(exc), 'automaticRetry': False}


def main():
    """Read a request from stdin or a caller-owned JSON file; never log its content."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['discover', 'plan', 'candidates', 'observe'])
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    try:
        source = args.input.read_text() if args.input else sys.stdin.read()
        require(len(source.encode()) <= 2_000_000, 'Input capture exceeds 2 MB')
        result = run(args.operation, json.loads(source))
    except (OSError, ValueError) as exc:
        result = {'status': 'NeedsInput', 'message': str(exc), 'automaticRetry': False}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] != 'NeedsInput' else 2


if __name__ == '__main__':
    raise SystemExit(main())
