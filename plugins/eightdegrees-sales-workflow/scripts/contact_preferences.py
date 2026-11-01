#!/usr/bin/env python3
"""Publish a source-bound restrictive contact overlay without rewriting approval."""

import hashlib
import json
import re
from datetime import datetime
from email.utils import parseaddr
from html import unescape

from email_presentation import blocks, properties
from notion_checks import object_result, page_body, page_id
from workflow_checks import visible_markdown

HEADING = '## Current contact restrictions'


def stop_overlay(data):
    cycle = blocks(data['cycle_page'], 'sms-cycle-current-state')[1]
    package = blocks(data['send_task'], 'sales-send-package')[1]
    manifest = package['transport_manifest']
    message = object_result(data['message'])
    headers = {h['name'].casefold(): h['value'] for h in message['payload']['headers']}
    if (page_id(manifest['task_page_id']) != page_id(object_result(data['send_task'])['id'])
            or message.get('thread_id') != manifest['thread_id']
            or parseaddr(headers.get('from', ''))[1].casefold() != parseaddr(manifest['to'])[1].casefold()
            or parseaddr(headers.get('to', ''))[1].casefold() != parseaddr(manifest['from_address'])[1].casefold()
            or manifest['task_page_id'].replace('-', '') not in [str(v).replace('-', '') for v in
                        [blocks(data['cycle_page'], 'material-handoff-v1')[1]['email_task_id']]]):
        raise ValueError('Stop source must match the original enquiry email and parties')
    persona = blocks(data['persona_page'], 'approved-persona-snapshot')[1]
    if persona['client_id'] != cycle['location_id'] + ':' + cycle['contact_id']:
        raise ValueError('Persona belongs to another CRM customer')
    text = []
    def visit(part):
        body = (part.get('body') or {}).get('content')
        if isinstance(body, str):
            body = re.sub(r'<blockquote\b[^>]*>.*?</blockquote>', '', body, flags=re.I | re.S)
            body = re.sub(r'<div\b[^>]*class=["\x27][^"\x27]*(?:gmail_quote|yahoo_quoted)[^"\x27]*["\x27][^>]*>.*', '', body, flags=re.I | re.S)
            body = re.split(r'(?mi)^(?:On .+wrote:|[- ]*Original Message[- ]*)', body)[0]
            text.append(unescape(re.sub('<[^>]*>', ' ', '\n'.join(line for line in body.splitlines() if not line.lstrip().startswith('>')))))
        for child in part.get('parts') or []:
            visit(child)
    visit(message['payload'])
    quote = data['stop_quote']
    if (data.get('explicit_stop') is not True or not isinstance(quote, str) or not quote.strip()
            or ' '.join(quote.split()) not in ' '.join(' '.join(text).split())
            or not re.search(r'\bstop\b.*\b(?:sms|text)|\bdo not\b.*\b(?:sms|text)|\u505c\u6b62.*\u77ed\u4fe1', quote, re.I)
            or re.search(r"\b(?:don't|do not|not|never)\s+(?:want\s+to\s+)?stop\b", quote, re.I)):
        raise ValueError('Use a direct explicit current SMS stop quote; ambiguous scope stays blocked')
    if data.get('scope_confirmed') != 'current_enquiry' or not cycle.get('context_key'):
        raise ValueError('Do not guess global/channel/context scope')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', message['id']):
        raise ValueError('Use the immutable source message ID')
    at = datetime.fromisoformat(data['observed_at'].replace('Z', '+00:00'))
    if at.tzinfo is None:
        raise ValueError('Observation requires a timezone')
    event = {'event_id': hashlib.sha256((cycle['cycle_id'] + ':' + message['id']).encode()).hexdigest(),
             'source_message_id': message['id'], 'quote': quote, 'context_key': cycle['context_key'],
             'channel': 'sms', 'restriction': 'stop', 'observed_at': data['observed_at']}
    body = page_body(data['persona_page'])
    record = blocks(data['persona_page'], 'contact-restrictions-v1', required=False)
    if record:
        old, overlay = record
        if overlay['client_id'] != persona['client_id']:
            raise ValueError('Existing overlay belongs to another customer')
        events = list(overlay['events'])
    else:
        old, events = None, []
    matching = [v for v in events if v['event_id'] == event['event_id']]
    if matching:
        if any(matching[0].get(k) != event[k] for k in ('source_message_id', 'quote', 'context_key', 'channel', 'restriction')):
            raise ValueError('Previously saved stop evidence differs')
        return {'status': 'ContactRestrictionPlanned', 'updates': [], 'event': matching[0]}
    events.append(event)
    updated = {'record_type': 'contact-restrictions-v1', 'client_id': persona['client_id'],
               'rule': 'Restrictions override historical preferences; no automatic re-enable', 'events': events}
    new = '```json\n' + json.dumps(updated, ensure_ascii=False, indent=2) + '\n```'
    if old:
        if body.count(old) != 1:
            raise ValueError('Ambiguous restriction record')
        edit = {'old_str': old, 'new_str': new}
    else:
        # Insert before a unique owned heading, never match native children or
        # reserialize the approved snapshot to append a new restriction.
        if HEADING in visible_markdown(body):
            raise ValueError('Existing unbound restriction section needs reconciliation')
        headings = [h for h in ('## Current approved persona', '## \u5f53\u524d\u5df2\u5ba1\u6838\u753b\u50cf')
                    if re.search(r'(?m)^' + re.escape(h) + r'$', visible_markdown(body))]
        if len(headings) != 1 or body.count(headings[0]) != 1:
            raise ValueError('Need one exact approved-persona heading for safe insertion')
        edit = {'old_str': headings[0], 'new_str': HEADING + '\n\nLatest scoped restrictions override earlier approved contact preferences.\n\n' + new + '\n\n' + headings[0]}
    return {'status': 'ContactRestrictionPlanned', 'updates': [edit], 'event': event,
            'scope': 'Restrictive current display only; no approval, CRM DND change or re-enable'}


