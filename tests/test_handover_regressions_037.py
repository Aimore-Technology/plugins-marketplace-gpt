"""Forward gates and current-result regressions from the 0.1.36 rehearsal."""

import copy
import json
import re
import unittest
from unittest.mock import patch

from test_execution_preflight import request, PREFLIGHT, capture as saved_plan
from test_notion_mutation import update
from test_email_presentation import fixture as email, apply_plan, page, block, SEND, REVIEW
from fixtures_intake import handoff, ROOT, SOURCE, KEY, capture
import email_presentation
import intake_handoff
import invocation_context
import local_checks
import notion_mutation
import notion_checks
import runtime_records
import scan_cycle


def mutation(body, edits):
    return {'target': capture(SOURCE, body), 'call': {
        'tool': 'mcp__notion__notion_notion_update_page', 'args': {
            'page_id': SOURCE, 'command': 'update_content', 'content_updates': edits}}}


class IntakeOrdering(unittest.TestCase):
    def test_prospective_plan_needs_actual_readback_and_preserves_old_capture(self):
        data = handoff(); data['invocation_id'] = 'new-intake'
        data['checkpoint_page']['text'] = data['checkpoint_page']['text'].replace('"completed"', '"waiting"')
        before = copy.deepcopy(data)
        planned = intake_handoff.plan(data)
        self.assertTrue(planned['must_save_and_read_back'])
        with self.assertRaises(ValueError): intake_handoff.verify(data)
        saved = copy.deepcopy(data); old, _ = email_presentation.blocks(data['checkpoint_page'], 'scan-checkpoint-v1')
        saved['checkpoint_page']['text'] = saved['checkpoint_page']['text'].replace(old, block(planned['checkpoint']))
        self.assertEqual(intake_handoff.verify(saved)['status'], 'IntakeHandoffVerified')
        self.assertEqual(data, before)

    def test_new_source_version_does_not_consume_old_unknown_intake(self):
        data = handoff(); data['invocation_id'] = 'new-intake'
        data['checkpoint_page']['text'] = data['checkpoint_page']['text'].replace('"completed"', '"unknown"')
        data['source_page']['text'] = data['source_page']['text'].replace('source-v1', 'source-v2')
        with self.assertRaisesRegex(ValueError, 'unknown intake'): intake_handoff.plan(data)

    def test_reply_patch_cannot_borrow_another_sources_completed_receipt(self):
        from test_reply_transport import fixture
        data = request(); data.update(operation='reply-patch', reply=fixture())
        data['reply']['manifest']['reply_message_id'] = 'another-source'
        with self.assertRaisesRegex(ValueError, 'Reply transport differs'): PREFLIGHT.prepare(data)

    def test_missing_intake_stops_before_fact_preparation_or_any_call(self):
        data = request(); del data['intake_handoff']
        with patch.object(PREFLIGHT, 'canonical_facts') as facts:
            with self.assertRaises(KeyError): PREFLIGHT.prepare(data)
            facts.assert_not_called()

    def test_saved_source_without_completed_handoff_has_no_execution_plan(self):
        data = request()
        data['intake_handoff']['checkpoint_page']['text'] = data['intake_handoff']['checkpoint_page']['text'].replace('"completed"', '"waiting"')
        result = PREFLIGHT.prepare(data)
        self.assertEqual(result['status'], 'NeedsCorrection')
        self.assertNotIn('execution_plan', result)
        self.assertNotIn('outputs', result)

    def test_wrong_root_source_receipt_version_and_truncated_capture_refuse(self):
        changes = [lambda d: d.update(root_id='a' * 32), lambda d: d.update(source_key='other'),
                   lambda d: d.update(source_version='other'),
                   lambda d: d['checkpoint_page'].update(text=d['checkpoint_page']['text'].replace(SOURCE, 'b' * 32)),
                   lambda d: d['source_page'].update(truncated=True)]
        for edit in changes:
            data = handoff(); edit(data)
            with self.assertRaises(ValueError): intake_handoff.verify(data)

    def test_actual_durable_source_is_frozen_and_readback_not_retrospective_order(self):
        data = request(); original = copy.deepcopy(data)
        prepared = PREFLIGHT.prepare(data)
        ready = PREFLIGHT.ready({'prepared': prepared, 'saved_plan': saved_plan(prepared)})
        self.assertEqual(ready['status'], 'ExecutionPlanReady')
        self.assertEqual(prepared['outputs']['intake_handoff']['source_page_id'], SOURCE)
        self.assertEqual(data, original)
        changed = copy.deepcopy(prepared); changed['outputs'].pop('intake_handoff')
        with self.assertRaises(ValueError): PREFLIGHT.ready({'prepared': changed, 'saved_plan': saved_plan(prepared)})


