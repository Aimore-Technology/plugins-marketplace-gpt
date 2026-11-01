"""Recovery, source-bound stops and related status projections without providers."""

import copy
import hashlib
import json
import unittest

from test_email_presentation import page, block, fixture as email_fixture, apply_plan
import email_presentation
import sms_presentation
import contact_preferences
import scan_cycle

IDS = {k: format(i, '032x') for i, k in enumerate(sorted(sms_presentation.ROLES), 10)}


def sms_fixture(status='SentToNetwork', version='v1'):
    task = IDS['notification']
    digest = hashlib.sha256(b'Material email sent.').hexdigest()
    frozen = {'contract': 'sms-notification-v1', 'task_id': task, 'content_version': version,
              'body': 'Material email sent.', 'body_sha256': digest, 'recipient': '+61400000000', 'device_id': 'phone'}
    attempt = {'record_type': 'sms-send-attempt', 'attempt_id': 'attempt1', 'payload_sha256': digest,
               **{k: frozen[k] for k in ('body', 'recipient', 'device_id', 'content_version')}}
    provider = {'record_type': 'sms-provider-result', 'attempt_id': 'attempt1', 'payload_sha256': digest,
                'provider_result': {'Id': 'message1', 'Status': 'AwaitingPhone'}}
    outcome = {'record_type': 'sms-current-outcome', 'task_id': task, 'content_version': version,
               'attempt_id': 'attempt1', 'message_id': 'message1', 'provider_status': 'AwaitingPhone',
               'provider': {'status': 'AwaitingPhone'}, 'sent': False, 'reserved': True,
               'provider_delivered': False, 'human_received': False, 'payload_sha256': digest,
               'observed_at': '2026-11-01T01:00:00Z'}
    cycle = {'record_type': 'sms-cycle-current-state', 'cycle_id': 'cycle1',
             'cycle_page_id': IDS['cycle'], 'task_page_id': IDS['data_task'],
             'action_page_id': IDS['data_action'], 'run_page_id': IDS['data_run'],
             'current_outcome': outcome, 'stop': True, 'active': False, 'next_due': None,
             'reserved_count': 1, 'total_count': 1, 'known_this_executor_sent': 0, 'count_verified': True}
    action = '## Current status\n\nAwaitingPhone old status\n\n## Input history\n\n- [x] submitted\n\n## Processing result\n\nAwaitingPhone old result'
    pages = {'notification': page(task, '\n\n'.join(map(block, [frozen, attempt, provider, outcome])),
                    {'State': 'InProgress', 'OwnerSkill': sms_presentation.OWNER, 'ContentVersion': version,
                     'StepId': 'SendNotificationSms', 'ResumeStep': 'SendNotificationSms',
                     'CycleId': 'cycle1', 'ActionPageURL': IDS['result'], 'RunId': 'send-run'}),
             'result': page(IDS['result'], action + '\n\n' + block(outcome), {}),
             'data_task': page(IDS['data_task'], 'Original accepted input', {'State': 'Completed',
                    'OwnerSkill': sms_presentation.OWNER, 'ContentVersion': version, 'CycleId': 'cycle1',
                    'StepId': 'PrepareSmsFollowUp', 'ResumeStep': 'PrepareSmsFollowUp',
                    'ActionPageURL': IDS['data_action'], 'RunId': 'data-run'}),
             'data_action': page(IDS['data_action'], action, {}),
             'cycle': page(IDS['cycle'], block(cycle), {})}
    for role, run in [('send_run', 'send-run'), ('data_run', 'data-run')]:
        pages[role] = page(IDS[role], 'Immutable execution plan', {'Skill': sms_presentation.OWNER,
                         'RunId': run, 'State': 'WaitingForOperator', 'CurrentStep': 'AwaitingPhone'})
    return {'pages': pages, 'provider_status': {'id': 'message1', 'status': status, 'deviceId': 'phone'},
            'observed_at': '2026-11-01T02:00:00Z'}


def saved_sms(data):
    pages = copy.deepcopy(data['pages'])
    for update in sms_presentation.plan(data)['updates']:
        capture = pages[update['role']]
        for edit in update.get('content_updates', []):
            capture['text'] = capture['text'].replace(edit['old_str'], edit['new_str'], 1)
        if 'properties' in update:
            old = email_presentation.properties(capture)
            capture['text'] = capture['text'].replace(json.dumps(old), json.dumps(old | update['properties']), 1)
    return pages


