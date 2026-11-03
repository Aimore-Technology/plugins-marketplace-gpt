"""Execute with task state and local run labels, without a unique host/session."""
import copy
import unittest

import invocation_context
import scan_cycle
import dispatch_admission
import workflow_checks
from test_schedule_checks import scheduled_guard, SCHEDULE
from test_unattended import cycle_fixture, page, block
from test_pre_action_order import dispatch, ready


def configured_tick():
    data = scheduled_guard()
    data.pop('context')
    data.pop('invocation')
    data.pop('capabilities')
    for key in ('owner_host', 'schedule_ids', 'generation', 'working_directory', 'provider', 'account_id'):
        data['scheduling'].pop(key, None)
    return data


class TaskStateExecutionTests(unittest.TestCase):
    def test_tick_requires_no_native_identity_or_executor_assignment(self):
        data = configured_tick()
        before = copy.deepcopy(data)
        guard = SCHEDULE.guard(data)
        self.assertEqual(guard['status'], 'EligibleForScheduledCycle')
        self.assertEqual(guard['guard_contract'], 'task-state-v2')
        self.assertNotIn('host_id', guard)
        self.assertNotIn('invocation_id', guard)
        self.assertEqual(data, before)

    def test_both_local_runtimes_need_no_current_native_task_id(self):
        for runtime in ('codex-local-task', 'cowork-local-task'):
            data = configured_tick()
            data['scheduling']['runtime'] = runtime
            self.assertEqual(SCHEDULE.guard(data)['status'], 'EligibleForScheduledCycle')

    def test_other_runs_and_missing_serialization_are_not_global_barriers(self):
        data = configured_tick()
        data['active_run'] = {'status': 'InProgress', 'invocation_id': 'unrelated-run'}
        data['executor'] = {'coverage_complete': False, 'serialized': False, 'active_ids': ['other']}
        self.assertEqual(SCHEDULE.guard(data)['status'], 'EligibleForScheduledCycle')

    def test_legacy_exclusive_settings_are_inert_without_migration_or_rebinding(self):
        data = configured_tick()
        data['scheduling'].update(single_owner_required=True, owner_host='old-host', generation=1)
        data['setup']['queue_execution'] = {'executor_mode': 'single_native_owner',
                                           'on_demand_executor_thread_id': 'old-thread'}
        self.assertEqual(SCHEDULE.guard(data)['status'], 'EligibleForScheduledCycle')

    def test_wrong_installation_account_scope_still_defers(self):
        for patch in ({'root_id': 'b' * 32}, {'operator_id': 'other'}, {'mailbox': 'other@example.com'}):
            data = configured_tick()
            data['context'] = patch
            self.assertEqual(SCHEDULE.guard(data)['status'], 'Deferred')

    def test_stop_and_authority_revocation_still_block_scheduled_work(self):
        for patch in ({'enabled': False}, {'approved_work_enabled': False},
                      {'desired_state': 'Stopped'}, {'state': 'StopRequested'}):
            data = configured_tick()
            data['scheduling'].update(patch)
            self.assertEqual(SCHEDULE.guard(data)['status'], 'Deferred')

    def test_owner_route_accepts_task_state_without_session_identity(self):
        from test_scheduled_outcomes import task
        guard = SCHEDULE.guard(configured_tick())
        item = task()
        item['OperatorId'] = guard['operator_id']
        self.assertEqual(workflow_checks.check_resume(item, 'scheduled-approved-work',
                         schedule_guard=guard)['status'], 'EligibleForOwnerCheck')

    def test_final_publication_accepts_task_state_without_session_identity(self):
        from test_owner_completion import completion_for, TASK, CHECKS
        from test_workflow_checks import task
        guard = SCHEDULE.guard(configured_tick())
        data = completion_for('eightdegrees-sales-reply')
        data['registry'].update(policy='scheduled-approved-work', schedule_guard=guard,
                                operator_id=guard['operator_id'])
        item = task('ReviewReplyDraft', 'Automatic')
        item.update(PageId=TASK, OperatorId=guard['operator_id'])
        route = next(c for c in data['completion']['checks'] if c['name'] == 'route')
        route['result'] = workflow_checks.check_resume(item, 'scheduled-approved-work', schedule_guard=guard)
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')

    def test_cycle_without_executor_generates_a_stable_log_label(self):
        data = cycle_fixture()
        data.pop('executor')
        first, second = scan_cycle.advance(data), scan_cycle.advance(data)
        self.assertEqual(first['status'], 'ScanCyclePlanned')
        self.assertEqual(len(first['work']), 1)
        self.assertEqual(first['checkpoint']['invocation_id'], second['checkpoint']['invocation_id'])
        self.assertEqual(first['execution_basis'], 'TaskStateAndAttempts')
        self.assertFalse(first['external_actions_allowed'])

    def test_explicit_local_run_label_is_used_without_native_observations(self):
        data = cycle_fixture()
        data['run_id'] = 'local-log-uuid'
        data.pop('executor')
        self.assertEqual(scan_cycle.advance(data)['checkpoint']['invocation_id'], 'local-log-uuid')

    def test_dispatch_and_fresh_release_work_without_host_identity(self):
        data = dispatch()
        data['scan'].pop('executor')
        data = ready(data)
        data['current_scan'].pop('executor', None)
        self.assertEqual(dispatch_admission.release(data)['status'], 'DispatchArgumentsPrepared')

    def test_task_stop_still_blocks_dispatch_without_host_identity(self):
        data = dispatch()
        data['scan'].pop('executor')
        data['scan']['items'][0]['stopped'] = True
        with self.assertRaises(ValueError):
            dispatch_admission.prepare(data)

    def test_completed_work_is_skipped_without_global_executor_checks(self):
        data = cycle_fixture()
        data.pop('executor')
        planned = scan_cycle.advance(data)
        item = planned['work'][0]
        data['checkpoint_page'] = page('f' * 32, block(planned['checkpoint']), {})
        data['results'] = [{'key': item['key'], 'state': 'completed', 'receipt_ref': 'saved-original-result'}]
        self.assertEqual(scan_cycle.advance(data)['work'], [])

    def test_unknown_attempt_still_cannot_be_sent_again(self):
        data = dispatch()
        data['scan'].pop('executor')
        data['scan']['items'][0].update(unknown_attempt=True, attempt_id='original-provider-attempt')
        with self.assertRaises(ValueError):
            dispatch_admission.prepare(data)

    def test_recovery_generates_local_uuid_and_needs_no_executor_identity(self):
        data = {'command': 'run-auto', 'root_id': 'a' * 32, 'started_at': '2026-11-04T00:00:00Z'}
        record = invocation_context.prepare(data)['record']
        self.assertTrue(record['invocation_id'].startswith('run-'))
        self.assertIsNone(record['executor_id'])
        result = invocation_context.resume(data | {'context_record': record,
             'now': '2026-11-04T00:01:00Z', 'executor_id': 'optional-other-diagnostic'})
        self.assertEqual(result['remaining_seconds'], 840)
        self.assertFalse(result['external_actions_allowed'])

    def test_local_recovery_label_never_relaxes_original_budget_or_policy(self):
        data = {'command': 'run-auto', 'root_id': 'a' * 32, 'started_at': '2026-11-04T00:00:00Z',
                'policy': 'one-cycle-no-customer-send', 'restrictions': ['No customer sends']}
        record = invocation_context.prepare(data)['record']
        current = data | {'context_record': record, 'now': '2026-11-04T00:01:00Z'}
        for patch in ({'started_at': '2026-11-04T00:00:30Z'}, {'policy': 'one-cycle-approved-work'}):
            with self.assertRaises(ValueError):
                invocation_context.resume(current | patch)


if __name__ == '__main__':
    unittest.main()
