"""Prospective release gates: no approval controls/calls before prerequisites."""

import copy
import hashlib
import json
import unittest

from test_notion_checks import page, preview, HTML
from test_reply_transport import fixture as transport_fixture
from test_sms_authority import inputs as sms_inputs, saved as saved_sms
from test_unattended import cycle_fixture
import dispatch_admission
import local_checks
import notion_mutation
import reply_transport
import review_release
import scan_cycle


def block(value):
    return '```json\n' + json.dumps(value) + '\n```'


def review():
    data = transport_fixture(HTML.encode())
    import base64
    data['manifest']['html_base64url'] = base64.urlsafe_b64encode(HTML.encode()).decode().rstrip('=')
    data['manifest']['html_sha256'] = hashlib.sha256(HTML.encode()).hexdigest()
    binding = {'record_type': 'email-review-copy-v1', 'task_page_id': data['manifest']['task_page_id'],
               'content_version': data['manifest']['content_version'], 'html_sha256': data['manifest']['html_sha256']}
    body = ('## Email subject\n\n' + data['manifest']['subject'] + '\n\n## Email HTML\n\n```html\n'
            + HTML + '\n```\n\n## Package\n\n' + block(binding))
    return {'transport': data, 'copy_page': page(body), 'preview': {'kind': 'html', 'input': preview()}}


def action():
    release = review()
    verified = reply_transport.verify(release['transport'])
    m = release['transport']['manifest']
    bound = {'record_type': 'action-binding', 'TaskPageId': m['task_page_id'], 'ActionPageId': 'a' * 32,
             'StepId': 'ReviewReplyDraft', 'ResumeStep': 'ReviewReplyDraft', 'ContentVersion': m['content_version'],
             'DraftBindingSha256': verified['draft_binding_sha256']}
    return {'call': {'tool': 'mcp__notion__notion_notion_update_page', 'args': {'page_id': 'a' * 32,
             'command': 'insert_content', 'content': '\n- [ ] Confirm content\n- [ ] Submit content decision'}},
            'target': page('Preparing review.\n\n' + block(bound)), 'review_release': release}


def dispatch(channel='email'):
    scan = cycle_fixture(); scan['policy'] = 'one-cycle-approved-work'
    transport = transport_fixture()
    result = {'scan': scan, 'channel': channel, 'run_page_id': 'b' * 32,
              'task_page_id': transport['manifest']['task_page_id'], 'transport': transport,
              'call': {'tool': 'mcp__gmail__send_draft', 'args': {'draft_id': transport['manifest']['draft_id']}}}
    scan['items'][0]['version'] = transport['manifest']['content_version']
    if channel == 'sms':
        sms = sms_inputs(); sms['saved_task'] = saved_sms(sms)
        scan['root_id'] = sms['authority']['root_id']
        result.update(notification=sms, task_page_id=sms['payload']['task_id'])
        scan['items'][0].update(step='SendNotificationSms', version=sms['payload']['content_version'])
        result['call'] = {'tool': 'mcp__androidsync__request_sms', 'args': {
            'body': sms['payload']['body'], 'recipient': sms['payload']['recipient'],
            'deviceId': sms['payload']['device_id'], 'idempotencyKey': 'one_original_request'}}
    result['work_key'] = scan_cycle.advance(scan)['work'][0]['key']
    return result


def ready(data):
    record = dispatch_admission.prepare(data)['record']
    data['saved_run'] = page(block(record)); data['saved_run']['id'] = data['run_page_id']
    data['now'] = '2026-11-01T00:01:10Z'
    data['current_scan'] = copy.deepcopy(data['scan']); data['current_scan']['now'] = data['now']
    return data