class SMSRecovery(unittest.TestCase):
    def test_failed_does_not_claim_success_or_release_unknown_by_retry(self):
        data = sms_fixture('Failed'); saved = saved_sms(data)
        self.assertEqual(email_presentation.properties(saved['send_run'])['State'], 'Error')
        self.assertEqual(email_presentation.blocks(saved['cycle'], 'sms-cycle-current-state')[1]['total_count'], 1)
        self.assertEqual(sms_presentation.plan(data | {'pages': saved})['updates'], [])

    def test_missing_original_or_partial_capture_cannot_complete_repair(self):
        data = sms_fixture(); data['pages'].pop('data_run')
        with self.assertRaises(ValueError): sms_presentation.plan(data)
        data = sms_fixture(); data['pages']['cycle']['truncated'] = True
        with self.assertRaises(ValueError): sms_presentation.plan(data)

    def test_pending_to_network_updates_original_runs_and_actions_without_replay(self):
        data = sms_fixture(); before = copy.deepcopy(data)
        saved = saved_sms(data)
        self.assertEqual(sms_presentation.verify(data | {'saved_pages': saved})['status'], 'SMSPresentationVerified')
        cycle = email_presentation.blocks(saved['cycle'], 'sms-cycle-current-state')[1]
        self.assertEqual(cycle['known_this_executor_sent'], 1)
        self.assertEqual(cycle['total_count'], 1)
        self.assertEqual(cycle['reserved_count'], 0)
        self.assertTrue(cycle['stop']); self.assertFalse(cycle['active']); self.assertIsNone(cycle['next_due'])
        self.assertEqual(email_presentation.properties(saved['send_run'])['State'], 'Completed')
        self.assertEqual(email_presentation.properties(saved['notification'])['State'], 'Completed')
        self.assertIn('- [x] submitted', saved['data_action']['text'])
        for role in ('notification', 'data_task', 'data_run', 'send_run', 'result', 'data_action'):
            self.assertIn('SentToNetwork', saved[role]['text'])
        for kind in ('sms-send-attempt', 'sms-provider-result'):
            self.assertEqual(email_presentation.blocks(before['pages']['notification'], kind),
                             email_presentation.blocks(saved['notification'], kind))
        self.assertEqual(sms_presentation.plan(data | {'pages': saved})['updates'], [])

    def test_pending_is_machine_wait_not_human_approval(self):
        data = sms_fixture('AwaitingPhone'); saved = saved_sms(data)
        self.assertEqual(email_presentation.properties(saved['send_run'])['State'], 'InProgress')
        self.assertEqual(email_presentation.properties(saved['data_run'])['State'], 'Completed')
        self.assertEqual(email_presentation.blocks(saved['cycle'], 'sms-cycle-current-state')[1]['reserved_count'], 1)

    def test_wrong_request_wrong_device_and_regression_are_refused(self):
        for key, value in [('id', 'another'), ('deviceId', 'another')]:
            data = sms_fixture(); data['provider_status'][key] = value
            with self.assertRaises(ValueError): sms_presentation.plan(data)
        data = sms_fixture(); data['pages'] = saved_sms(data); data['provider_status']['status'] = 'AwaitingPhone'
        with self.assertRaises(ValueError): sms_presentation.plan(data)

    def test_readback_rejects_changes_to_inputs_stop_counts_or_payload(self):
        for role, old, new in [('data_action', '[x]', '[ ]'), ('cycle', '"stop": true', '"stop": false'),
                                ('notification', 'Material email sent.', 'Other text')]:
            data = sms_fixture(); saved = saved_sms(data)
            saved[role]['text'] = saved[role]['text'].replace(old, new)
            self.assertEqual(sms_presentation.verify(data | {'saved_pages': saved})['status'], 'NeedsCorrection')


class EmailSnapshotLabels(unittest.TestCase):
    def test_chinese_live_shape_label_repair_preserves_frozen_package(self):
        data = email_fixture(False)
        heading = '## \u5f53\u524d\u7cbe\u786e\u53d1\u9001\u5305 \u00b7 test-v1'
        text = '\u5f53\u524d\u5c1a\u672a\u63a5\u53d7\u53d1\u9001\u51b3\u5b9a\u3002'
        data['pages']['send_task']['text'] = data['pages']['send_task']['text'].replace('<content>\n', '<content>\n' + heading + '\n\n' + text + '\n\n')
        original = email_presentation.blocks(data['pages']['send_task'], 'sales-send-package')[0]
        saved = apply_plan(data)
        self.assertNotIn(heading, saved['send_task']['text']); self.assertNotIn(text, saved['send_task']['text'])
        self.assertIn(original, saved['send_task']['text'])
        self.assertEqual(email_presentation.plan(data | {'pages': saved})['updates'], [])