def dispatch_gate(data):
    cycle = data['cycle']
    overlay = data.get('restrictions') or {'events': []}
    if overlay.get('client_id', data['client_id']) != data['client_id']:
        raise ValueError('Restriction scope belongs to another client')
    stopped = any(v['restriction'] == 'stop' and v['channel'] == 'sms'
                  and v['context_key'] in {data['context_key'], '*'} for v in overlay['events'])
    blocked = stopped or cycle.get('stop') is True or cycle.get('manual_pause') is True
    return {'status': 'ContactDispatchChecked', 'blocked': blocked,
            'reason': 'Current scoped restriction overrides historical consent' if blocked else 'No restriction in supplied scope; remaining guards required',
            'send_authorized': False}


def verify(data):
    result = stop_overlay(data)
    original, saved = data['persona_page'], data['saved_persona_page']
    body = page_body(original)
    for edit in result['updates']:
        if body.count(edit['old_str']) != 1:
            raise ValueError('Ambiguous original persona anchor')
        body = body.replace(edit['old_str'], edit['new_str'], 1)
    identity = page_id(object_result(original)['id'])
    issues = []
    if (page_id(object_result(saved)['id']) != identity or properties(saved) != properties(original)
            or page_body(saved) != body):
        issues.append('Restriction or protected persona fields/content differ')
    task = page_id(data['maintenance_task_id'])
    if task == identity:
        raise ValueError('Maintenance task must not be the persona page')
    return {'status': 'NeedsCorrection' if issues else 'ContactRestrictionVerified', 'issues': issues,
            'entity_id': task, 'content_version': 'stop-' + result['event']['source_message_id'],
            'projection_page_ids': [identity], 'source_message_id': result['event']['source_message_id']}
