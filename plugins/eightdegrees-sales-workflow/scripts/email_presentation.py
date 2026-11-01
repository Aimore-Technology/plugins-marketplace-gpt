#!/usr/bin/env python3
"""Plan and verify email result-only patches from original captures; no I/O."""

import argparse
import copy
from datetime import datetime
from email.utils import parseaddr
from html import unescape
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id, task_display
from workflow_checks import visible_markdown

ROLES = ('send_task', 'send_action', 'review_task', 'review_action')


def blocks(capture, kind, required=True):
    values = []
    for match in re.finditer(r'```json\s*\n(.*?)\n```', page_body(capture), re.S):
        try:
            value = json.loads(match[1])
        except ValueError:
            continue
        if isinstance(value, dict) and (value.get('record_type') == kind or value.get('contract') == kind):
            values.append((match.group(), value))
    if not values and not required:
        return None
    if len(values) != 1:
        raise ValueError('Expected one original ' + kind)
    return values[0]


def properties(capture):
    page = object_result(capture)
    page_body(capture)
    if page.get('metadata', {}).get('type') != 'page':
        raise ValueError('Use complete original page captures')
    matches = re.findall(r'<properties>\s*(.*?)\s*</properties>', page['text'], re.S)
    if len(matches) != 1:
        raise ValueError('Missing original page properties')
    return json.loads(matches[0])


def current_patch(body, names, text):
    """Change only the plain prefix; preserve native links and controls below it."""
    headings = list(re.finditer(r'^## ([^\n]+)', visible_markdown(body), re.M))
    found = [m for m in headings if m[1].strip().lower() in names]
    if len(found) != 1:
        raise ValueError('Missing/duplicate current section')
    start = found[0].start()
    end = next((m.start() for m in headings if m.start() > start), len(body))
    section = body[start:end].rstrip()
    protected = re.search(r'(?m)^.*(?:<\w|^- \[[ xX]\]|^\s*```|^\s*~~~)', section)
    old = section[:protected.start()].rstrip() if protected else section
    if not old or body.count(old) != 1:
        raise ValueError('Current plain-text anchor is not unique')
    new = found[0].group() + '\n\n' + text
    return {'old_str': old, 'new_str': new} if old != new else None


def json_value_span(text, path):
    """Find a dictionary value's exact original span without reserializing settings."""
    decoder, start, end = json.JSONDecoder(), 0, len(text)
    for wanted in path:
        cursor = start
        while text[cursor].isspace(): cursor += 1
        if text[cursor] != '{': raise ValueError('Expected an original settings object')
        cursor += 1
        entries = {}
        while True:
            while text[cursor].isspace(): cursor += 1
            if text[cursor] == '}': break
            key, cursor = decoder.raw_decode(text, cursor)
            while text[cursor].isspace(): cursor += 1
            if text[cursor] != ':': raise ValueError('Malformed original settings')
            cursor += 1
            while text[cursor].isspace(): cursor += 1
            value_start = cursor
            _, cursor = decoder.raw_decode(text, cursor)
            if key in entries: raise ValueError('Ambiguous duplicate settings key')
            entries[key] = (value_start, cursor)
            while text[cursor].isspace(): cursor += 1
            if text[cursor] == ',': cursor += 1
        start, end = entries[wanted]
    return start, end


def index_patch(capture, send_id, version, outcome):
    body = page_body(capture)
    configs = []
    for match in re.finditer(r'```json\s*\n(.*?)\n```', body, re.S):
        try: value = json.loads(match[1])
        except ValueError: continue
        if isinstance(value, dict) and 'settings_schema_version' in value:
            configs.append((match[1], value))
    if len(configs) != 1: raise ValueError('Use the single original RunSettings capture')
    raw, config = configs[0]
    found = []
    for key, entry in config['sales_replies'].items():
        if not isinstance(entry, dict):
            continue
        target = entry.get('send_task_page_id', entry.get('task_page_id'))
        if target and page_id(target) == send_id and entry.get('content_version') == version:
            found.append((key, entry))
    if len(found) != 1: raise ValueError('The original source index must identify this send/version once')
    key, entry = found[0]
    current = entry.get('current_outcome')
    if current is None: return None  # Pointer-only indexes need no duplicate outcome update.
    if (not isinstance(current, dict) or current.get('message_id') != outcome['message_id']
            or current.get('provider_status') != outcome['provider_status']):
        raise ValueError('Source index identifies another outcome; reconcile instead of retargeting')
    updated = current | outcome
    if updated == current: return None
    start, end = json_value_span(raw, ['sales_replies', key, 'current_outcome'])
    old = raw[start:end]
    if body.count(old) != 1: raise ValueError('The exact source-index value is ambiguous')
    return {'role': 'index', 'command': 'update_content', 'content_updates': [
        {'old_str': old, 'new_str': json.dumps(updated, ensure_ascii=False, indent=2)}]}


