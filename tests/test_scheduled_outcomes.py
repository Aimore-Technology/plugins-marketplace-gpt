"""State conflicts and interrupted result recording must not replay sending."""

import copy
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/eightdegrees-sales-workflow/scripts'
sys.path.insert(0, str(SCRIPTS))
import outcome_checks as OUTCOME
import send_receipt as RECEIPT
import workflow_checks as ROUTES
from test_schedule_checks import SCHEDULE, scheduled_guard
from test_workflow_checks import task


def outcome(operation='email', status='Sent'):
    return {'task_id': 'b' * 32, 'content_version': 'test-v1',
            'provider': {'operation': operation, 'status': status, 'message_id': 'sent-1', 'read_verified': True}}


def saved_outcome(data=None):
    data = copy.deepcopy(data or outcome())
    expected = OUTCOME.projection(data)['expected']
    data['saved'] = {name: {**expected, 'task_id': data['task_id'], 'content_version': data['content_version'], 'read_verified': True} for name in ('task', 'index', 'action_result')}
    return data


def receipt_input():
    approved = {'content_version': 'test-v1', 'sender': 'operator@example.com', 'recipient': 'buyer@example.com',
                'subject': 'Project information', 'payload_sha256': 'f' * 64, 'receipt_template': 'send-receipt-v1',
                'location_id': 'location-1', 'contact_id': 'contact-1'}
    return {'task_id': 'b' * 32, 'timezone': 'Australia/Adelaide',
            'source_url': 'https://app.notion.com/p/' + 'b' * 32,
            'customer': {'location_id': 'location-1', 'contact_id': 'contact-1', 'name': 'Example Customer'},
            'approved': approved, 'sent': {**approved, 'message_id': 'sent-1',
                'sent_at': '2026-10-30T00:55:23Z', 'status': 'Sent', 'read_verified': True}}


def note_readback(data):
    return {'id': 'note-1', 'location_id': data['customer']['location_id'],
            'contact_id': data['customer']['contact_id'], 'read_verified': True,
            'body': RECEIPT.render(data)['note']}


