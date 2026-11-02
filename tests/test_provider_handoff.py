"""Finish at external acceptance; keep our approval, storage and CRM checks."""

import copy
import unittest

from test_reply_transport import fixture, ADAPTER
from test_email_presentation import fixture as email_pages, apply_plan, block
from test_sms_authority import inputs as sms_input, saved as sms_saved
from test_scheduled_outcomes import outcome, saved_outcome, receipt_input, note_readback
from test_unattended import sms_fixture, saved_sms
import email_presentation
import local_checks
import material_handoff
import notion_checks
import operator_experience
import outcome_checks
import provider_handoff
import send_receipt
import sms_authority
import sms_channel
import sms_presentation


def email_ack():
    draft = fixture()
    draft['manifest'].update(task_page_id='b' * 32, content_version='test-v1')
    return {'operation': 'email', 'manifest': draft['manifest'],
            'draft_verification': ADAPTER.verify(draft),
            'request': {'draft_id': draft['manifest']['draft_id']},
            'response': {'id': 'sent-1'}}


def sms_ack(status='AwaitingPhone'):
    data = sms_input()
    data['saved_task'] = sms_saved(data)
    frozen = sms_authority.prepare(data)['record']
    return {'operation': 'sms', 'notification': frozen, 'authority': sms_authority.verify(data),
            'request': {'body': frozen['body'], 'recipient': frozen['recipient'],
                        'deviceId': frozen['device_id'], 'idempotencyKey': 'one-original-request'},
            'response': {'Id': 'request-1', 'Status': status}}


def submitted_email_pages():
    data = email_pages(False)
    ack_input = email_ack()
    ack = provider_handoff.verify(ack_input)
    original, package = email_presentation.blocks(data['pages']['send_task'], 'sales-send-package')
    package['transport_manifest'] = ack_input['manifest']
    data['pages']['send_task']['text'] = data['pages']['send_task']['text'].replace(original, block(package))
    original, _ = email_presentation.blocks(data['pages']['send_task'], 'email-sent-proof')
    replacement = {'record_type': 'email-handoff-proof', 'verification': ack,
                   'provider_result': ack_input['response']}
    data['pages']['send_task']['text'] = data['pages']['send_task']['text'].replace(original, block(replacement))
    original, result = email_presentation.blocks(data['pages']['send_task'], 'email-send-current-outcome')
    result['provider_status'] = 'ProviderAccepted'
    data['pages']['send_task']['text'] = data['pages']['send_task']['text'].replace(original, block(result))
    return data