def receipt_evidence(receipt, manifest, proof):
    """Bind an owner-selected explicit quote to an actual matching Gmail reply."""
    message = object_result(receipt['message'])
    headers = {h['name'].lower(): h['value'] for h in message['payload']['headers']}
    details = proof['details']
    if (parseaddr(headers.get('from', ''))[1].lower() != parseaddr(manifest['to'])[1].lower()
            or parseaddr(headers.get('to', ''))[1].lower() != parseaddr(manifest['from_address'])[1].lower()
            or message.get('thread_id') != manifest['thread_id']
            or details['rfc_message_id'] not in (headers.get('in-reply-to', '') + ' ' + headers.get('references', '')).split()):
        raise ValueError('Receipt reply must match the actual sent message, thread and parties')
    texts = []
    def visit(part):
        content = (part.get('body') or {}).get('content')
        if isinstance(content, str):
            texts.append(unescape(re.sub(r'<[^>]*>', ' ', content)))
        for child in part.get('parts') or []:
            visit(child)
    visit(message['payload'])
    quote = receipt['received_quote']
    if (receipt.get('explicit_confirmation') is not True or not isinstance(quote, str) or not quote.strip()
            or ' '.join(quote.split()) not in ' '.join(' '.join(texts).split())
            or not re.search(r'\breceived\b|\bgot\b|\u6536\u5230', quote, re.I)
            or re.search(r"\b(?:not|never|haven't|hasn't|hadn't)\b|\u672a\u6536\u5230|\u6ca1(?:\u6709)?\u6536\u5230|\u5c1a\u672a\u6536\u5230", quote, re.I)):
        raise ValueError('Use an explicit positive receipt quote from the observed reply, not an inference')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', message['id']):
        raise ValueError('Use the immutable provider message ID')
    return {'message_id': message['id'], 'quote': quote,
            'source_url': 'https://mail.google.com/mail/u/0/#inbox/' + message['id']}