def contact_fixture():
    data = email_fixture(); send = data['pages']['send_task']
    package = email_presentation.blocks(send, 'sales-send-package')[1]
    cycle = {'record_type': 'sms-cycle-current-state', 'cycle_id': 'cycle1', 'context_key': 'enquiry1',
             'location_id': 'location1', 'contact_id': 'contact1', 'stop': True}
    handoff = {'contract': 'material-handoff-v1', 'email_task_id': package['transport_manifest']['task_page_id']}
    persona = {'record_type': 'approved-persona-snapshot', 'client_id': 'location1:contact1',
               'facts': {'short_factual_sms_after_email_allowed': True}}
    message = data['receipt']['message']; message['payload']['body']['content'] = 'Please stop SMS for this enquiry.'
    return {'cycle_page': page('a'*32, block(cycle)+'\n'+block(handoff), {}), 'send_task': send,
            'persona_page': page('d'*32, '## Current approved persona\n\n'+block(persona), {}),
            'message': message, 'stop_quote': 'Please stop SMS for this enquiry.', 'explicit_stop': True,
            'scope_confirmed': 'current_enquiry', 'observed_at': '2026-11-01T03:00:00Z'}


class ScopedContactStops(unittest.TestCase):
    def test_saved_overlay_verification_rejects_silent_persona_change(self):
        data = contact_fixture(); result = contact_preferences.stop_overlay(data)
        saved = copy.deepcopy(data['persona_page'])
        for edit in result['updates']: saved['text'] = saved['text'].replace(edit['old_str'], edit['new_str'], 1)
        args = data | {'saved_persona_page': saved, 'maintenance_task_id': 'e'*32}
        self.assertEqual(contact_preferences.verify(args)['status'], 'ContactRestrictionVerified')
        saved['text'] = saved['text'].replace('"short_factual_sms_after_email_allowed": true', '"short_factual_sms_after_email_allowed": false')
        self.assertEqual(contact_preferences.verify(args)['status'], 'NeedsCorrection')

    def test_new_overlay_overrides_old_consent_without_changing_approved_snapshot(self):
        data = contact_fixture(); old = email_presentation.blocks(data['persona_page'], 'approved-persona-snapshot')[0]
        result = contact_preferences.stop_overlay(data)
        saved = copy.deepcopy(data['persona_page'])
        for edit in result['updates']: saved['text'] = saved['text'].replace(edit['old_str'], edit['new_str'])
        self.assertIn(old, saved['text'])
        self.assertEqual(contact_preferences.stop_overlay(data | {'persona_page': saved})['updates'], [])
        restrictions = email_presentation.blocks(saved, 'contact-restrictions-v1')[1]
        args = {'client_id': 'location1:contact1', 'context_key': 'enquiry1', 'restrictions': restrictions, 'cycle': {}}
        self.assertTrue(contact_preferences.dispatch_gate(args)['blocked'])
        self.assertFalse(contact_preferences.dispatch_gate(args | {'context_key': 'other'})['blocked'])

    def test_wrong_thread_sender_quoted_only_and_ambiguous_scope_refused(self):
        for change in ('thread', 'sender', 'quoted', 'scope'):
            data = contact_fixture()
            if change == 'thread': data['message']['thread_id'] = 'other'
            elif change == 'sender': data['message']['payload']['headers'][0]['value'] = 'unknown@example.com'
            elif change == 'quoted': data['message']['payload']['body']['content'] = '> Please stop SMS for this enquiry.'
            else: data['scope_confirmed'] = 'maybe_global'
            with self.assertRaises(ValueError): contact_preferences.stop_overlay(data)


def cycle_fixture():
    item = {'source_key': 'email1', 'step': 'SendApprovedReply', 'version': 'v1', 'input_digest': 'sha1'}
    return {'root_id': 'a'*32, 'started_at': '2026-11-01T00:00:00Z', 'now': '2026-11-01T00:01:00Z',
            'executor': {'current_id': 'run1', 'active_ids': ['run1'], 'serialized': True, 'coverage_complete': True},
            'items': [item], 'streams': {'gmail': {'cutoff': '2026-11-01T00:00:00Z', 'durable': True, 'complete': True}}}