class PublicationBinding(unittest.TestCase):
    def setUp(self):
        self.binding = {'record_type': 'action-binding', 'TaskPageId': SOURCE,
                        'ActionPageId': 'b' * 32, 'ContentVersion': 'notes-v1'}
        self.body = '## Current status\n\nWaiting.\n\n## Processing result\n\nPending.\n\n' + block(self.binding)

    def test_status_patch_preserves_binding_but_whole_page_drop_is_refused(self):
        data = mutation(self.body, [{'old_str': 'Pending.', 'new_str': 'Verified; no further input.'}])
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')
        data['call']['args'] = {'page_id': SOURCE, 'command': 'replace_content',
                              'new_str': '## Current status\n\nCompleted.\n\n## Processing result\n\nSaved.'}
        with self.assertRaisesRegex(ValueError, 'original action-binding'): notion_mutation.prepare(data)

    def test_same_version_payload_and_identity_cannot_be_rebound(self):
        for field in ('TaskPageId', 'ActionPageId', 'ContentVersion'):
            other = self.binding | {field: 'c' * 32}
            data = mutation(self.body, [{'old_str': block(self.binding), 'new_str': block(other)}])
            with self.assertRaises(ValueError): notion_mutation.prepare(data)

    def test_duplicate_sections_fail_before_write_and_atomic_cleanup_is_allowed(self):
        data = mutation(self.body, [])
        data['call']['args'] = {'page_id': SOURCE, 'command': 'insert_content',
                              'content': '## Current status\n\nAnother current copy.'}
        with self.assertRaisesRegex(ValueError, 'Duplicate current'): notion_mutation.prepare(data)
        duplicated = self.body + '\n\n## Current status\n\nExtra.\n'
        data = mutation(duplicated, [{'old_str': '\n\n## Current status\n\nExtra.\n', 'new_str': ''}])
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')

    def test_literal_code_does_not_create_a_duplicate_heading(self):
        data = mutation(self.body, [{'old_str': 'Pending.', 'new_str': 'Verified.\n\n```txt\n## Current status\n```'}])
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')

    def test_new_send_package_keeps_source_but_legacy_package_is_preserved(self):
        package = {'record_type': 'sales-send-package', 'content_version': 'v1'}
        data = mutation('Inert preparation.', [{'old_str': 'Inert preparation.', 'new_str': block(package)}])
        with self.assertRaisesRegex(ValueError, 'source_page_id'): notion_mutation.prepare(data)
        data['call']['args']['content_updates'][0]['new_str'] = block(package | {'source_page_id': SOURCE})
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')
        data = mutation(block(package) + '\nOld label.', [{'old_str': 'Old label.', 'new_str': 'Current result.'}])
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')


