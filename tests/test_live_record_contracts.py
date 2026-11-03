"""Regressions for the actual mixed-version record shapes, with synthetic data."""
import copy
import json
import unittest

from test_email_presentation import fixture, page, block, apply_plan
from test_unattended import contact_fixture, cycle_fixture
from test_material_handoff import inputs, saved
from test_owner_completion import completion_for, TASK
import contact_preferences
import email_presentation
import material_handoff
import notion_checks
import scan_cycle
import sms_channel


class LegacyRecords(unittest.TestCase):
    def legacy_persona(self):
        data = contact_fixture()
        capture = data['persona_page']
        original, value = email_presentation.blocks(capture, 'approved-persona-snapshot')
        value.pop('client_id')
        value.update(approved=True, content_version='call-v1', approved_input_sha256='a'*64)
        capture['text'] = capture['text'].replace(original, block(value)).replace('## Current approved persona', '## \u5df2\u786e\u8ba4\u753b\u50cf · Customer')
        settings = {'settings_schema_version': 2, 'client_pages': {
            'location1:contact1': {'location_id': 'location1', 'contact_id': 'contact1',
                                 'persona_page_id': capture['id']}}}
        data['settings_page'] = page('9'*32, block(settings), {})
        return data

    def test_legacy_missing_client_and_localized_heading_uses_original_registry(self):
        data = self.legacy_persona()
        snapshot = email_presentation.blocks(data['persona_page'], 'approved-persona-snapshot')[0]
        result = contact_preferences.stop_overlay(data)
        updated = copy.deepcopy(data['persona_page'])
        for edit in result['updates']:
            updated['text'] = updated['text'].replace(edit['old_str'], edit['new_str'], 1)
        self.assertIn(snapshot, updated['text'])
        self.assertEqual(contact_preferences.verify(data | {'saved_persona_page': updated,
            'maintenance_task_id': '8'*32})['status'], 'ContactRestrictionVerified')
        self.assertEqual(contact_preferences.stop_overlay(data | {'persona_page': updated})['updates'], [])

    def test_legacy_binding_cannot_be_inferred_from_name_or_given_client(self):
        for change in ('missing', 'other_page', 'other_customer', 'unapproved'):
            data = self.legacy_persona()
            if change == 'missing': data.pop('settings_page')
            elif change == 'other_page': data['settings_page']['text'] = data['settings_page']['text'].replace('d'*32, '7'*32)
            elif change == 'other_customer': data['settings_page']['text'] = data['settings_page']['text'].replace('location1:contact1', 'location1:another')
            else: data['persona_page']['text'] = data['persona_page']['text'].replace('"approved": true', '"approved": false')
            with self.subTest(change=change), self.assertRaises(ValueError): contact_preferences.stop_overlay(data)

    def test_top_level_sent_rfc_id_is_read_without_rewriting_proof(self):
        data = fixture(); capture = data['pages']['send_task']
        original, proof = email_presentation.blocks(capture, 'email-sent-proof')
        proof['rfc_message_id'] = proof.pop('details')['rfc_message_id']
        capture['text'] = capture['text'].replace(original, block(proof))
        data['saved_pages'] = apply_plan(data)
        self.assertEqual(email_presentation.verify(data)['status'], 'EmailPresentationVerified')
        self.assertIn(block(proof), data['saved_pages']['send_task']['text'])

    def test_conflicting_rfc_layouts_and_quoted_only_receipt_are_rejected(self):
        data = fixture(); capture = data['pages']['send_task']
        original, proof = email_presentation.blocks(capture, 'email-sent-proof')
        proof['rfc_message_id'] = '<another@example.com>'
        capture['text'] = capture['text'].replace(original, block(proof))
        with self.assertRaises(ValueError): email_presentation.plan(data)
        for text in ('> I received the brochure.', '<blockquote>I received the brochure.</blockquote>'):
            data = fixture(); data['receipt']['message']['payload']['body']['content'] = text
            with self.assertRaises(ValueError): email_presentation.plan(data)

    def test_legacy_approval_pointer_requires_actual_accepted_review(self):
        data = fixture(); capture = data['pages']['send_task']
        original, package = email_presentation.blocks(capture, 'sales-send-package')
        approval = package.pop('content_approval')
        package.update(content_approved=True, content_approval_sha256='a'*64,
            content_task_page_id=approval['task_page_id'], content_action_page_id=approval['action_page_id'])
        capture['text'] = capture['text'].replace(original, block(package))
        with self.assertRaises(ValueError): email_presentation.plan(data)
        accepted = {'record_type': 'accepted-action-submission', 'read_verified': True,
            'task_id': approval['task_page_id'], 'action_page_id': approval['action_page_id'],
            'content_version': 'test-v1', 'decision': 'Confirm', 'input_sha256': 'a'*64}
        data['pages']['review_task']['text'] = data['pages']['review_task']['text'].replace('</content>', block(accepted)+'\n</content>')
        self.assertEqual(email_presentation.plan(data)['status'], 'EmailPresentationPlanned')
        data['pages']['review_task']['text'] = data['pages']['review_task']['text'].replace('"input_sha256": "'+ 'a'*64, '"input_sha256": "'+'b'*64)
        with self.assertRaises(ValueError): email_presentation.plan(data)


