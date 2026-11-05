"""Verify saved editable copy/preview/transport BEFORE exposing email review."""

import re

from email_presentation import blocks
from notion_checks import check_image_preview, check_preview, object_result, page_body, page_id
from reply_transport import manifest, verify
from workflow_checks import visible_markdown


def section(body, heading):
    headings = list(re.finditer(r'^## ([^\n]+)\n', visible_markdown(body), re.M))
    found = [m for m in headings if m[1] == heading]
    if len(found) != 1:
        raise ValueError('Expected one saved editable section: ' + heading)
    start = found[0].end()
    end = next((m.start() for m in headings if m.start() > start), len(body))
    return body[start:end]


def prepare(data):
    transport = data['transport']
    if transport.get('phase', 'draft') != 'draft':
        raise ValueError('Review needs a current unsent stored draft')
    m, html = manifest(transport)
    stored = verify(transport)
    if stored['status'] != 'StoredReplyVerified':
        raise ValueError('Stored draft verification failed: ' + '; '.join(stored['issues']))
    if 'publication_writes' in data:
        return acknowledged_publication(data, m, stored)
    copy_page = data['copy_page']
    original_copy = object_result(copy_page)
    if original_copy.get('metadata', {}).get('type') != 'page':
        raise ValueError('Use the original complete Notion editable-copy page fetch')
    binding = blocks(copy_page, 'email-review-copy-v1')[1]
    if (page_id(binding['task_page_id']) != page_id(m['task_page_id'])
            or binding['content_version'] != m['content_version'] or binding['html_sha256'] != m['html_sha256']):
        raise ValueError('Saved editable copy belongs to another task/version/package')
    body = page_body(copy_page)
    subject = section(body, data.get('subject_heading', 'Email subject')).strip('\n')
    if subject != m['subject']:
        raise ValueError('Saved editable subject differs from the stored draft')
    html_section = section(body, data.get('html_heading', 'Email HTML'))
    match = re.fullmatch(r'\n*```html\n(.*?)\n```\n*', html_section, re.S)
    if not match or match[1].encode() != html:
        raise ValueError('Saved editable HTML differs from exact frozen bytes; preserve trailing newlines inside the fence')
    preview = data['preview']
    if preview['input']['html_sha256'] != m['html_sha256']:
        raise ValueError('Preview represents another HTML package')
    if preview['kind'] == 'image':
        if preview['input']['content_version'] != m['content_version']:
            raise ValueError('Preview represents another review version')
        checked = check_image_preview(preview['input'])
        expected = 'SavedImageAndBytesMatch'
    elif preview['kind'] == 'html':
        checked, expected = check_preview(preview['input']), 'SavedEmbedAndBytesMatch'
    else:
        raise ValueError('Use a supported saved HTML or same-file native image preview')
    if checked['status'] != expected:
        raise ValueError('Saved preview verification failed')
    return {'status': 'EmailReviewReady', 'task_page_id': page_id(m['task_page_id']),
            'content_version': m['content_version'], 'html_sha256': m['html_sha256'],
            'draft_binding_sha256': stored['draft_binding_sha256'],
            'copy_page_id': page_id(original_copy['id']),
            'scope': 'Current saved copy/preview/draft agreement only; no human decision or send permission'}


def acknowledged_publication(data, manifest_data, stored):
    """Release a prepared review from successful copy/asset/preview writes.

    Render and inspect the local package before upload. These results confirm
    publication exists, not that stored bytes were read or compared.
    """
    from api_result import confirm
    preview, writes = data['preview'], data['publication_writes']
    source = preview['input']
    prepared_copy = data['prepared_copy']
    if any(prepared_copy.get(key) != manifest_data[key]
           for key in ('task_page_id', 'content_version', 'subject', 'html_sha256')):
        raise ValueError('Prepared editable copy belongs to another local package/version')
    if (preview['kind'] not in {'image', 'html'} or source['html_sha256'] != manifest_data['html_sha256']
            or source['content_version'] != manifest_data['content_version']):
        raise ValueError('Prepared preview belongs to another approved package/version')
    if preview['kind'] == 'image':
        render = source['render_manifest']
        if (render.get('completed') is not True or render.get('blocked_resources') != []
                or render.get('source_html_sha256') != manifest_data['html_sha256']
                or render.get('content_version') != manifest_data['content_version']
                or not render.get('preview_png_sha256') or not render.get('width') or not render.get('height')
                or render.get('renderer') != 'playwright-chromium' or render.get('javascript_enabled') is not False):
            raise ValueError('Complete same-version local render is required before upload')
    receipts = {}
    for role in ('copy', 'asset', 'preview'):
        receipts[role] = confirm({**writes[role], 'service': 'notion'})
        if receipts[role]['status'] != 'APIWriteConfirmed':
            raise ValueError('Review publication is unknown: ' + role)
    return {'status': 'EmailReviewReady', 'task_page_id': page_id(manifest_data['task_page_id']),
            'content_version': manifest_data['content_version'], 'html_sha256': manifest_data['html_sha256'],
            'draft_binding_sha256': stored['draft_binding_sha256'],
            'copy_page_id': page_id(receipts['copy']['record_id']),
            'preview_page_id': page_id(receipts['preview']['record_id']),
            'verification_basis': 'api-write-ack', 'stored_content_verified': False,
            'scope': 'Prepared version/render and copy/asset/preview API acknowledgements; no post-write byte comparison or human approval'}


def gate_mutation(data, texts):
    """A new email review binding/control cannot bypass copy verification.

    Existing operator submissions/closing controls remain ordinary mutations.
    Create an inert action first; controls activate only on its actual page ID.
    """
    args = data['call']['args']
    old_body = page_body(data['target']) if args.get('page_id') else ''
    def bindings(body):
        import json
        values = []
        for raw in re.findall(r'```json\s*\n(.*?)\n```', body, re.S):
            try: value = json.loads(raw)
            except ValueError: continue
            if (isinstance(value, dict) and value.get('record_type') == 'action-binding'
                    and value.get('ResumeStep', value.get('StepId')) in {'ReviewReplyDraft', 'SendApprovedReply', 'SendGeneralReply'}):
                values.append(value)
        return values
    old_bindings = bindings(old_body)
    new_bindings = bindings('\n'.join(texts))
    changed_binding = any(bound not in old_bindings for bound in new_bindings)
    controls = lambda text: set(re.findall(r'^\s*- \[[ xX]\] ([^\n]+)', visible_markdown(text), re.M))
    new_controls = controls('\n'.join(texts)) - controls(old_body)
    active = new_bindings or old_bindings
    if not active or not (new_controls or changed_binding and controls(old_body)):
        return None
    if not args.get('page_id') or len(active) != 1:
        raise ValueError('Create an inert email action first; activate one registered review on its actual page')
    bound = active[0]
    if page_id(bound['ActionPageId']) != page_id(args['page_id']):
        raise ValueError('Email review controls target another registered action')
    result = prepare(data['review_release'])
    if (result['task_page_id'] != page_id(bound['TaskPageId']) or result['content_version'] != bound['ContentVersion']
            or result['draft_binding_sha256'] != bound['DraftBindingSha256']):
        raise ValueError('Email review activation does not match verified draft task/version/binding')
    return result