class CurrentEmailResults(unittest.TestCase):
    def test_task_body_and_original_source_match_success_without_touching_payload(self):
        data = email(False)
        for role in ('send_task', 'review_task'):
            old = email_presentation.page_body(data['pages'][role])
            data['pages'][role]['text'] = data['pages'][role]['text'].replace(old,
                '## Current status\n\nUnsent.\n\n## Processing result\n\nWaiting.\n\n' + old)
        source = handoff()['source_page']
        props = email_presentation.properties(source) | {'Account': 'operator@example.com', 'ThreadId': 'thread-1', 'State': 'WaitingForOperator', 'Result': 'Unsent.'}
        data['source_page'] = capture(SOURCE, '## Current status\n\nWaiting for review.\n\n## Original mail\n\nKeep every original byte.', props)
        task = data['pages']['send_task']; raw, package = email_presentation.blocks(task, 'sales-send-package')
        package['source_page_id'] = SOURCE; package['transport_manifest']['reply_message_id'] = 'source-1'
        task['text'] = task['text'].replace(raw, block(package))
        raw, proof = email_presentation.blocks(task, 'email-sent-proof')
        proof['record_type'] = 'email-handoff-proof'
        proof['verification'].update(status='ProviderHandoffVerified', phase='handoff')
        task['text'] = task['text'].replace(raw, block(proof))
        saved = apply_plan(data); data['saved_source_page'] = saved.pop('source'); data['saved_pages'] = saved
        self.assertEqual(email_presentation.verify(data)['status'], 'EmailPresentationVerified')
        for role in ('send_task', 'review_task'):
            self.assertIn('Submitted to Gmail', email_presentation.page_body(saved[role]))
            self.assertEqual(email_presentation.blocks(saved[role], 'action-binding'), email_presentation.blocks(data['pages'][role], 'action-binding'))
        self.assertEqual(email_presentation.properties(data['saved_source_page'])['State'], 'Processing')
        self.assertEqual(email_presentation.plan(data)['source_completion'], {
            'entity_id': SOURCE, 'state': 'Processed', 'requires': 'FullOwnerCompletion'})
        self.assertIn('Keep every original byte.', email_presentation.page_body(data['saved_source_page']))
        repeat = data | {'pages': saved, 'source_page': data['saved_source_page']}
        self.assertEqual(email_presentation.plan(repeat)['updates'], [])
        data.pop('source_page')
        with self.assertRaisesRegex(ValueError, 'source_page_id'): email_presentation.plan(data)

    def test_inbox_processed_marker_cannot_bypass_the_final_owner_gate(self):
        data = {'registry': {'owner_skill': 'eightdegrees-sales-reply', 'policy': 'owner-workflow',
                            'publication_page_ids': [SOURCE]}, 'call': {
                'tool': 'mcp__notion__notion_notion_update_page', 'args': {
                    'page_id': SOURCE, 'command': 'update_properties', 'properties': {'State': 'Processed'}}}}
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')


