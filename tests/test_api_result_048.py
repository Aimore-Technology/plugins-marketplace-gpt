"""Receipt-first completion, bounded reads and compact current-rule loading."""
import copy
import json
from unittest.mock import patch
import unittest

from test_execution_preflight import request, PREFLIGHT, RUN, TASK
from test_reply_transport import fixture, ADAPTER
from test_scheduled_outcomes import receipt_input
from test_crm_note import payload
from test_pre_action_order import dispatch, ready, review
from fixtures_intake import handoff

import api_result
import communication_intake
import crm_note
import current_rules
import dispatch_admission
import intake_handoff
import local_checks
import notion_checks
import review_release
import scan_control
import send_receipt


def write(identity, **kwargs):
    return {'response': {'id': identity}, 'request': {}, **kwargs}


def prepared():
    data = request(); data.pop('verification_mode')
    return PREFLIGHT.prepare(data)


def completion():
    original = prepared()
    ready_result = PREFLIGHT.ready({'prepared': original, 'run_write': write(RUN)})
    registry = ready_result['registry']
    checks = []
    for name, spec in registry['required_checks'].items():
        if spec['kind'] == 'execution-plan':
            result = ready_result
        elif spec['kind'] == 'route':
            result = {'status': 'EligibleForOwnerCheck', 'entity_id': spec['entity_id'],
                      'content_version': 'reply-v2', 'resume_step': spec['resume_step'],
                      'owner': registry['owner_skill'], 'policy': registry['policy'], 'phase': 'execute'}
        else:
            result = api_result.confirm({**write(spec['entity_id'] if spec['service'] == 'notion' else 'draft-id'),
                                         **spec, 'purpose': spec['purpose']})
        checks.append({'name': name, 'result': result, 'exit_code': 0,
                       'invocation_id': registry['invocation_id'], 'publication_version': registry['publication_version']})
    return {'registry': registry,
            'completion': {'required_checks': copy.deepcopy(registry['required_checks']), 'checks': checks,
                           'invocation_id': registry['invocation_id'], 'publication_version': registry['publication_version']},
            'call': {'tool': 'mcp__notion__notion_notion_update_page', 'args': {
                'command': 'update_properties', 'page_id': TASK, 'properties': {'State': 'Completed'}}}}


