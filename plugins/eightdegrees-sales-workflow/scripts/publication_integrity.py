"""Validate the whole proposed page, retaining original review bindings; no I/O."""

import json
import re

from notion_checks import page_body, page_id
from workflow_checks import visible_markdown

SECTIONS = ({'current status', '\u5f53\u524d\u72b6\u6001'},
            {'processing result', '\u5904\u7406\u7ed3\u679c'},
            {'your input', '\u60a8\u7684\u8f93\u5165'})


def bindings(body):
    result = []
    for raw in re.findall(r'```json\s*\n(.*?)\n```', body, re.S):
        try:
            value = json.loads(raw)
        except ValueError:
            continue
        if isinstance(value, dict) and value.get('record_type') == 'action-binding':
            result.append(value)
    return result


def send_packages(body):
    result = []
    for raw in re.findall(r'```json\s*\n(.*?)\n```', body, re.S):
        try:
            value = json.loads(raw)
        except ValueError:
            continue
        if isinstance(value, dict) and value.get('record_type') == 'sales-send-package':
            result.append(value)
    return result


def require_source(package):
    try:
        valid = re.fullmatch(r'[a-f0-9]{32}', page_id(package.get('source_page_id', '')))
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise ValueError('New sales send package must retain its original source_page_id')


def proposed_body(target, args):
    body = page_body(target)
    command = args['command']
    if command == 'replace_content':
        return args['new_str']
    if command == 'insert_content':
        text = args['content']
        return text + '\n' + body if args.get('position', {}).get('type') == 'start' else body + '\n' + text
    if command == 'update_content':
        for edit in args['content_updates']:
            count = body.count(edit['old_str'])
            if count == 0 or count > 1 and not edit.get('replace_all_matches'):
                raise ValueError('Exact original mutation anchor is absent or ambiguous')
            body = body.replace(edit['old_str'], edit['new_str'], -1 if edit.get('replace_all_matches') else 1)
    return body


def check_body(body):
    headings = [m[1].strip().lower() for m in re.finditer(r'^## ([^\n]+)', visible_markdown(body), re.M)]
    for names in SECTIONS:
        if sum(h in names for h in headings) > 1:
            raise ValueError('Duplicate current status/result/input section; update the existing section')
    if len(bindings(body)) > 1:
        raise ValueError('One current action-binding is required; archive old bindings explicitly')


def check(data, review=None):
    call = data['call']; args = call['args']
    if call['tool'].endswith('__notion_notion_create_pages'):
        for page in args['pages']:
            check_body(page.get('content', ''))
            from consent_review import check_publication
            check_publication('', page.get('content', ''), page.get('properties', {}))
            for package in send_packages(page.get('content', '')):
                require_source(package)
        return
    if not call['tool'].endswith('__notion_notion_update_page'):
        return
    before = page_body(data['target'])
    after = proposed_body(data['target'], args)
    from consent_review import check_publication
    check_publication(before, after, args.get('properties', {}))
    def pins(body):
        values = []
        for raw in re.findall(r'```json\s*\n(.*?)\n```', body, re.S):
            try:
                value = json.loads(raw)
            except ValueError:
                continue
            if isinstance(value, dict) and value.get('record_type') == 'invocation-context-v1':
                values.append(value)
        return values
    old_pins, new_pins = pins(before), pins(after)
    if old_pins:
        if len(old_pins) != 1 or len(new_pins) != 1:
            raise ValueError('Preserve the single original invocation recovery pin')
        old_pin, new_pin = old_pins[0], new_pins[0]
        old_receipts = old_pin.get('receipt_page_ids', [])
        new_receipts = new_pin.get('receipt_page_ids', [])
        if (not isinstance(new_receipts, list) or new_receipts[:len(old_receipts)] != old_receipts
                or {k: v for k, v in old_pin.items() if k != 'receipt_page_ids'}
                != {k: v for k, v in new_pin.items() if k != 'receipt_page_ids'}):
            raise ValueError('Invocation command/identity/start/deadline are frozen; append receipt pointers only')
    for package in send_packages(after):
        if package not in send_packages(before):
            require_source(package)
    # Metadata-only writes must not turn legacy malformed copy into an unrelated
    # blocker. Content writes must leave one usable current view.
    if args['command'] != 'update_properties':
        check_body(after)
    old, new = bindings(before), bindings(after)
    if old and old != new:
        if len(old) != 1 or len(new) != 1:
            raise ValueError('Do not delete or duplicate the original action-binding during publication')
        prior, current = old[0], new[0]
        stable = ('TaskPageId', 'ActionPageId', 'OwnerSkill', 'ResumeStep', 'StepId', 'Mode', 'Category')
        ready = bool(review and review.get('status') == 'EmailReviewReady')
        if (review and review.get('status') == 'SingleEmailReviewPrepared'
                and review.get('package', {}).get('record_type') in {'email-review-v3', 'email-review-v4'}):
            from email_flow import validate
            validate(review['package'])
            ready = (current.get('ApprovalContract') == review['package']['record_type']
                     and page_id(current['ActionPageId']) == page_id(review['package']['action_page_id'])
                     and current.get('PackageSha256') == review['package']['package_sha256'])
            stable = tuple(k for k in stable if k != 'ActionPageId')
        if (any(prior.get(k) != current.get(k) for k in stable)
                or prior.get('ContentVersion') == current.get('ContentVersion')
                or not ready
                or review['task_page_id'] != page_id(current['TaskPageId'])
                or review['content_version'] != current['ContentVersion']
                or review['draft_binding_sha256'] != current.get('DraftBindingSha256')):
            raise ValueError('Current publication cannot replace the original review identity/payload binding')
        archives = []
        for raw in re.findall(r'```json\s*\n(.*?)\n```', after, re.S):
            try:
                value = json.loads(raw)
            except ValueError:
                continue
            if isinstance(value, dict) and value.get('record_type') == 'historical-action-binding':
                archives.append(value.get('binding'))
        if prior not in archives:
            raise ValueError('A separately verified new review version must retain its original binding history')