class ScheduledOutcomeTests(unittest.TestCase):
    def test_native_cycle_can_reach_automatic_send_owner_but_public_scan_cannot(self):
        guard = SCHEDULE.guard(scheduled_guard())
        item = task(); item['OperatorId'] = guard['operator_id']
        self.assertEqual(ROUTES.check_resume(item, 'scheduled-approved-work', schedule_guard=guard)['status'], 'EligibleForOwnerCheck')
        self.assertEqual(ROUTES.check_resume(item, 'one-cycle-no-customer-send')['status'], 'Deferred')

    def test_internal_policy_name_without_guard_or_wrong_operator_does_not_dispatch(self):
        item = task(); item['OperatorId'] = 'operator-local-demo'
        self.assertEqual(ROUTES.check_resume(item, 'scheduled-approved-work')['status'], 'Deferred')
        guard = SCHEDULE.guard(scheduled_guard()); item['OperatorId'] = 'other'
        self.assertEqual(ROUTES.check_resume(item, 'scheduled-approved-work', schedule_guard=guard)['status'], 'Deferred')

    def test_manual_inputs_never_transfer_to_native_cycle_even_with_continue(self):
        guard = SCHEDULE.guard(scheduled_guard()); item = task(mode='Manual'); item['OperatorId'] = guard['operator_id']
        for phase in ('register', 'observe', 'execute'):
            self.assertEqual(ROUTES.check_resume(item, 'scheduled-approved-work', True, phase, guard)['status'], 'Deferred')

    def test_completed_original_is_not_reopened_from_query_row(self):
        data = {'original': {'id': 'task-1', 'state': 'Completed', 'read_verified': True},
                'candidate': {'id': 'task-1', 'state': 'InProgress'}}
        before = copy.deepcopy(data); result = OUTCOME.task_state(data)
        self.assertEqual(result['status'], 'NeedsReconciliation')
        self.assertFalse(result['execute_allowed']); self.assertEqual(data, before)

    def test_query_completed_cannot_hide_open_original(self):
        data = {'original': {'id': 'task-1', 'state': 'WaitingForOperator', 'read_verified': True},
                'candidate': {'id': 'task-1', 'state': 'Completed'}}
        self.assertFalse(OUTCOME.task_state(data)['execute_allowed'])

    def test_unread_or_terminal_task_does_not_dispatch(self):
        for state in ('Completed', 'Cancelled'):
            self.assertEqual(OUTCOME.task_state({'original': {'id': 'task-1', 'state': state, 'read_verified': True}})['status'], 'Deferred')
        with self.assertRaises(ValueError): OUTCOME.task_state({'original': {'id': 'task-1', 'state': 'InProgress'}})

    def test_stale_sent_false_index_blocks_projection_success(self):
        data = saved_outcome()
        self.assertEqual(OUTCOME.verify_projection(data)['status'], 'OutcomeProjectionsVerified')
        data['saved']['index']['sent'] = False
        self.assertEqual(OUTCOME.verify_projection(data)['status'], 'NeedsCorrection')

    def test_same_message_on_wrong_task_or_version_cannot_verify_a_projection(self):
        for key, value in (('task_id', 'other-task'), ('content_version', 'old-version')):
            data = saved_outcome(); data['saved']['action_result'][key] = value
            self.assertEqual(OUTCOME.verify_projection(data)['status'], 'NeedsCorrection')

    def test_receipt_target_must_match_the_frozen_approval(self):
        for key in ('location_id', 'contact_id'):
            data = receipt_input(); data['customer'][key] = 'other'
            with self.assertRaises(ValueError): RECEIPT.render(data)

    def test_accepted_or_unknown_reserves_instead_of_counting_sent(self):
        for status in ('AwaitingPhone', 'PendingApproval', 'ProviderAccepted', 'Unknown'):
            fields = OUTCOME.projection(outcome('sms', status))['expected']
            self.assertFalse(fields['sent']); self.assertTrue(fields['reserved'])

    def test_operator_receipt_never_changes_actual_provider_status(self):
        data = outcome('sms', 'SentToNetwork')
        data['human_receipt'] = {'message_id': 'sent-1', 'received': True, 'source': 'operator observation', 'sender_display': 'own-number'}
        fields = OUTCOME.projection(data)['expected']
        self.assertTrue(fields['human_received']); self.assertFalse(fields['provider_delivered'])
        self.assertEqual(fields['provider_status'], 'SentToNetwork')
        data['human_receipt']['message_id'] = 'another'
        with self.assertRaises(ValueError): OUTCOME.projection(data)

    def test_stale_action_or_unread_projection_is_not_success(self):
        for field, value in (('human_received', True), ('read_verified', False)):
            data = saved_outcome(); data['saved']['action_result'][field] = value
            self.assertEqual(OUTCOME.verify_projection(data)['status'], 'NeedsCorrection')

    def test_totals_deduplicate_log_copies_and_never_count_unknown_as_sent(self):
        email = {**outcome(), 'account': 'sender@example.com'}
        sms = {**outcome('sms', 'Unknown'), 'account': 'device-owner'}
        result = OUTCOME.counts({'events': [email, copy.deepcopy(email), sms], 'coverage_complete': True})
        self.assertEqual((result['email_sent'], result['sms_sent'], result['unknown'], result['reserved']), (1, 0, 1, 1))

    def test_partial_discovery_does_not_claim_global_zero_or_hide_conflicts(self):
        result = OUTCOME.counts({'events': [], 'coverage_complete': False})
        self.assertFalse(result['coverage_complete'])
        email = {**outcome(), 'account': 'sender@example.com'}
        conflict = copy.deepcopy(email); conflict['provider']['status'] = 'Unknown'
        self.assertEqual(OUTCOME.counts({'events': [email, conflict], 'coverage_complete': True})['status'], 'NeedsReconciliation')

    def test_receipt_uses_complete_plain_template_and_actual_message(self):
        note = RECEIPT.render(receipt_input())['note']
        self.assertIn('Provider message ID: sent-1', note)
        for section in ('Context Background:', 'Action:', 'Recommendation:', 'Next Schedule:'): self.assertIn(section, note)
        self.assertNotIn('**', note)

    def test_changed_actual_payload_cannot_use_old_receipt_scope(self):
        for key in ('sender', 'recipient', 'subject', 'payload_sha256'):
            data = receipt_input(); data['sent'][key] = 'changed'
            with self.assertRaises(ValueError): RECEIPT.render(data)

    def test_unscoped_legacy_approval_and_unknown_send_cannot_make_receipt(self):
        data = receipt_input(); del data['approved']['receipt_template']
        with self.assertRaises(ValueError): RECEIPT.render(data)
        for key, value in (('status', 'Unknown'), ('read_verified', False)):
            data = receipt_input(); data['sent'][key] = value
            with self.assertRaises(ValueError): RECEIPT.render(data)

    def test_interrupted_projection_reuses_exact_existing_receipt(self):
        data = receipt_input(); data.update(existing_notes=[note_readback(data)], list_complete=True)
        result = RECEIPT.reconcile(data)
        self.assertEqual(result['status'], 'CRMReceiptVerified'); self.assertFalse(result['append_allowed'])
        self.assertEqual(result['crm_note_id'], 'note-1')

    def test_unknown_append_or_incomplete_listing_blocks_another_receipt(self):
        data = receipt_input(); data.update(existing_notes=[], list_complete=False)
        self.assertEqual(RECEIPT.reconcile(data)['status'], 'NeedsReconciliation')
        data['list_complete'] = True
        self.assertTrue(RECEIPT.reconcile(data)['append_allowed'])
        data['pending_attempt_status'] = 'Unknown'
        self.assertEqual(RECEIPT.reconcile(data)['status'], 'NeedsReconciliation')

    def test_wrong_contact_or_changed_receipt_bytes_fails_readback(self):
        data = receipt_input(); note = note_readback(data)
        for key, value in (('contact_id', 'other'), ('location_id', 'other'), ('body', note['body'] + '\n')):
            data['note_readback'] = {**note, key: value}
            self.assertEqual(RECEIPT.verify(data)['status'], 'NeedsReconciliation')

    def test_duplicate_receipts_do_not_cause_another_append(self):
        data = receipt_input(); data.update(existing_notes=[note_readback(data), note_readback(data)], list_complete=True)
        self.assertEqual(RECEIPT.reconcile(data)['status'], 'NeedsReconciliation')

    def test_receipt_key_survives_retry_but_changes_with_actual_message(self):
        data = receipt_input(); key = RECEIPT.render(data)['receipt_key']
        data['task_id'] = 'c' * 32; data['approved']['content_version'] = 'recovery-v2'
        self.assertEqual(RECEIPT.render(data)['receipt_key'], key)
        data['sent']['message_id'] = 'sent-2'
        self.assertNotEqual(RECEIPT.render(data)['receipt_key'], key)


if __name__ == '__main__': unittest.main()
