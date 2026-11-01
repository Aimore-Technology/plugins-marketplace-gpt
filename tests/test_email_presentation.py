"""Closed email results reconcile without reopening or replaying business work."""

import copy
import json
import unittest

from test_notion_checks import SCRIPTS
import email_presentation as PRESENTATION

SEND, ACTION, REVIEW, REVIEW_ACTION = (x * 32 for x in 'bcef')


def page(identity, body, props):
    return {'id': identity, 'metadata': {'type': 'page'},
            'text': '<properties>\n' + json.dumps(props) + '\n</properties>\n<content>\n' + body + '\n</content>'}


def block(value):
    return '```json\n' + json.dumps(value, indent=2) + '\n```'


def fixture(receipt=True):
    binding = lambda task, action: {'record_type': 'action-binding', 'TaskPageId': task,
                                   'ActionPageId': action, 'ContentVersion': 'test-v1'}
    package = {'record_type': 'sales-send-package', 'content_version': 'test-v1',
               'transport_manifest': {'task_page_id': SEND, 'content_version': 'test-v1', 'html_sha256': 'f' * 64,
                   'from_address': 'operator@example.com', 'to': 'buyer@example.com', 'thread_id': 'thread-1'},
               'content_approval': {'task_page_id': REVIEW, 'action_page_id': REVIEW_ACTION,
                                    'decision': 'Confirm', 'content_version': 'test-v1'}}
    proof = {'record_type': 'email-sent-proof', 'verification': {'status': 'StoredReplyVerified',
             'phase': 'sent', 'entity_id': SEND, 'content_version': 'test-v1', 'html_sha256': 'f' * 64,
             'message_id': 'sent-1'}, 'details': {'rfc_message_id': '<sent@example.com>'}}
    outcome = {'record_type': 'email-send-current-outcome', 'task_id': SEND, 'content_version': 'test-v1', 'message_id': 'sent-1', 'provider_status': 'Sent',
               'sent': True, 'reserved': False, 'human_received': False, 'provider_delivered': False}
    action = ('## Current status\n\nUnsent draft; waiting for send approval.\n\n'
              '## Approved content (history)\n\n```txt\nApproved original bytes\n```\n\n'
              '- [x] Original confirmed decision\n\n'
              '<image source="notion-file-block://original-image" />\n\n'
              '## Processing result\n\nNot yet sent.\n\n'
              '<mention url="https://app.notion.com/p/' + SEND + '" />')
    data = {'observed_at': '2026-11-01T08:00:00Z', 'language': 'en', 'pages': {
        'send_task': page(SEND, '\n\n'.join(map(block, [package, binding(SEND, ACTION), proof, outcome])),
                          {'State': 'Completed', 'StepId': 'SendApprovedReply', 'ResumeStep': 'SendApprovedReply', 'OwnerSkill': 'eightdegrees-sales-reply', 'ContentVersion': 'test-v1', 'Result': 'Old result'}),
        'review_task': page(REVIEW, block(binding(REVIEW, REVIEW_ACTION)),
                            {'State': 'Completed', 'StepId': 'ReviewReplyDraft', 'ResumeStep': 'ReviewReplyDraft', 'OwnerSkill': 'eightdegrees-sales-reply', 'ContentVersion': 'test-v1', 'Result': 'Unsent draft'}),
        'send_action': page(ACTION, action + '\n\n## Current email record\n\n' + block(outcome), {'title': 'Send result'}),
        'review_action': page(REVIEW_ACTION, 'Next: separate send approval <mention url="https://app.notion.com/p/' + ACTION + '" />\n\n' + action, {'title': 'Review result'})}}
    if receipt:
        data['receipt'] = {'explicit_confirmation': True, 'received_quote': 'I received the brochure.',
                          'message': {'id': 'reply-1', 'thread_id': 'thread-1', 'payload': {
                              'headers': [{'name': n, 'value': v} for n, v in
                                          [('From', 'Buyer <buyer@example.com>'), ('To', 'operator@example.com'),
                                           ('In-Reply-To', '<sent@example.com>')]],
                              'body': {'content': 'I received the brochure. Please stop SMS.'}}}}
    return data


def apply_plan(data):
    saved = copy.deepcopy(data['pages'])
    if data.get('index_page') is not None:
        saved['index'] = copy.deepcopy(data['index_page'])
    for update in PRESENTATION.plan(data)['updates']:
        capture = saved[update['role']]
        if update['command'] == 'update_content':
            for edit in update['content_updates']:
                capture['text'] = capture['text'].replace(edit['old_str'], edit['new_str'], 1)
        else:
            props = PRESENTATION.properties(capture)
            old = json.dumps(props)
            props.update(update['properties'])
            capture['text'] = capture['text'].replace(old, json.dumps(props), 1)
    return saved