class RecoveryEvidence(unittest.TestCase):
    def evidence(self):
        data = inputs(); data['email_task_id'] = '1'*32
        record = {'record_type': 'material-handoff-recovery-v1', 'original_send_task_id': '1'*32,
            'current_outcome': {'message_id': 'sent-one', 'sent': True, 'content_version': 'test-v1'}}
        recovery = page(TASK, block(record), {'OwnerSkill': 'eightdegrees-sales-reply',
            'StepId': 'RecordMaterialHandoff', 'ResumeStep': 'RecordMaterialHandoff',
            'SourceURL': 'https://app.notion.com/p/'+'1'*32, 'ContentVersion': 'test-v1'})
        return {'input': data, 'saved_email_task': saved(data, 'email') | {'id': '1'*32},
                'saved_cycle': saved(data), 'saved_recovery_task': recovery}

    def test_distinct_recovery_passes_the_unweakened_owner_completion_gate(self):
        payload = self.evidence(); result = material_handoff.verify(payload)
        self.assertEqual(result['entity_id'], TASK)
        self.assertEqual(result['email_task_id'], '1'*32)
        data = completion_for('eightdegrees-sales-reply', 'RecordMaterialHandoff')
        required = data['completion']['required_checks']
        required['handoff'] = {'kind': 'material-handoff', 'entity_id': TASK}
        required['email'] = {'kind': 'page-links', 'entity_id': '1'*32}
        data['registry']['publication_page_ids'].append('1'*32)
        data['registry']['required_checks'] = copy.deepcopy(required)
        for name, proof in [('handoff', result), ('email', notion_checks.page_links({'page': payload['saved_email_task']}))]:
            data['completion']['checks'].append({'name': name, 'invocation_id': 'run-1',
                'publication_version': 'publication-v1', 'exit_code': 0, 'result': proof})
        self.assertEqual(notion_checks.owner_write(data)['status'], 'WithinOwnerScope')
        data['completion']['checks'][-2]['result']['entity_id'] = '1'*32
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')

    def test_foreign_recovery_source_or_message_cannot_close(self):
        for old, new in [('sent-one', 'other-sent'), ('1'*32, '2'*32), ('test-v1', 'wrong-version')]:
            data = self.evidence()
            data['saved_recovery_task']['text'] = data['saved_recovery_task']['text'].replace(old, new)
            with self.subTest(old=old), self.assertRaises(ValueError): material_handoff.verify(data)


class ScanAdmission(unittest.TestCase):
    def test_completed_step_clears_stale_digest_candidates_and_survives_next_cycle(self):
        data = cycle_fixture(); original = data['items'][0]; identity = scan_cycle.key(original)
        data['items'].append(original | {'input_digest': 'old-unsubmitted', 'waiting': True})
        first = scan_cycle.advance(data | {'results': [{'key': identity, 'state': 'completed', 'receipt_ref': 'actual-result'}]})
        self.assertEqual(first['checkpoint']['work_items'], [])
        data['checkpoint_page'] = page('9'*32, block(first['checkpoint']), {})
        data['items'] = [original | {'input_digest': 'reconstructed'}]
        self.assertEqual(scan_cycle.advance(data)['work'], [])

    def test_unknown_old_attempt_blocks_changed_digest_or_new_version_dispatch(self):
        data = cycle_fixture(); original = data['items'][0]; identity = scan_cycle.key(original)
        first = scan_cycle.advance(data | {'results': [{'key': identity, 'state': 'unknown',
            'attempt_id': 'original-request', 'receipt_ref': 'original-evidence'}]})
        data['checkpoint_page'] = page('9'*32, block(first['checkpoint']), {})
        data['items'] = [original | {'input_digest': 'changed', 'version': 'v2'}]
        data['attempted_keys'] = [identity]
        self.assertEqual(scan_cycle.advance(data)['work'], [])

    def test_one_selection_and_cost_prevents_new_owner_near_deadline(self):
        data = cycle_fixture(); data['items'][0]['estimated_seconds'] = 150
        data['now'] = '2026-11-01T00:05:00Z'
        result = scan_cycle.advance(data)
        self.assertEqual(result['work'], [])
        self.assertTrue(result['requires_next_cycle'])
        self.assertEqual(result['seconds_available_for_work'], 120)
        data['now'] = '2026-11-01T00:04:00Z'
        self.assertEqual(len(scan_cycle.advance(data)['work']), 1)

    def test_multiple_historical_unknown_attempts_remain_individually_reconcilable(self):
        data = cycle_fixture(); first = data['items'][0]
        data['items'].append(first | {'version': 'v2', 'input_digest': 'second-actual-attempt'})
        results = [{'key': scan_cycle.key(item), 'state': 'unknown', 'attempt_id': 'attempt'+str(i),
                    'receipt_ref': 'actual'+str(i)} for i,item in enumerate(data['items'])]
        data['results'] = results
        saved = scan_cycle.advance(data)
        self.assertEqual(saved['work'], [])
        data['checkpoint_page'] = page('9'*32, block(saved['checkpoint']), {})
        data.pop('results')
        for item in data['items']:
            item['recovery_wakeup'] = {'evidence_ref': 'capture:original-new-evidence', 'revision': 'new:'+item['version']}
        r = scan_cycle.advance(data); self.assertEqual(r['work'][0]['action'], 'reconcile')
        data['attempted_keys'] = [r['work'][0]['key']]
        r2 = scan_cycle.advance(data); self.assertEqual(r2['work'][0]['action'], 'reconcile')
        self.assertNotEqual(r['work'][0]['attempt_id'], r2['work'][0]['attempt_id'])

    def test_unfitting_stop_is_not_skipped_to_admit_an_outbound_send(self):
        data = cycle_fixture(); data['now'] = '2026-11-01T00:06:00Z'
        data['items'].append(data['items'][0] | {'source_key': 'stop', 'step': 'RefreshContactRestrictions',
            'estimated_seconds': 90, 'priority': 9, 'scope': {'global': True}})
        data['items'][0]['estimated_seconds'] = 10
        self.assertEqual(scan_cycle.advance(data)['work'], [])


