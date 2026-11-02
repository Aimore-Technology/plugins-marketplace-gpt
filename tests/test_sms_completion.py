"""Network submission finishes SMS sending without an unavailable handset signal."""
import copy
import unittest

from test_scheduled_outcomes import outcome
from test_unattended import sms_fixture, saved_sms
import email_presentation
import local_checks
import operator_experience
import outcome_checks
import sms_presentation


class SMSCompletion(unittest.TestCase):
    def test_network_and_optional_delivery_finish_without_receipt_or_more_polling(self):
        for status in ('SentToNetwork', 'Delivered'):
            data = outcome('sms', status)
            result = outcome_checks.sms_progress(data)
            self.assertTrue(result['send_complete'])
            self.assertFalse(result['query_original_request'])
            self.assertFalse(result['requires_handset_confirmation'])
            self.assertFalse(result['retry_send_allowed'])
            self.assertEqual(result['message_id'], data['provider']['message_id'])

    def test_unknown_handoff_keeps_reservation_without_automatic_polling(self):
        for status in ('Unknown',):
            data = outcome('sms', status)
            result = outcome_checks.sms_progress(data)
            self.assertFalse(result['send_complete'])
            self.assertFalse(result['query_original_request'])
            self.assertFalse(result['retry_send_allowed'])
            self.assertTrue(outcome_checks.projection(data)['expected']['reserved'])
            self.assertEqual(result['needs_reconciliation'], status == 'Unknown')

    def test_failed_is_not_sent_and_never_automatically_retries(self):
        result = outcome_checks.sms_progress(outcome('sms', 'Failed'))
        self.assertFalse(result['send_complete'])
        self.assertFalse(result['query_original_request'])
        self.assertFalse(result['retry_send_allowed'])

    def test_native_pending_status_is_preserved_after_accepted_handoff(self):
        event = outcome('sms', 'PendingApproval') | {'account': 'configured-device'}
        row = operator_experience.result_summary({'events': [event], 'coverage_complete': True})['rows'][0]
        self.assertEqual(row['result'], 'Submitted to AndroidSync')
        self.assertEqual(row['provider_status'], 'PendingApproval')
        self.assertTrue(row['send_complete'])
        self.assertFalse(row['query_original_request'])
        self.assertFalse(row['requires_handset_confirmation'])

    def test_unread_or_email_status_cannot_be_used_as_sms_completion(self):
        with self.assertRaises(ValueError):
            outcome_checks.sms_progress(outcome('email', 'Sent'))
        data = outcome('sms', 'SentToNetwork')
        data['provider']['read_verified'] = False
        with self.assertRaises(ValueError):
            outcome_checks.sms_progress(data)

    def test_local_batch_uses_original_capture_and_returns_no_poll(self):
        data = outcome('sms', 'SentToNetwork')
        result = local_checks.run({'checks': [{'name': 'completion', 'operation': 'sms.progress',
                                              'input': {'$capture': 'original'}}]}, {'original': data})
        self.assertEqual(result['status'], 'LocalChecksPassed')
        self.assertFalse(result['checks'][0]['result']['query_original_request'])

    def test_current_pages_finish_once_without_changing_payload_counts_or_stop(self):
        for language, label in [('en', 'Submitted to AndroidSync'), ('zh-CN', '\u5df2\u4ea4\u4ed8AndroidSync')]:
            data = sms_fixture() | {'language': language}
            original = copy.deepcopy(data)
            plan = sms_presentation.plan(data)
            self.assertTrue(plan['send_complete'])
            self.assertFalse(plan['query_original_request'])
            self.assertFalse(plan['requires_handset_confirmation'])
            saved = saved_sms(data)
            self.assertEqual(email_presentation.properties(saved['notification'])['State'], 'Completed')
            self.assertEqual(email_presentation.properties(saved['send_run'])['State'], 'Completed')
            cycle = email_presentation.blocks(saved['cycle'], 'sms-cycle-current-state')[1]
            self.assertEqual(cycle['known_this_executor_sent'], 1)
            self.assertEqual(cycle['reserved_count'], 0)
            self.assertTrue(cycle['stop'])
            self.assertIn(label, saved['result']['text'])
            self.assertFalse(email_presentation.blocks(saved['notification'], 'sms-current-outcome')[1]['human_received'])
            self.assertEqual(sms_presentation.plan(data | {'pages': saved})['updates'], [])
            self.assertEqual(data, original)

    def test_operator_success_has_no_missing_confirmation_prompt_in_either_language(self):
        event = outcome('sms', 'SentToNetwork') | {'account': 'configured-device'}
        for language, label in [('en', 'Submitted to AndroidSync'), ('zh-CN', '\u5df2\u4ea4\u4ed8AndroidSync')]:
            result = operator_experience.result_summary({'events': [event], 'language': language,
                                                         'coverage_complete': True})
            row = result['rows'][0]
            self.assertEqual(row['result'], label)
            self.assertTrue(row['send_complete'])
            self.assertFalse(row['query_original_request'])
            self.assertFalse(row['requires_handset_confirmation'])
            self.assertEqual(result['counts']['sms_sent'], 1)
            self.assertNotIn('unconfirmed', row['receipt'])
            self.assertNotIn('\u672a\u786e\u8ba4', row['receipt'])

    def test_optional_later_delivery_does_not_count_the_same_send_twice(self):
        data = sms_fixture()
        network_pages = saved_sms(data)
        delivered = data | {'pages': network_pages,
                            'provider_status': {'id': 'message1', 'status': 'Delivered', 'deviceId': 'phone'}}
        final = saved_sms(delivered)
        cycle = email_presentation.blocks(final['cycle'], 'sms-cycle-current-state')[1]
        self.assertEqual(cycle['known_this_executor_sent'], 1)
        self.assertEqual(cycle['total_count'], 1)
        self.assertTrue(cycle['stop'])
        self.assertFalse(sms_presentation.plan(delivered)['query_original_request'])

    def test_one_completed_send_does_not_cancel_an_independent_future_follow_up(self):
        data = sms_fixture()
        old, cycle = email_presentation.blocks(data['pages']['cycle'], 'sms-cycle-current-state')
        cycle.update(stop=False, active=True, next_due='2026-11-02T02:00:00Z')
        data['pages']['cycle']['text'] = data['pages']['cycle']['text'].replace(
            old, sms_presentation.json_block(cycle))
        saved = saved_sms(data)
        current = email_presentation.blocks(saved['cycle'], 'sms-cycle-current-state')[1]
        self.assertTrue(current['active'])
        self.assertEqual(current['next_due'], '2026-11-02T02:00:00Z')
        self.assertFalse(sms_presentation.plan(data)['query_original_request'])