def plan(data):
    pages = dict(data['pages'])
    if set(pages) != set(ROLES):
        raise ValueError('Capture exactly the send and linked content-review task/actions')
    if data.get('index_page') is not None:
        pages['index'] = data['index_page']
    props = {k: properties(v) for k, v in pages.items()}
    ids = {k: page_id(object_result(v)['id']) for k, v in pages.items()}
    if len(set(ids.values())) != len(ids):
        raise ValueError('Distinct related pages cannot alias')
    entity_id = page_id(data.get('maintenance_task_id', ids['send_task']))
    if 'maintenance_task_id' in data and entity_id in ids.values():
        raise ValueError('A maintenance task must not reopen or impersonate the original completed records')
    _, package = blocks(pages['send_task'], 'sales-send-package')
    manifest, approval = package['transport_manifest'], package['content_approval']
    version = package['content_version']
    if not isinstance(version, str) or not version or re.search(r'[\n\r`*<>\[\]]', version):
        raise ValueError('Use the exact single-line canonical content version')
    if (page_id(manifest['task_page_id']) != ids['send_task'] or manifest.get('content_version') != version
            or page_id(approval['task_page_id']) != ids['review_task']
            or page_id(approval['action_page_id']) != ids['review_action']
            or approval.get('decision') != 'Confirm' or approval.get('content_version') != version):
        raise ValueError('Related review must come from the original send package')
    for role, states, step in [('send_task', {'InProgress', 'Completed'}, 'SendApprovedReply'),
                               ('review_task', {'Completed'}, 'ReviewReplyDraft')]:
        p = props[role]
        if (p.get('State') not in states or p.get('ContentVersion') != version or p.get('StepId') != step
                or p.get('ResumeStep') != step or p.get('OwnerSkill') != 'eightdegrees-sales-reply'):
            raise ValueError('Only a verified sent email and its completed matching review may be refreshed')
        _, binding = blocks(pages[role], 'action-binding')
        action = 'send_action' if role == 'send_task' else 'review_action'
        if (page_id(binding['TaskPageId']) != ids[role] or page_id(binding['ActionPageId']) != ids[action]
                or binding['ContentVersion'] != version):
            raise ValueError('Original action binding differs')
    _, proof = blocks(pages['send_task'], 'email-sent-proof')
    verification = proof['verification']
    old_block, outcome = blocks(pages['send_task'], 'email-send-current-outcome')
    if (verification.get('status') != 'StoredReplyVerified' or verification.get('phase') != 'sent'
            or verification.get('issues') or page_id(verification['entity_id']) != ids['send_task']
            or verification.get('content_version') != version
            or verification.get('html_sha256') != manifest['html_sha256']
            or page_id(outcome['task_id']) != ids['send_task'] or outcome.get('content_version') != version
            or outcome.get('message_id') != verification['message_id'] or outcome.get('sent') is not True
            or outcome.get('provider_status') != 'Sent' or outcome.get('reserved') is not False
            or outcome.get('provider_delivered') is not False):
        raise ValueError('Reconcile the original verified Sent proof; presentation cannot prove or repeat sending')
    observed = datetime.fromisoformat(data['observed_at'].replace('Z', '+00:00'))
    if observed.tzinfo is None:
        raise ValueError('Observation time needs a timezone')
    new_outcome = copy.deepcopy(outcome)
    receipt = receipt_evidence(data['receipt'], manifest, proof) if data.get('receipt') else None
    if receipt:
        new_outcome.update(human_received=True, receipt_source_message_id=receipt['message_id'],
                           receipt_source_url=receipt['source_url'], receipt_quote=receipt['quote'])
    language = data.get('language', 'en')
    if language not in {'en', 'zh-CN'}:
        raise ValueError('Use the saved workspace language')
    message = outcome['message_id']
    text = 'Version: ' + version + '. ' + ('\u90ae\u4ef6\u5df2\u53d1\u9001' if language == 'zh-CN' else 'Email sent') + ' · Sent · ' + message + '.'
    if new_outcome.get('human_received') is True:
        text += ' ' + ('\u5ba2\u6237\u5df2\u786e\u8ba4\u6536\u5230。' if language == 'zh-CN' else 'Customer receipt confirmed.')
    text += ' ' + ('\u672c\u6b65\u65e0\u9700\u518d\u63d0\u4ea4；\u5176\u4ed6\u6e20\u9053\u89c1\u5176\u539f\u59cb\u7ed3\u679c。' if language == 'zh-CN' else 'No resubmission needed; other channels keep their own results.')
    if new_outcome != outcome:
        new_outcome['observed_at'] = data['observed_at']
    updates = []
    for role in ROLES:
        edits = []
        if role == 'send_task':
            # Labels outside immutable packages are current presentation, not
            # approved content. Match the complete version-bound heading only.
            body = page_body(pages[role])
            replacements = [
                ('## Current exact send package', '## Historical approved send package'),
                ('## \u5f53\u524d\u7cbe\u786e\u53d1\u9001\u5305', '## \u5386\u53f2\u6279\u51c6\u65f6\u53d1\u9001\u5305'),
            ]
            for old, new in replacements:
                anchor = old + ' \u00b7 ' + version
                if re.search(r'(?m)^' + re.escape(anchor) + r'$', visible_markdown(body)):
                    if body.count(anchor) != 1:
                        raise ValueError('Ambiguous historical package heading')
                    edits.append({'old_str': anchor, 'new_str': new + ' \u00b7 ' + version})
            for old, new in [
                ('No send decision has been accepted yet.', 'Historical approval snapshot; see the current sent result.'),
                ('\u5f53\u524d\u5c1a\u672a\u63a5\u53d7\u53d1\u9001\u51b3\u5b9a\u3002',
                 '\u5386\u53f2\u6279\u51c6\u5feb\u7167\uff1b\u5f53\u524d\u7ed3\u679c\u89c1\u5df2\u53d1\u9001\u8bb0\u5f55\u3002'),
            ]:
                if old in visible_markdown(body):
                    if body.count(old) != 1:
                        raise ValueError('Ambiguous historical approval label')
                    edits.append({'old_str': old, 'new_str': new})
        if role == 'send_task' and new_outcome != outcome:
            edits.append({'old_str': old_block, 'new_str': '```json\n' + json.dumps(new_outcome, ensure_ascii=False, indent=2) + '\n```'})
        if role.endswith('action'):
            body = page_body(pages[role])
            if role == 'send_action':
                record = blocks(pages[role], 'email-send-current-outcome', required=False)
                if record:
                    old_action_block, action_outcome = record
                    if (page_id(action_outcome['task_id']) != ids['send_task']
                            or action_outcome.get('content_version') != version
                            or action_outcome.get('message_id') != message):
                        raise ValueError('Action outcome belongs to another send/version')
                    updated_action = action_outcome | new_outcome
                    if updated_action != action_outcome:
                        edits.append({'old_str': old_action_block, 'new_str': '```json\n' + json.dumps(updated_action, ensure_ascii=False, indent=2) + '\n```'})
            else:
                # These are navigation/history labels, not approved content.
                prefix = body.split('## ', 1)[0]
                for old, new in [('\u4e0b\u4e00\u6b65\uff1a\u72ec\u7acb\u53d1\u9001\u6279\u51c6', '\u6700\u65b0\u90ae\u4ef6\u7ed3\u679c'),
                                 ('Next: separate send approval', 'Current email result')]:
                    if old in prefix and body.count(old) == 1:
                        edits.append({'old_str': old, 'new_str': new})
                for old, new in [('## \u5ba1\u6838\u6458\u8981', '## \u5ba1\u6838\u6458\u8981\uff08\u5386\u53f2\u5ba1\u6838\uff09'),
                                 ('## Review summary', '## Review summary (at approval)')]:
                    if re.search(r'(?m)^' + re.escape(old) + r'\s*$', body) and body.count(old) == 1:
                        edits.append({'old_str': old, 'new_str': new})
            for names in ({'current status', '\u5f53\u524d\u72b6\u6001'}, {'processing result', '\u5904\u7406\u7ed3\u679c'}):
                edit = current_patch(body, names, text)
                if edit:
                    edits.append(edit)
        if edits:
            updates.append({'role': role, 'command': 'update_content', 'content_updates': edits})
        if role.endswith('task') and props[role].get('Result') != text:
            updates.append({'role': role, 'command': 'update_properties', 'properties': {'Result': text}})
    if 'index' in pages:
        edit = index_patch(pages['index'], ids['send_task'], version, new_outcome)
        if edit: updates.append(edit)
    return {'status': 'EmailPresentationPlanned', 'entity_id': entity_id,
            'send_task_id': ids['send_task'], 'content_version': version, 'message_id': message,
            'projection_page_ids': list(ids.values()), 'page_ids': ids, 'updates': updates,
            'index_page_id': ids.get('index'),
            'expected_outcome': new_outcome, 'scope': 'Notion current results only; no state/approval/payload/provider/CRM change'}