class ChannelSetup(unittest.TestCase):
    def data(self):
        payload = {'recipient': '+61400000000', 'device_id': 'owned-phone', 'sender_number': '+61400000001'}
        return {'invocation_policy': 'one-cycle-approved-work', 'context_key': 'enquiry-one',
            'channel_verified': False, 'inbound_reader_available': False,
            'guards': dict.fromkeys(('stop', 'manual_pause', 'unknown_attempt', 'customer_replied'), False),
            'payload': payload, 'now': '2026-11-02T01:00:00Z', 'controlled_sms_test': payload | {
                'enabled': True, 'max_messages': 1, 'authorization_ref': 'original-init-input',
                'context_key': 'enquiry-one', 'expires_at': '2026-11-02T02:00:00Z',
                'used_slots': 0, 'unknown_attempt': False}}

    def test_explicit_one_message_exception_never_certifies_ordinary_readiness(self):
        data = self.data(); r = sms_channel.gate(data)
        self.assertEqual(r['status'], 'ChannelCheckEligible')
        self.assertFalse(r['ordinary_readiness_verified']); self.assertFalse(r['send_authorized'])
        data['channel_verified'] = data['inbound_reader_available'] = True
        self.assertEqual(sms_channel.gate(data)['mode'], 'ordinary')

    def test_used_unknown_expired_foreign_or_unscoped_check_stays_blocked(self):
        for patch in ({'used_slots': 1}, {'max_messages': True}, {'unknown_attempt': True}, {'recipient': '+61400000002'},
                      {'expires_at': '2026-11-02T00:00:00Z'}, {'authorization_ref': ''}, {'context_key': 'other'}):
            data = self.data(); data['controlled_sms_test'].update(patch)
            with self.subTest(patch=patch): self.assertEqual(sms_channel.gate(data)['status'], 'ChannelCheckBlocked')

    def test_only_own_original_reserved_attempt_can_continue_before_request(self):
        data = self.data(); data['attempt_id'] = 'attempt1'
        data['controlled_sms_test'].update(used_slots=1, reserved_attempt_id='attempt1', provider_result_present=False)
        self.assertEqual(sms_channel.gate(data)['status'], 'ChannelCheckEligible')
        data['controlled_sms_test']['provider_result_present'] = True
        self.assertEqual(sms_channel.gate(data)['status'], 'ChannelCheckBlocked')

    def test_no_send_policy_or_new_stop_cannot_be_waived(self):
        for k in ('stop', 'manual_pause', 'unknown_attempt', 'customer_replied'):
            data = self.data(); data['guards'][k] = True
            self.assertEqual(sms_channel.gate(data)['status'], 'ChannelCheckBlocked')
        for policy in ('report-only', 'draft-only', 'setup-only', 'one-cycle-no-customer-send'):
            data = self.data(); data['invocation_policy'] = policy
            with self.assertRaises(ValueError): sms_channel.gate(data)


if __name__ == '__main__': unittest.main()
