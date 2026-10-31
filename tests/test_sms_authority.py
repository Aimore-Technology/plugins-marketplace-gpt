"""Standing notification permission never requires a per-message approval."""

import copy
import json
import unittest

from test_notion_checks import page, REPORT
import sms_authority as SMS


def inputs():
    authority = {'policy': 'notification-sms-v1', 'enabled': True,
                 'per_message_review_required': False, 'revoked_at': None,
                 'allowed_intents': sorted(SMS.INTENTS), 'root_id': 'f'*32,
                 'operator_id': 'configured-operator', 'sender_number': '+61400000001',
                 'device_id': 'actual-device', 'operator_sms_number': '+61400000002'}
    payload = {'root_id': authority['root_id'], 'operator_id': authority['operator_id'],
               'task_id': REPORT, 'content_version': 'sms-v1', 'intent': 'material_receipt',
               'recipient_role': 'customer', 'recipient': '+61400000003',
               'sender_number': authority['sender_number'], 'device_id': authority['device_id'],
               'body': 'Hi Alex, the brochure email has been sent. Thanks, Ori',
               'source_refs': ['actual-material-message-id'], 'facts_verified': True}
    return {'authority': authority, 'payload': payload, 'invocation_policy': 'one-cycle-approved-work'}


def saved(data):
    return page('```json\n' + json.dumps(SMS.prepare(data)['record']) + '\n```')


class SMSAuthorityTests(unittest.TestCase):
    def test_current_standing_permission_and_saved_exact_body_need_no_human_decision(self):
        data = inputs(); before = copy.deepcopy(data)
        result = SMS.prepare(data)
        self.assertFalse(result['record']['requires_human_review'])
        self.assertEqual(data, before)
        self.assertNotIn('Decision', result['record'])
        data['saved_task'] = saved(data)
        data['dispatch'] = {k: data['payload'][k] for k in ('recipient','device_id','body')}
        self.assertEqual(SMS.verify(data)['status'], 'SMSNotificationVerified')

    def test_disable_revocation_or_wrong_policy_blocks_existing_notification(self):
        for change in ({'enabled': False}, {'revoked_at': '2026-11-01T00:00:00Z'},
                       {'policy': 'unknown'}, {'per_message_review_required': True}):
            data = inputs(); data['saved_task'] = saved(data); data['authority'].update(change)
            with self.assertRaises(ValueError): SMS.verify(data)

    def test_other_operator_root_sender_or_device_does_not_inherit_authority(self):
        for field in ('operator_id','root_id','sender_number','device_id'):
            data = inputs(); data['payload'][field] = 'another-identity'
            with self.assertRaises(ValueError): SMS.prepare(data)

    def test_report_draft_setup_and_explicit_no_send_invocations_remain_restricted(self):
        for policy in ('report-only','draft-only','setup-only','scheduling-only','one-cycle-no-customer-send'):
            data = inputs(); data['invocation_policy'] = policy
            with self.assertRaises(ValueError): SMS.prepare(data)

    def test_offer_or_unverified_notification_fact_is_not_covered(self):
        for change in ({'intent': 'price_offer'}, {'facts_verified': False}, {'source_refs': []}, {'source_refs': [None]}):
            data = inputs(); data['payload'].update(change)
            with self.assertRaises(ValueError): SMS.prepare(data)

    def test_operator_alert_cannot_be_redirected_to_a_customer(self):
        data = inputs(); data['payload'].update(intent='operator_alert', recipient_role='operator')
        with self.assertRaises(ValueError): SMS.prepare(data)
        data['payload']['recipient'] = data['authority']['operator_sms_number']
        self.assertEqual(SMS.prepare(data)['status'], 'SMSNotificationPrepared')

    def test_edited_notification_needs_fresh_freeze_but_no_human_review(self):
        data = inputs(); data['saved_task'] = saved(data)
        data['payload'].update(body='Hi Alex, your brochure email is ready. Thanks, Ori', content_version='sms-v2')
        with self.assertRaises(ValueError): SMS.verify(data)
        data['saved_task'] = saved(data)
        self.assertEqual(SMS.verify(data)['status'], 'SMSNotificationVerified')

    def test_body_target_or_device_cannot_change_in_actual_dispatch(self):
        for field in ('body','recipient','device_id'):
            data = inputs(); data['saved_task'] = saved(data)
            data['dispatch'] = {k: data['payload'][k] for k in ('recipient','device_id','body')}
            data['dispatch'][field] = 'changed-value'
            with self.assertRaises(ValueError): SMS.verify(data)

    def test_missing_wrong_or_incomplete_saved_task_does_not_pass(self):
        data = inputs(); data['saved_task'] = saved(data)
        for change in ({'id': 'd'*32}, {'truncated': True}):
            bad = copy.deepcopy(data); bad['saved_task'].update(change)
            with self.assertRaises(ValueError): SMS.verify(bad)

    def test_duplicate_current_frozen_payloads_do_not_pass(self):
        data = inputs(); data['saved_task'] = saved(data)
        data['saved_task']['text'] = data['saved_task']['text'].replace('</content>', data['saved_task']['text'] + '\n</content>')
        with self.assertRaises(ValueError): SMS.verify(data)