class CheckpointAndRecovery(unittest.TestCase):
    def checkpoint(self, state='waiting'):
        record = {'record_type': 'scan-checkpoint-v1', 'root_id': ROOT, 'invocation_id': 'past', 'streams': {},
                  'items': {'item': {'source_key': 'original-task', 'version': 'notes-v1', 'step': 'ReviewCommunication',
                                     'state': state, 'receipt_ref': SOURCE, 'attempt_id': 'keep-attempt'}}}
        task = capture(SOURCE, 'Original accepted result.', {'TaskId': 'original-task', 'ContentVersion': 'notes-v1',
            'ResumeStep': 'ReviewCommunication', 'State': 'Completed'})
        return {'root_id': ROOT, 'checkpoint_page': capture('6' * 32, block(record)), 'task_pages': [task]}

    def test_terminal_task_retires_waiting_pointer_preserving_unknown_and_old_capture(self):
        for terminal in ('Completed', 'Cancelled'):
            data = self.checkpoint(); data['task_pages'][0]['text'] = data['task_pages'][0]['text'].replace('"Completed"', json.dumps(terminal))
            original = copy.deepcopy(data)
            result = scan_cycle.reconcile(data)
            self.assertEqual(result['checkpoint']['items']['item']['state'], terminal.lower())
            self.assertEqual(data, original)
        data = self.checkpoint('unknown'); result = scan_cycle.reconcile(data)
        self.assertEqual(result['changes'], [])
        self.assertEqual(result['checkpoint']['items']['item']['attempt_id'], 'keep-attempt')

    def test_other_version_or_task_never_clears_a_wait(self):
        data = self.checkpoint(); data['task_pages'][0]['text'] = data['task_pages'][0]['text'].replace('notes-v1', 'notes-v2')
        with self.assertRaises(ValueError): scan_cycle.reconcile(data)

    def test_legacy_waiting_work_item_without_item_identity_is_removed_from_current_queue(self):
        data = self.checkpoint()
        record = email_presentation.blocks(data['checkpoint_page'], 'scan-checkpoint-v1')[1]
        work = {'source_key': 'original-task', 'step': 'ReviewCommunication', 'version': 'notes-v1',
                'input_digest': 'unsubmitted', 'waiting': True}
        record['items'] = {}
        record['work_items'] = [work]
        data['checkpoint_page'] = capture('6' * 32, block(record))
        result = scan_cycle.reconcile(data)
        self.assertEqual(result['checkpoint']['work_items'], [])
        self.assertEqual(result['checkpoint']['items'][scan_cycle.key(work)]['state'], 'completed')
        record['items'][scan_cycle.key(work)] = {'state': 'unknown', 'attempt_id': 'keep-unknown'}
        data['checkpoint_page'] = capture('6' * 32, block(record))
        result = scan_cycle.reconcile(data)
        self.assertEqual(result['checkpoint']['work_items'], [work])
        self.assertEqual(result['changes'], [])

    def context(self):
        inputs = {'command': 'run-auto', 'invocation_id': 'current-turn', 'executor_id': 'this-thread',
                  'root_id': ROOT, 'started_at': '2026-11-02T00:00:00Z', 'receipt_page_ids': [SOURCE]}
        record = invocation_context.prepare(inputs)['record']
        return inputs | {'context_page': capture('5' * 32, block(record)), 'now': '2026-11-02T00:05:00Z'}

    def test_compaction_keeps_command_role_budget_and_receipt_pointers(self):
        data = self.context(); result = invocation_context.resume(data)
        self.assertEqual(result['remaining_seconds'], 600)
        self.assertFalse(result['peer_session_control_allowed'])
        self.assertFalse(result['external_actions_allowed'])
        self.assertEqual(result['receipt_pages_to_read'], [SOURCE])
        data['now'] = '2026-11-02T00:16:00Z'
        self.assertTrue(invocation_context.resume(data)['closeout_only'])

    def test_original_local_pin_needs_no_fabricated_notion_page_and_cannot_reset_start(self):
        data = self.context(); record = email_presentation.blocks(data.pop('context_page'), 'invocation-context-v1')[1]
        data['context_record'] = record
        self.assertEqual(invocation_context.resume(data)['remaining_seconds'], 600)
        record['started_at'] = '2026-11-02T00:01:00Z'; record['deadline'] = '2026-11-02T00:16:00+00:00'
        with self.assertRaisesRegex(ValueError, 'original invocation start'): invocation_context.resume(data)

    def test_publication_cannot_drop_or_reset_pin_but_can_append_original_receipts(self):
        record = email_presentation.blocks(self.context()['context_page'], 'invocation-context-v1')[1]
        body = block(record)
        updated = record | {'receipt_page_ids': record['receipt_page_ids'] + ['a' * 32]}
        data = mutation(body, [{'old_str': body, 'new_str': block(updated)}])
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')
        for new in ['No recovery pin.', block(record | {'deadline': '2026-11-03T00:15:00Z'})]:
            data['call']['args']['content_updates'][0]['new_str'] = new
            with self.assertRaises(ValueError): notion_mutation.prepare(data)

    def test_wrong_local_run_command_or_reset_deadline_cannot_resume(self):
        for key in ('command', 'invocation_id'):
            data = self.context(); data[key] = 'report' if key == 'command' else 'other'
            with self.assertRaises(ValueError): invocation_context.resume(data)
        data = self.context(); data['context_page']['text'] = data['context_page']['text'].replace('00:15:00+00:00', '01:15:00+00:00')
        with self.assertRaises(ValueError): invocation_context.resume(data)

    def test_legacy_summary_never_fills_metadata_or_changes_old_state(self):
        data = update(); old_run = {'RecordType': 'Business', 'RunId': 'old-run', 'Skill': 'eightdegrees-sms-follow-up',
                                   'SkillVersion': '', 'SourceKey': '', 'State': 'InProgress'}
        data['target']['text'] = re.sub(r'<properties>.*?</properties>', lambda m: '<properties>'+json.dumps(old_run)+'</properties>', data['target']['text'], flags=re.S)
        data['legacy_task_page'] = capture(SOURCE, 'Cancelled at original expiry.', {
            'State': 'Cancelled', 'OwnerSkill': old_run['Skill'], 'RunId': old_run['RunId'],
            'ContentVersion': 'v1', 'TaskId': 'original-task'})
        fixed = runtime_records.legacy_projection({'run_page': data['target'], 'task_page': data['legacy_task_page']})
        data['call']['args']['properties'] = fixed['properties']
        self.assertEqual(notion_mutation.prepare(data)['status'], 'NotionMutationPrepared')
        data['call']['args']['properties']['State'] = 'Completed'
        with self.assertRaises(ValueError): notion_mutation.prepare(data)


if __name__ == '__main__':
    unittest.main()