class EmailPresentationTests(unittest.TestCase):
    def index_fixture(self, data, current=True):
        outcome = PRESENTATION.blocks(data['pages']['send_task'], 'email-send-current-outcome')[1]
        entry = {'send_task_page_id': SEND, 'content_version': 'test-v1', 'stop': True}
        if current: entry['current_outcome'] = outcome
        config = {'settings_schema_version': 1, 'sales_replies': {'other': {'state': 'new'}, 'reply': entry},
                  'sms_policy': {'enabled': False}, 'unrelated': 'Keep every original byte here.'}
        data['index_page'] = page('d' * 32, block(config), {'title': 'Dashboard'})
        return config

    def test_legacy_index_receipt_updates_only_the_original_nested_outcome(self):
        data = fixture(); config = self.index_fixture(data)
        saved = apply_plan(data)
        data['saved_index_page'] = saved.pop('index'); data['saved_pages'] = saved
        result = PRESENTATION.verify(data)
        self.assertEqual(result['status'], 'EmailPresentationVerified')
        self.assertEqual(len(result['projection_page_ids']), 5)
        body = PRESENTATION.page_body(data['saved_index_page'])
        updated = json.loads(body.split('```json\n')[1].split('\n```')[0])
        expected = copy.deepcopy(config)
        expected['sales_replies']['reply']['current_outcome'] = result['expected_outcome']
        self.assertEqual(updated, expected)
        repeat = data | {'pages': saved, 'index_page': data['saved_index_page']}
        self.assertEqual(PRESENTATION.plan(repeat)['updates'], [])

    def test_pointer_only_index_is_verified_without_synthesizing_outcome(self):
        data = fixture(); self.index_fixture(data, current=False)
        saved = apply_plan(data)
        self.assertEqual(saved.pop('index'), data['index_page'])
        self.assertFalse(any(x['role'] == 'index' for x in PRESENTATION.plan(data)['updates']))

    def test_index_different_message_and_unrelated_setting_change_fail_verification(self):
        data = fixture(); self.index_fixture(data)
        data['index_page']['text'] = data['index_page']['text'].replace('"message_id": "sent-1"', '"message_id": "other"')
        with self.assertRaises(ValueError): PRESENTATION.plan(data)
        data = fixture(); self.index_fixture(data)
        saved = apply_plan(data); data['saved_index_page'] = saved.pop('index')
        data['saved_pages'] = saved
        data['saved_index_page']['text'] = data['saved_index_page']['text'].replace('"enabled": false', '"enabled": true')
        self.assertEqual(PRESENTATION.verify(data)['status'], 'NeedsCorrection')

    def test_nested_settings_span_rejects_ambiguous_duplicate_keys(self):
        raw = '{"outer":{"key": {}, "key": {}}}'
        with self.assertRaises(ValueError): PRESENTATION.json_value_span(raw, ['outer', 'key'])

    def test_visible_navigation_and_action_json_use_the_same_new_receipt(self):
        data = fixture(); saved = apply_plan(data)
        record = PRESENTATION.blocks(saved['send_action'], 'email-send-current-outcome')[1]
        self.assertTrue(record['human_received'])
        self.assertFalse(record['provider_delivered'])
        self.assertNotIn('Next: separate send approval', saved['review_action']['text'])
        self.assertIn('Current email result <mention', saved['review_action']['text'])

    def test_actual_gmail_nullable_parts_and_body_are_handled(self):
        data = fixture(); payload = data['receipt']['message']['payload']
        payload['parts'] = None
        self.assertEqual(PRESENTATION.plan(data)['status'], 'EmailPresentationPlanned')
        payload['parts'] = [{'body': None, 'parts': None}]
        self.assertEqual(PRESENTATION.plan(data)['status'], 'EmailPresentationPlanned')

    def test_maintenance_task_is_distinct_and_does_not_reopen_completed_send(self):
        data = fixture(); data['maintenance_task_id'] = SEND
        with self.assertRaises(ValueError): PRESENTATION.plan(data)
        data['maintenance_task_id'] = 'a' * 32
        data['saved_pages'] = apply_plan(data)
        self.assertEqual(PRESENTATION.verify(data)['entity_id'], 'a' * 32)
        self.assertEqual(PRESENTATION.properties(data['saved_pages']['send_task'])['State'], 'Completed')

    def test_actual_linked_closed_pages_refresh_without_approval_or_provider_change(self):
        data = fixture(); before = copy.deepcopy(data)
        data['saved_pages'] = apply_plan(data)
        result = PRESENTATION.verify(data)
        self.assertEqual(result['status'], 'EmailPresentationVerified')
        self.assertTrue(result['expected_outcome']['human_received'])
        self.assertFalse(result['expected_outcome']['provider_delivered'])
        for role in ('send_task', 'review_task'):
            self.assertEqual(PRESENTATION.properties(data['saved_pages'][role])['State'], 'Completed')
        for role in ('send_action', 'review_action'):
            body = data['saved_pages'][role]['text']
            self.assertIn('Approved original bytes', body)
            self.assertIn('- [x] Original confirmed decision', body)
            self.assertIn('notion-file-block://original-image', body)
            self.assertNotIn('Unsent draft', body)
            self.assertIn('sent-1', body)
        self.assertEqual(before['pages'], data['pages'])

    def test_repeated_projection_has_no_writes_and_never_releases_stopped_work(self):
        data = fixture(); data['pages'] = apply_plan(data)
        result = PRESENTATION.plan(data)
        self.assertEqual(result['updates'], [])
        self.assertTrue(result['expected_outcome']['human_received'])
        del data['receipt']
        self.assertEqual(PRESENTATION.plan(data)['updates'], [])

    def test_projection_remains_compatible_with_existing_version_and_display_gates(self):
        from notion_checks import task_display
        data = fixture(); saved = apply_plan(data)
        for role, task_role in [('send_action', 'send_task'), ('review_action', 'review_task')]:
            task = PRESENTATION.properties(saved[task_role]) | {'PageId': saved[task_role]['id'],
                'ActionPageURL': 'https://app.notion.com/p/' + saved[role]['id']}
            self.assertEqual(task_display({'page': saved[role], 'task': task})['status'], 'DisplayConsistentForCheckedPatterns')

    def test_sent_without_receipt_updates_review_but_does_not_invent_receipt(self):
        data = fixture(False); data['saved_pages'] = apply_plan(data)
        result = PRESENTATION.verify(data)
        self.assertEqual(result['status'], 'EmailPresentationVerified')
        self.assertFalse(result['expected_outcome']['human_received'])

    def test_wrong_recipient_thread_or_parent_cannot_supply_receipt(self):
        for field, value in [('From', 'other@example.com'), ('To', 'other@example.com'),
                             ('In-Reply-To', '<other@example.com>')]:
            data = fixture()
            next(h for h in data['receipt']['message']['payload']['headers'] if h['name'] == field)['value'] = value
            with self.assertRaises(ValueError): PRESENTATION.plan(data)
        data = fixture(); data['receipt']['message']['thread_id'] = 'other'
        with self.assertRaises(ValueError): PRESENTATION.plan(data)

    def test_negative_generic_missing_or_invented_receipt_quote_is_not_confirmation(self):
        for text in ['Thanks.', "I haven't received the brochure.", '\u5c1a\u672a\u6536\u5230\u8d44\u6599。', 'I received another file.']:
            data = fixture(); data['receipt']['received_quote'] = text
            with self.assertRaises(ValueError): PRESENTATION.plan(data)

    def test_unfinished_review_changed_version_and_wrong_binding_stop_repair(self):
        for key, value in [('State', 'WaitingForOperator'), ('ContentVersion', 'old-version')]:
            data = fixture(); old = PRESENTATION.properties(data['pages']['review_task']); new = {**old, key: value}
            data['pages']['review_task']['text'] = data['pages']['review_task']['text'].replace(json.dumps(old), json.dumps(new))
            with self.assertRaises(ValueError): PRESENTATION.plan(data)
        data = fixture(); data['pages']['send_action']['id'] = 'a' * 32
        with self.assertRaises(ValueError): PRESENTATION.plan(data)

    def test_incomplete_error_layers_or_missing_sent_proof_are_not_hidden(self):
        for change in ({'truncated': True}, {'isError': True}, {'unknown_block_count': 1}):
            data = fixture(); data['pages']['send_task'].update(change)
            with self.assertRaises(ValueError): PRESENTATION.plan(data)
        data = fixture(); data['pages']['send_task']['text'] = data['pages']['send_task']['text'].replace('"phase": "sent"', '"phase": "draft"')
        with self.assertRaises(ValueError): PRESENTATION.plan(data)

    def test_protected_payload_input_state_and_provider_proof_cannot_be_repaired_away(self):
        for old, new, role in [('Approved original bytes', 'Changed bytes', 'review_action'),
                               ('[x] Original', '[ ] Original', 'review_action'),
                               ('"State": "Completed"', '"State": "InProgress"', 'send_task'),
                               ('<sent@example.com>', '<changed@example.com>', 'send_task')]:
            data = fixture(); data['saved_pages'] = apply_plan(data)
            data['saved_pages'][role]['text'] = data['saved_pages'][role]['text'].replace(old, new)
            self.assertEqual(PRESENTATION.verify(data)['status'], 'NeedsCorrection')


if __name__ == '__main__': unittest.main()