class APIWriteResults(unittest.TestCase):
    def test_success_needs_only_returned_id_not_saved_body(self):
        for service in api_result.SERVICES:
            result = api_result.confirm({**write('actual-id'), 'service': service})
            self.assertEqual(result['status'], 'APIWriteConfirmed')
            self.assertFalse(result['stored_content_verified'])
            self.assertFalse(result['retry_allowed'])

    def test_wrapper_and_note_envelopes_work_without_body(self):
        for value in ({'note': {'id': 'note-1'}}, {'data': {'noteId': 'note-1'}},
                      {'structuredContent': {'id': 'note-1'}, 'isError': False},
                      {'content': [{'type': 'text', 'text': '{"id":"note-1"}'}]}):
            self.assertEqual(api_result.confirm({'service': 'crm', 'response': value})['record_id'], 'note-1')

    def test_update_success_without_body_retains_known_id(self):
        for response in ({'success': True}, {'statusCode': 204}, {'content': [{'type': 'text', 'text': 'Action completed.'}]}):
            result = api_result.confirm({'service': 'notion', 'response': response, 'expected_id': RUN})
            self.assertEqual(result['record_id'], RUN)

    def test_empty_or_error_layers_do_not_mean_success(self):
        for response in ({'isError': False}, {}, {'isError': True, 'id': 'x'},
                         {'structuredContent': {'id': 'x'}, 'content': [{'type': 'text', 'text': '{"error":"denied"}'}]},
                         {'data': {'success': False, 'id': 'x'}}):
            self.assertEqual(api_result.confirm({'service': 'crm', 'response': response})['status'], 'NeedsReconciliation')

    def test_unknown_uses_scoped_existence_not_content(self):
        result = api_result.confirm({'service': 'crm', 'response': {'isError': True},
                                     'expected_id': 'note-1', 'existence_response': {'id': 'note-1'}})
        self.assertEqual(result['verification_basis'], 'record-exists')
        self.assertNotIn('body', result)
        with self.assertRaises(ValueError):
            api_result.confirm({'service': 'crm', 'response': {}, 'existence_response': {'id': 'random'}})

    def test_wrong_case_sensitive_crm_id_and_known_refusal_cannot_pass(self):
        result = api_result.confirm({'service': 'crm', 'expected_id': 'NoteA', 'response': {'id': 'notea'}})
        self.assertEqual(result['status'], 'NeedsReconciliation')
        result = api_result.confirm({'service': 'crm', 'expected_id': 'note-1',
                                     'response': {'statusCode': 403}, 'existence_response': {'id': 'note-1'}})
        self.assertEqual(result['status'], 'NeedsReconciliation')

    def test_batch_create_requires_actual_selected_id(self):
        response = {'pages': [{'id': RUN}, {'id': TASK}]}
        with self.assertRaises(ValueError):
            api_result.confirm({'service': 'notion', 'response': response})
        self.assertEqual(api_result.confirm({'service': 'notion', 'response': response, 'expected_id': TASK})['record_id'], TASK)

    def test_default_plan_uses_receipts_and_ready_never_reads_saved_content(self):
        result = prepared()
        self.assertEqual(result['execution_plan']['contract_version'], api_result.CONTRACT)
        with patch.object(PREFLIGHT, 'page_body', side_effect=AssertionError('No readback')):
            ready_result = PREFLIGHT.ready({'prepared': result, 'run_write': write(RUN)})
        self.assertEqual(ready_result['status'], 'ExecutionPlanReady')
        with self.assertRaises(ValueError):
            PREFLIGHT.ready({'prepared': result, 'run_write': write(TASK)})

    def test_receipt_completion_preserves_affected_scope_and_versions(self):
        data = completion()
        self.assertEqual(notion_checks.owner_write(data)['status'], 'WithinOwnerScope')
        data['call']['args']['page_id'] = 'f' * 32
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')
        data = completion()
        next(c for c in data['completion']['checks'] if c['result'].get('purpose') == 'reply-draft')['result']['content_version'] = 'old'
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')

    def test_missing_draft_receipt_cannot_finish_and_future_send_is_not_required(self):
        data = completion()
        kinds = {s['kind'] for s in data['registry']['required_checks'].values()}
        self.assertNotIn('provider-handoff', kinds)
        self.assertFalse(any(s.get('purpose') in {'crm-note', 'material-handoff'} for s in data['registry']['required_checks'].values()))
        data['completion']['checks'] = [c for c in data['completion']['checks'] if c['result'].get('purpose') != 'reply-draft']
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')

    def test_send_requires_real_dispatch_crm_and_registration_receipts(self):
        data = request(); data.pop('verification_mode')
        data.update(policy='owner-workflow', operation='review')
        data['resources'][1]['resume_step'] = 'SendApprovedReply'
        required = PREFLIGHT.prepare(data)['execution_plan']['required_checks']
        self.assertTrue({'crm-note', 'material-handoff'} <= {s.get('purpose') for s in required.values()})
        self.assertIn('provider-handoff', {s['kind'] for s in required.values()})
        self.assertNotIn('reply-draft', {s.get('purpose') for s in required.values()})
        data['policy'] = 'draft-only'
        with self.assertRaises(ValueError):
            PREFLIGHT.prepare(data)

    def test_unmatched_inquiry_can_finish_send_with_separate_crm_recovery(self):
        data = request(); data.pop('verification_mode')
        data.update(policy='owner-workflow', operation='review')
        task = data['resources'][1]
        task.update(resume_step='SendApprovedReply', crm_recording='pending-unmatched',
                    crm_match='none', crm_search_complete=True, crm_pending_task_id='f' * 32)
        specs = PREFLIGHT.prepare(data)['execution_plan']['required_checks']
        self.assertIn('crm-pending', {s.get('purpose') for s in specs.values()})
        self.assertNotIn('crm-note', {s.get('purpose') for s in specs.values()})
        task['crm_match'] = 'matched'
        with self.assertRaises(ValueError):
            PREFLIGHT.prepare(data)

    def test_completion_cannot_drop_its_crm_or_other_generated_obligations(self):
        data = completion()
        name = next(name for name in data['registry']['required_checks'] if name.endswith(':reply-draft'))
        data['registry']['required_checks'].pop(name)
        data['completion']['required_checks'].pop(name)
        data['completion']['checks'] = [c for c in data['completion']['checks'] if c['name'] != name]
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')

    def test_crm_receipt_success_never_reads_body(self):
        data = receipt_input(); data['write_result'] = write('note-1')
        result = send_receipt.verify(data)
        self.assertEqual(result['status'], 'CRMReceiptVerified')
        self.assertFalse(result['stored_content_verified'])

    def test_gmail_draft_ack_does_not_require_raw_mime_but_keeps_payload_binding(self):
        data = fixture(); data.pop('message'); data.pop('draft')
        data['write_result'] = write(data['manifest']['draft_id'])
        result = ADAPTER.verify(data)
        self.assertEqual(result['status'], 'StoredReplyVerified')
        self.assertFalse(result['stored_content_verified'])
        data['manifest']['html_sha256'] = 'f' * 64
        with self.assertRaises(ValueError):
            ADAPTER.verify(data)

    def test_intake_and_admission_accept_original_api_response(self):
        data = handoff()
        record = json.loads(data.pop('checkpoint_page')['text'].split('```json\n')[1].split('\n```')[0])
        data.update(checkpoint_record=record, checkpoint_page_id='7' * 32, checkpoint_write=write('7' * 32))
        self.assertEqual(intake_handoff.verify(data)['status'], 'IntakeHandoffVerified')
        admission = ready(dispatch()); admission.pop('saved_run')
        admission['admission_write'] = write(admission['run_page_id'])
        self.assertEqual(dispatch_admission.release(admission)['status'], 'DispatchArgumentsPrepared')

    def test_stop_write_confirmation_does_not_need_settings_readback(self):
        result = scan_control.verify({'operation': 'stop', 'settings': {}, 'write_result': write(RUN)})
        self.assertEqual(result['status'], 'ScanningStopped')
        self.assertEqual(scan_control.gate({'settings': {'scan_control': {'contract': 'scan-control-v1', 'enabled': False}}})['status'], 'ScanStopped')

    def test_review_can_release_from_published_ids_without_downloads(self):
        data = review(); data['transport'].pop('message'); data['transport'].pop('draft')
        data['transport']['write_result'] = write(data['transport']['manifest']['draft_id'])
        data['preview']['input']['content_version'] = data['transport']['manifest']['content_version']
        data['publication_writes'] = {role: write(identity) for role, identity in
                                      [('copy', '1' * 32), ('asset', '2' * 32), ('preview', '3' * 32)]}
        data['prepared_copy'] = {key: data['transport']['manifest'][key]
                                 for key in ('task_page_id', 'content_version', 'subject', 'html_sha256')}
        data.pop('copy_page')
        with patch.object(review_release, 'check_preview', side_effect=AssertionError('No download')):
            self.assertEqual(review_release.prepare(data)['status'], 'EmailReviewReady')
        data['preview']['input']['html_sha256'] = 'f' * 64
        with self.assertRaises(ValueError):
            review_release.prepare(data)

    def test_current_rules_default_keeps_python_out_but_fingerprints_it(self):
        compact, full = current_rules.load(), current_rules.load({'include_code': True})
        self.assertEqual(compact['rule_sha256'], full['rule_sha256'])
        self.assertIn('scripts/api_result.py', compact['rule_files'])
        self.assertNotIn('scripts/api_result.py', compact['rules'])
        self.assertIn('references/api-result-policy.md', compact['rules'])
        self.assertLess(len(json.dumps(compact)), len(json.dumps(full)) * .6)

    def test_provided_text_and_notes_use_bounded_reads_and_fixed_renderer(self):
        result = communication_intake.plan({'source_kind': 'provided-text'})
        self.assertFalse(any('supplied authorized' in read for read in result['reads']))
        self.assertIn('mailbox scanning', result['skip'])
        rendered = communication_intake.note({'payload': payload()})
        self.assertEqual(rendered['note'].encode(), crm_note.render(payload()))
        self.assertFalse(rendered['crm_write_allowed'])
        bad = payload(); bad['sections']['action'] = ['**wrong format**']
        with self.assertRaises(ValueError):
            communication_intake.note({'payload': bad})

    def test_failed_write_in_batch_emits_no_dependent_completion(self):
        result = local_checks.run({'checks': [
            {'name': 'write', 'operation': 'write.confirm', 'input': {'service': 'crm', 'response': {'isError': True}}},
            {'name': 'render', 'operation': 'communication.note', 'input': {'payload': payload()}}]}, {})
        self.assertEqual(result['status'], 'NeedsCorrection')
        self.assertEqual(result['checks_run'], 1)


if __name__ == '__main__':
    unittest.main()