class BoundedRecovery(unittest.TestCase):
    def on_demand(self):
        data = cycle_fixture(); data['policy'] = 'one-cycle-approved-work'
        data['executor'].update(coverage_complete=False, serialized=False, on_demand={
            'operator_assigned': True, 'settings_read_verified': True, 'runs_read_complete': True,
            'registered_thread_id': 'assigned-thread', 'current_thread_id': 'assigned-thread',
            'current_thread_status': 'active', 'current_turn_id': 'run1', 'current_turn_status': 'inProgress',
            'root_id': 'a'*32, 'scheduler_enabled': False, 'scheduler_state': 'Stopped',
            'schedule_ids': [], 'schedule_pending_attempt': None, 'other_active_scan_ids': []})
        return data

    def test_explicit_current_conversation_can_run_without_claiming_cloud_serialization(self):
        data = self.on_demand(); result = scan_cycle.advance(data)
        self.assertEqual(result['status'], 'ScanCyclePlanned')
        self.assertEqual(result['execution_basis'], 'BoundOnDemand')
        self.assertEqual(len(result['work']), 1)
        self.assertFalse(result['external_actions_allowed'])
        data['policy'] = 'one-cycle-no-customer-send'
        self.assertEqual(scan_cycle.advance(data)['status'], 'ScanCyclePlanned')

    def test_on_demand_binding_cannot_bypass_native_policy_or_ambiguous_owner(self):
        for patch in ({'current_thread_id': 'other-thread'}, {'current_turn_id': 'old-turn'},
                      {'operator_assigned': False}, {'settings_read_verified': False}, {'runs_read_complete': False},
                      {'other_active_scan_ids': ['other-scan']}, {'scheduler_enabled': True},
                      {'schedule_ids': ['native-task']}, {'schedule_pending_attempt': {'status': 'Unknown'}},
                      {'root_id': 'b'*32}, {'scheduler_state': 'NeedsReconciliation'}):
            data = self.on_demand(); data['executor']['on_demand'].update(patch)
            with self.subTest(patch=patch):self.assertEqual(scan_cycle.advance(data)['status'], 'ScanDeferred')
        for policy in ('scheduled-approved-work', 'owner-workflow', 'report-only'):
            data = self.on_demand(); data['policy'] = policy
            with self.subTest(policy=policy):self.assertEqual(scan_cycle.advance(data)['status'], 'ScanDeferred')
        data = self.on_demand(); data['executor']['active_ids'].append('another-executor')
        self.assertEqual(scan_cycle.advance(data)['status'], 'ScanDeferred')

    def test_stop_precedes_outbound_and_duplicate_candidate_runs_once(self):
        data = cycle_fixture(); base = data['items'][0]
        data['items'] += [copy.deepcopy(base), base | {'source_key': 'stop', 'step': 'ObserveStop'}]
        result = scan_cycle.advance(data)
        self.assertEqual(len(result['work']), 2)
        self.assertEqual(result['work'][0]['step'], 'ObserveStop')
        result = scan_cycle.advance(data | {'attempted_keys': [v['key'] for v in result['work']]})
        self.assertEqual(result['work'], [])

    def test_unchanged_completed_item_is_not_reopened_by_stale_candidate(self):
        data = cycle_fixture(); identity = scan_cycle.key(data['items'][0])
        result = scan_cycle.advance(data | {'results': [{'key': identity, 'state': 'completed', 'receipt_ref': 'actual-result'}]})
        data['checkpoint_page'] = page('f'*32, block(result['checkpoint']), {})
        self.assertEqual(scan_cycle.advance(data)['work'], [])
        with self.assertRaises(ValueError):
            scan_cycle.advance(data | {'results': [{'key': identity, 'state': 'unknown', 'attempt_id': 'new', 'receipt_ref': 'stale'}]})

    def test_five_rounds_resume_unknown_exactly_once_and_keep_unrelated_work(self):
        data = cycle_fixture(); item = data['items'][0]; identity = scan_cycle.key(item)
        first = scan_cycle.advance(data); self.assertEqual(len(first['work']), 1)
        checkpoint = lambda v: page('f'*32, block(v['checkpoint']), {})
        second = scan_cycle.advance(data | {'checkpoint_page': checkpoint(first), 'results': [
            {'key': identity, 'state': 'unknown', 'attempt_id': 'original-attempt', 'receipt_ref': 'request-receipt'}]})
        self.assertEqual(second['work'][0]['action'], 'reconcile')
        self.assertEqual(second['work'][0]['attempt_id'], 'original-attempt')
        # A crash leaves a durable unknown. Even a rebuilt "ready" item cannot resend.
        third = scan_cycle.advance(data | {'checkpoint_page': checkpoint(second), 'items': []})
        self.assertEqual(third['work'][0]['action'], 'reconcile')
        fourth = scan_cycle.advance(data | {'checkpoint_page': checkpoint(third), 'results': [
            {'key': identity, 'state': 'completed', 'attempt_id': 'original-attempt', 'receipt_ref': 'actual-sent-readback'}]})
        self.assertEqual(fourth['work'], [])
        fifth = scan_cycle.advance(data | {'checkpoint_page': checkpoint(fourth)})
        self.assertEqual(fifth['work'], []); self.assertFalse(fifth['requires_next_cycle'])

    def test_deadline_reserves_publication_and_preserves_remaining_work(self):
        data = cycle_fixture(); data['now'] = '2026-11-01T00:07:00Z'
        result = scan_cycle.advance(data)
        self.assertTrue(result['budget_exhausted']); self.assertEqual(result['work'], [])
        self.assertEqual(len(result['checkpoint']['work_items']), 1)

    def test_unsubmitted_and_future_items_do_not_block_another_client(self):
        data = cycle_fixture(); base = data['items'][0]
        data['items'] += [base | {'source_key': 'waiting', 'waiting': True},
                          base | {'source_key': 'future', 'due_at': '2026-11-02T00:00:00Z'}]
        result = scan_cycle.advance(data)
        self.assertEqual([v['source_key'] for v in result['work']], ['email1'])
        self.assertEqual(len(result['checkpoint']['work_items']), 3)

    def test_overlap_unknown_ownership_or_unserialized_executor_defers(self):
        for patch in ({'active_ids': ['run1', 'run2']}, {'coverage_complete': False}, {'serialized': False}):
            data = cycle_fixture(); data['executor'].update(patch)
            result = scan_cycle.advance(data)
            self.assertEqual(result['status'], 'ScanDeferred'); self.assertEqual(result['work'], [])

    def test_unsaved_or_partial_source_cannot_advance_watermark(self):
        data = cycle_fixture(); data['streams']['gmail']['durable'] = False
        self.assertEqual(scan_cycle.advance(data)['checkpoint']['streams'], {})
        self.assertTrue(scan_cycle.advance(data)['requires_next_cycle'])
        old = scan_cycle.advance(cycle_fixture())
        data['checkpoint_page'] = page('f'*32, block(old['checkpoint']), {})
        self.assertFalse(scan_cycle.advance(data)['coverage_complete'])
        data['streams']['gmail'].update(durable=True, complete=False, next_cursor='page2')
        result = scan_cycle.advance(data)
        self.assertFalse(result['coverage_complete']); self.assertTrue(result['requires_next_cycle'])