class ProviderHandoffTests(unittest.TestCase):
    def test_new_send_plan_cannot_require_a_future_external_sent_lookup(self):
        from phase_contracts import task_evidence
        with self.assertRaises(ValueError):
            task_evidence({'resume_step': 'SendApprovedReply', 'evidence': ['reply-sent']})
        self.assertIn('provider-handoff', task_evidence({'resume_step': 'SendApprovedReply'}))
        self.assertIn('reply-sent', task_evidence({'resume_step': 'SendApprovedReply',
                      'evidence': ['reply-sent']}, allow_legacy=True))

    def test_gmail_id_only_ack_finishes_without_sent_mime_or_receiving_mailbox(self):
        data = email_ack()
        original = copy.deepcopy(data)
        result = provider_handoff.verify(data)
        self.assertEqual(result['status'], 'ProviderHandoffVerified')
        self.assertEqual(result['provider_status'], 'ProviderAccepted')
        self.assertTrue(result['send_complete'])
        self.assertFalse(result['query_original_request'])
        self.assertFalse(result['delivery_verification_required'])
        self.assertNotIn('message', data)
        self.assertNotIn('sent_message_id', data)
        self.assertEqual(data, original)

    def test_wrong_draft_payload_binding_or_explicit_rejection_cannot_finish(self):
        for mutation in ('draft', 'payload', 'recipient', 'rejection', 'missing-id', 'saved-draft'):
            data = email_ack()
            if mutation == 'draft': data['request']['draft_id'] = 'another'
            if mutation == 'payload': data['draft_verification']['html_sha256'] = '0' * 64
            if mutation == 'recipient': data['manifest']['to'] = 'other@example.com'
            if mutation == 'rejection': data['response']['success'] = False
            if mutation == 'missing-id': data['response'].clear()
            if mutation == 'saved-draft': data['response']['label_ids'] = ['DRAFT']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                provider_handoff.verify(data)

    def test_actual_mcp_error_envelope_is_not_success(self):
        data = email_ack()
        data['response'] = {'isError': True, 'content': [{'type': 'text', 'text': 'Rejected'}]}
        with self.assertRaises(ValueError): provider_handoff.verify(data)

    def test_androidsync_ack_completes_at_every_accepted_state_without_polling(self):
        for status in ('AwaitingPhone', 'PendingApproval', 'ProviderAccepted', 'SentToNetwork', 'Delivered'):
            result = provider_handoff.verify(sms_ack(status))
            self.assertTrue(result['send_complete'])
            self.assertFalse(result['query_original_request'])
            self.assertEqual(result['provider_status'], status)
            progress = outcome_checks.sms_progress(outcome('sms', status))
            self.assertTrue(progress['send_complete'])
            self.assertFalse(progress['query_original_request'])
            self.assertFalse(progress['retry_send_allowed'])

    def test_androidsync_failed_unknown_or_changed_request_is_not_handoff(self):
        for status in ('Unknown', 'Failed'):
            with self.assertRaises(ValueError): provider_handoff.verify(sms_ack(status))
        for key, value in [('body', 'Another message'), ('recipient', '+61400000000'), ('deviceId', 'another')]:
            data = sms_ack(); data['request'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): provider_handoff.verify(data)

    def test_only_unknown_handoff_is_reserved_and_no_status_poll_is_created(self):
        for operation in ('email', 'sms'):
            for status in ('Unknown', 'Failed'):
                event = outcome(operation, status)
                progress = outcome_checks.send_progress(event)
                self.assertFalse(progress['send_complete'])
                self.assertFalse(progress['query_original_request'])
                self.assertFalse(progress['retry_send_allowed'])
                self.assertEqual(outcome_checks.projection(event)['expected']['reserved'], status == 'Unknown')

    def test_email_local_results_complete_from_ack_without_delivery_fields(self):
        data = submitted_email_pages()
        data['saved_pages'] = apply_plan(data)
        result = email_presentation.verify(data)
        self.assertEqual(result['status'], 'EmailPresentationVerified')
        self.assertFalse(result['expected_outcome']['human_received'])
        self.assertFalse(result['expected_outcome']['provider_delivered'])
        self.assertEqual(result['expected_outcome']['provider_status'], 'ProviderAccepted')
        self.assertIn('Submitted to Gmail', data['saved_pages']['send_action']['text'])
        self.assertEqual(email_presentation.plan(data | {'pages': data['saved_pages']})['updates'], [])

    def test_sms_owned_pages_close_on_initial_ack_and_count_once(self):
        data = sms_fixture('AwaitingPhone')
        saved = saved_sms(data)
        for role in ('notification', 'send_run', 'data_task', 'data_run'):
            self.assertEqual(email_presentation.properties(saved[role])['State'], 'Completed')
        result = email_presentation.blocks(saved['notification'], 'sms-current-outcome')[1]
        cycle = email_presentation.blocks(saved['cycle'], 'sms-cycle-current-state')[1]
        self.assertEqual(result['provider_status'], 'AwaitingPhone')
        self.assertFalse(result['provider_delivered'])
        self.assertEqual(cycle['known_this_executor_sent'], 1)
        self.assertEqual(cycle['reserved_count'], 0)
        self.assertEqual(cycle['total_count'], 1)
        self.assertTrue(cycle['stop'])
        self.assertEqual(sms_presentation.plan(data | {'pages': saved})['updates'], [])

    def test_crm_still_requires_exact_written_body_target_and_readback(self):
        data = receipt_input(); data['sent']['status'] = 'ProviderAccepted'; data['approved']['receipt_template'] = 'send-receipt-v2'
        data['note_readback'] = note_readback(data)
        self.assertEqual(send_receipt.verify(data)['status'], 'CRMReceiptVerified')
        for key, value in [('body', 'Other note'), ('read_verified', False), ('contact_id', 'other')]:
            bad = copy.deepcopy(data); bad['note_readback'][key] = value
            self.assertEqual(send_receipt.verify(bad)['status'], 'NeedsReconciliation')

    def test_original_approved_crm_receipt_template_is_not_silently_rewritten(self):
        legacy = send_receipt.render(receipt_input())
        self.assertEqual(legacy['sha256'], 'c4729c91c94cfca7330d08168b14c880f56ad2129729d77c2c0f7e027b0a3c64')
        self.assertEqual(legacy['payload']['content_version'], 'send-receipt-v1')
        current = receipt_input(); current['approved']['receipt_template'] = 'send-receipt-v2'
        current['sent']['status'] = 'ProviderAccepted'
        result = send_receipt.render(current)
        self.assertEqual(result['payload']['content_version'], 'send-receipt-v2')
        self.assertIn('handed to Gmail', result['note'])

    def test_material_registration_uses_acceptance_without_sent_status_probe(self):
        from test_material_handoff import inputs
        data = inputs(); data['event']['status'] = 'ProviderAccepted'
        result = material_handoff.plan(data)
        self.assertEqual(result['status'], 'MaterialHandoffPlanned')
        self.assertFalse(result['record']['create_native_task'])
        self.assertEqual(result['record']['message_id'], data['event']['message_id'])

    def test_one_way_configured_channel_does_not_require_an_inbound_or_delivery_probe(self):
        data = {'invocation_policy': 'one-cycle-approved-work', 'channel_verified': True,
                'inbound_reader_available': False, 'guards': dict.fromkeys(
                    ('stop', 'manual_pause', 'unknown_attempt', 'customer_replied'), False)}
        self.assertEqual(sms_channel.gate(data)['mode'], 'ordinary')
        data['guards']['stop'] = True
        self.assertEqual(sms_channel.gate(data)['status'], 'ChannelCheckBlocked')

    def test_summary_distinguishes_submission_from_raw_external_status(self):
        for operation, status in [('email', 'ProviderAccepted'), ('sms', 'AwaitingPhone')]:
            event = outcome(operation, status) | {'account': 'authorized'}
            result = operator_experience.result_summary({'events': [event, copy.deepcopy(event)], 'coverage_complete': True})
            self.assertEqual(result['counts'][operation + '_sent'], 1)
            row = result['rows'][0]
            self.assertIn('Submitted to', row['result'])
            self.assertEqual(row['provider_status'], status)
            self.assertTrue(row['send_complete'])
            self.assertFalse(row['query_original_request'])

    def test_acceptance_does_not_permit_a_receipt_wait_in_our_current_status(self):
        data = saved_outcome(outcome('email', 'ProviderAccepted'))
        data['action_page']['text'] = data['action_page']['text'].replace('No action required.', 'Waiting for recipient confirmation.')
        self.assertEqual(outcome_checks.verify_projection(data)['status'], 'NeedsCorrection')

    def test_batch_checks_original_ack_offline_and_does_not_mutate_it(self):
        data = sms_ack(); original = copy.deepcopy(data)
        result = local_checks.run({'checks': [{'name': 'handoff', 'operation': 'provider.handoff',
                                  'input': {'$capture': 'ack'}}]}, {'ack': data})
        self.assertEqual(result['status'], 'LocalChecksPassed')
        self.assertTrue(result['checks'][0]['result']['handoff_complete'])
        self.assertEqual(data, original)

    def test_full_email_owner_completes_with_acceptance_only_and_keeps_crm_gate(self):
        from test_phase_ordering import sent, phased
        from test_material_handoff import inputs, saved
        data = sent()
        ack_input = email_ack()
        note = receipt_input(); note['sent']['status'] = 'ProviderAccepted'; note['approved']['receipt_template'] = 'send-receipt-v2'
        for target, origin in [('sender', 'from_address'), ('recipient', 'to'),
                               ('subject', 'subject'), ('payload_sha256', 'html_sha256')]:
            note['approved'][target] = note['sent'][target] = ack_input['manifest'][origin]
        note['note_readback'] = note_readback(note)
        material = inputs(); material['event'].update(status='ProviderAccepted', message_id='sent-1')
        material['email_task_id'] = ack_input['manifest']['task_page_id']
        view = submitted_email_pages(); view['saved_pages'] = apply_plan(view)
        values = {'provider-handoff': provider_handoff.verify(ack_input),
                  'outcome': outcome_checks.verify_projection(saved_outcome(outcome('email', 'ProviderAccepted'))),
                  'crm-receipt': send_receipt.verify(note),
                  'material-handoff': material_handoff.verify({'input': material,
                      'saved_email_task': saved(material, 'email') | {'id': material['email_task_id']},
                      'saved_cycle': saved(material)}),
                  'email-presentation': email_presentation.verify(view)}
        for item in data['completion']['checks']:
            kind = data['registry']['required_checks'][item['name']]['kind']
            if kind in values: item['result'] = values[kind]
        prepared = phased(data)
        self.assertEqual(notion_checks.owner_write(prepared)['status'], 'WithinOwnerScope')
        kinds = {x['kind'] for x in prepared['registry']['required_checks'].values()}
        self.assertNotIn('reply-sent', kinds)
        bad = copy.deepcopy(prepared)
        for item in bad['completion']['checks']:
            if bad['registry']['required_checks'][item['name']]['kind'] == 'crm-receipt':
                item['result']['status'] = 'NeedsReconciliation'
        self.assertEqual(notion_checks.owner_write(bad)['status'], 'Deferred')

    def test_owner_cannot_upgrade_acknowledgement_to_unobserved_external_sent(self):
        from test_phase_ordering import sent, phased
        data = phased(sent())
        for item in data['completion']['checks']:
            if data['registry']['required_checks'][item['name']]['kind'] == 'provider-handoff':
                item['result']['provider_status'] = 'ProviderAccepted'
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')


if __name__ == '__main__':
    unittest.main()