def verify(data):
    expected = plan(data)
    saved = dict(data['saved_pages'])
    if set(saved) != set(ROLES):
        raise ValueError('Read back every affected original page')
    originals = dict(data['pages'])
    if 'index_page' in data:
        originals['index'] = data['index_page']
        saved['index'] = data['saved_index_page']
    issues = []
    for role in originals:
        body, props = page_body(originals[role]), properties(originals[role])
        for update in expected['updates']:
            if update['role'] != role:
                continue
            props.update(update.get('properties', {}))
            for edit in update.get('content_updates', []):
                if body.count(edit['old_str']) != 1:
                    raise ValueError('Planned exact anchor changed')
                body = body.replace(edit['old_str'], edit['new_str'], 1)
        if (page_id(object_result(saved[role])['id']) != expected['page_ids'][role]
                or properties(saved[role]) != props or page_body(saved[role]) != body):
            issues.append(role + ': saved current result or protected content/fields differ')
        if role.endswith('action'):
            task_role = 'send_task' if role == 'send_action' else 'review_task'
            task = properties(saved[task_role]) | {'PageId': expected['page_ids'][task_role],
                'ActionPageURL': 'https://app.notion.com/p/' + expected['page_ids'][role]}
            display = task_display({'page': saved[role], 'task': task})
            issues.extend(role + ': ' + issue['reason'] for issue in display['issues'])
    return {k: v for k, v in expected.items() if k not in {'updates', 'page_ids'}} | {
        'status': 'NeedsCorrection' if issues else 'EmailPresentationVerified', 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'verify'))
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == '-' else Path(args.input).read_text(encoding='utf-8')
        result = (plan if args.command == 'plan' else verify)(json.loads(raw))
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        result = {'status': 'NeedsCorrection', 'issues': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] in {'EmailPresentationPlanned', 'EmailPresentationVerified'} else 2


if __name__ == '__main__':
    sys.exit(main())