class ReviewOrder(unittest.TestCase):
    def test_actual_saved_copy_preview_and_draft_allow_control_activation(self):
        result = notion_mutation.prepare(action())
        self.assertEqual(result['status'], 'NotionMutationPrepared')
        self.assertEqual(result['checks'][-1]['result']['status'], 'EmailReviewReady')

    def test_missing_gate_changed_subject_html_or_missing_preview_returns_no_call(self):
        for change in ('missing', 'subject', 'html', 'preview'):
            data = action()
            if change == 'missing': del data['review_release']
            elif change == 'subject': data['review_release']['copy_page']['text'] = data['review_release']['copy_page']['text'].replace('Re: TEST inquiry', 'Changed subject')
            elif change == 'html': data['review_release']['copy_page']['text'] = data['review_release']['copy_page']['text'].replace(HTML, HTML.rstrip('\n'))
            else: data['review_release']['preview']['input']['page'] = page('Upload pending.')
            result = local_checks.run({'checks': [{'name': 'activate', 'operation': 'notion.mutation', 'input': data}]}, {})
            self.assertEqual(result['status'], 'NeedsCorrection', change)
            self.assertNotIn('call', result['checks'][0]['result'])

    def test_extra_newline_is_a_byte_change_not_silently_trimmed(self):
        data = review(); data['copy_page']['text'] = data['copy_page']['text'].replace(HTML, HTML + '\n')
        with self.assertRaises(ValueError): review_release.prepare(data)

    def test_inert_creation_and_human_checkbox_submit_do_not_require_reapproval(self):
        data = action(); data.pop('review_release')
        data['call']['args']['content'] = 'Preparing review; no controls.'
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')
        data['target']['text'] = data['target']['text'].replace('</content>', '\n- [ ] Confirm content\n- [ ] Submit content decision\n</content>')
        data['call']['args']['content'] = '- [x] Confirm content\n- [x] Submit content decision'
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')
        # A whole-page preservation patch includes the same binding. That is
        # neither a new review release nor permission to revalidate idle work.
        body = data['target']['text'].split('<content>\n')[1].split('\n</content>')[0]
        data['call']['args'] = {'page_id': 'a' * 32, 'command': 'replace_content',
                              'new_str': body.replace('- [ ]', '- [x]')}
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')

    def test_unverified_controls_cannot_be_published_in_first_create(self):
        data = action(); body = data['target']['text'].split('<content>')[1].split('</content>')[0]
        data['call']['tool'] = 'mcp__notion__notion_notion_create_pages'
        data['call']['args'] = {'creation_mode': 'draft', 'pages': [{'properties': {'title': 'Review'},
            'content': body + '\n- [ ] Submit content decision'}]}
        with self.assertRaises(ValueError): notion_mutation.prepare(data)

    def test_version_or_draft_binding_change_cannot_reuse_old_release(self):
        for field in ('ContentVersion', 'DraftBindingSha256', 'ActionPageId'):
            data = action(); data['target']['text'] = data['target']['text'].replace(
                json.dumps({'ContentVersion': 'reply-v2', 'DraftBindingSha256': reply_transport.verify(data['review_release']['transport'])['draft_binding_sha256'],
                            'ActionPageId': 'a' * 32}[field]), json.dumps('b' * 32))
            with self.assertRaises(ValueError): notion_mutation.prepare(data)


class DispatchOrder(unittest.TestCase):
    def test_admission_has_no_call_and_only_saved_current_admission_releases_exact_args(self):
        for channel in ('email', 'sms'):
            data = dispatch(channel)
            staged = dispatch_admission.prepare(data)
            self.assertNotIn('call', staged)
            released = dispatch_admission.release(ready(data))
            self.assertEqual(released['call'], data['call'])
            self.assertEqual(released['status'], 'DispatchArgumentsPrepared')

    def test_missing_or_different_saved_admission_cannot_be_repaired_retrospectively(self):
        data = ready(dispatch()); data['saved_run'] = page('No admission recorded before dispatch.')
        data['saved_run']['id'] = data['run_page_id']
        with self.assertRaises(ValueError): dispatch_admission.release(data)
        data = ready(dispatch()); data['saved_run']['id'] = 'c' * 32
        with self.assertRaises(ValueError): dispatch_admission.release(data)

    def test_sms_body_version_or_key_edit_requires_new_saved_admission(self):
        for field in ('body', 'key', 'version'):
            data = ready(dispatch('sms'))
            if field == 'key': data['call']['args']['idempotencyKey'] = 'new_safe_key'
            else:
                sms = data['notification']
                if field == 'body':
                    sms['payload']['body'] = 'Hi Alex, brochure submitted. Thanks, Ori'
                    data['call']['args']['body'] = sms['payload']['body']
                else:
                    sms['payload']['content_version'] = 'sms-v2'
                    data['scan']['items'][0]['version'] = 'sms-v2'
                    data['work_key'] = scan_cycle.key(data['scan']['items'][0])
                sms['saved_task'] = saved_sms(sms)
            with self.assertRaises(ValueError): dispatch_admission.release(data)

    def test_sms_connector_limits_are_checked_before_any_executable_request(self):
        for value in ('short', 'bad:key_with_colon', 'x' * 101):
            data = dispatch('sms'); data['call']['args']['idempotencyKey'] = value
            with self.assertRaises(ValueError): dispatch_admission.prepare(data)
        data = dispatch('sms'); data['notification']['payload']['body'] = 'x' * 71
        data['notification']['saved_task'] = saved_sms(data['notification'])
        data['call']['args']['body'] = 'x' * 71
        with self.assertRaises(ValueError): dispatch_admission.prepare(data)

    def test_new_stop_overlap_expiry_or_no_send_policy_blocks_release(self):
        for fault in ('stop', 'overlap', 'expiry', 'restricted', 'unknown'):
            data = ready(dispatch())
            if fault == 'stop': data['current_scan']['items'][0]['stopped'] = True
            elif fault == 'overlap': data['current_scan']['executor']['active_ids'].append('another-scan')
            elif fault == 'expiry':
                data['now'] = '2026-11-01T00:03:01Z'; data['current_scan']['now'] = data['now']
            elif fault == 'restricted': data['scan']['policy'] = 'one-cycle-no-customer-send'
            else: data['current_scan']['items'][0].update(unknown_attempt=True, attempt_id='original-unknown')
            with self.assertRaises(ValueError): dispatch_admission.release(data)

    def test_unknown_or_changed_owner_version_has_no_admission(self):
        for change in ('unknown', 'version', 'workkey'):
            data = dispatch()
            if change == 'unknown': data['scan']['items'][0].update(unknown_attempt=True, attempt_id='old-attempt')
            elif change == 'version': data['scan']['items'][0]['version'] = 'unreviewed-version'
            else: data['work_key'] = 'wrong-key'
            with self.assertRaises(ValueError): dispatch_admission.prepare(data)


if __name__ == '__main__': unittest.main()