class MaintenanceCompletion(unittest.TestCase):
    def test_related_sms_completion_requires_all_original_saved_pages(self):
        from test_owner_completion import completion_for, TASK
        import notion_checks
        data = completion_for('eightdegrees-sms-follow-up', 'RefreshSmsOutcome')
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')
        value = sms_fixture(version='test-v1')
        value['maintenance_task_id'] = TASK
        result = sms_presentation.verify(value | {'saved_pages': saved_sms(value)})
        for identity in result['projection_page_ids']:
            data['registry']['publication_page_ids'].append(identity)
            spec = {'kind': 'page-links', 'entity_id': identity}
            data['registry']['required_checks'][identity] = spec
            data['completion']['required_checks'][identity] = spec
            data['completion']['checks'].append({'name': identity, 'invocation_id': 'run-1', 'publication_version': 'publication-v1',
                                                'exit_code': 0, 'result': notion_checks.page_links({'page': page(identity, 'Saved result.', {})})})
        spec = {'kind': 'sms-presentation', 'entity_id': TASK}
        data['registry']['required_checks']['sms'] = spec
        data['completion']['required_checks']['sms'] = spec
        data['completion']['checks'].append({'name': 'sms', 'invocation_id': 'run-1', 'publication_version': 'publication-v1',
                                            'exit_code': 0, 'result': result})
        self.assertEqual(notion_checks.owner_write(data)['status'], 'WithinOwnerScope')
        data['registry']['publication_page_ids'].remove(result['projection_page_ids'][-1])
        self.assertEqual(notion_checks.owner_write(data)['status'], 'Deferred')


if __name__ == '__main__':
    unittest.main()
