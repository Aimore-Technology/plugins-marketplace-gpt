"""Management capability limits must not block a verified existing local tick."""
import copy
import unittest

from test_schedule_checks import request, actual_task, scheduled_guard, SCHEDULE


class ExecutionWithoutManagementTests(unittest.TestCase):
    def execution(self, runtime='codex-local-task'):
        data = scheduled_guard()
        data['context']['runtime'] = runtime
        data['scheduling']['runtime'] = runtime
        for key in ('operation', 'capabilities', 'tasks', 'list_complete', 'list_includes_inactive'):
            data.pop(key, None)
        return data

    def test_existing_tick_needs_no_management_payload(self):
        for runtime in ('codex-local-task', 'cowork-local-task'):
            data = self.execution(runtime)
            before = copy.deepcopy(data)
            result = SCHEDULE.guard(data)
            self.assertEqual(result['status'], 'EligibleForScheduledCycle')
            self.assertEqual(result['policy'], 'scheduled-approved-work')
            self.assertEqual(data, before)

    def test_all_management_capabilities_unavailable_do_not_defer_execution(self):
        data = self.execution()
        data['capabilities'] = {key: False for key in
                                ('list', 'read', 'create', 'update', 'delete', 'runner_ready')}
        data['list_complete'] = False
        data['tasks'] = None
        self.assertEqual(SCHEDULE.guard(data)['status'], 'EligibleForScheduledCycle')

    def test_previous_management_failure_is_not_a_current_execution_failure(self):
        data = self.execution()
        data['management_result'] = {
            'status': 'NativeSchedulingUnavailable', 'operation': 'start',
            'limitation_scope': 'schedule-management-only'}
        before = copy.deepcopy(data['scheduling'])
        self.assertEqual(SCHEDULE.guard(data)['status'], 'EligibleForScheduledCycle')
        self.assertEqual(data['scheduling'], before)

    def test_missing_list_or_read_returns_a_management_scoped_limit(self):
        for operation in ('start', 'stop'):
            for capability in ('list', 'read'):
                data = request(operation)
                data['capabilities'][capability] = False
                data.pop('tasks')
                before = copy.deepcopy(data)
                result = SCHEDULE.plan(data)
                self.assertEqual(result['status'], 'NativeSchedulingUnavailable')
                self.assertEqual(result['operation'], operation)
                self.assertEqual(result['limitation_scope'], 'schedule-management-only')
                self.assertEqual(data, before)

    def test_cannot_create_still_does_not_claim_task_creation(self):
        data = request()
        data['capabilities']['create'] = False
        result = SCHEDULE.plan(data)
        self.assertEqual(result['status'], 'NativeSchedulingUnavailable')
        self.assertEqual(result['limitation_scope'], 'schedule-management-only')
        self.assertNotIn('schedule_id', result)
        self.assertNotIn('prompt', result)

    def test_existing_exact_job_can_be_reused_without_create_or_update(self):
        data = request()
        data['tasks'] = [actual_task(data)]
        data['capabilities'].update(create=False, update=False, delete=False)
        self.assertEqual(SCHEDULE.plan(data)['status'], 'ReuseExisting')

    def test_unavailable_delete_preserves_native_identity_and_cannot_claim_stopped(self):
        data = request('stop')
        data['tasks'] = [actual_task(data)]
        data['capabilities']['delete'] = False
        result = SCHEDULE.plan(data)
        self.assertEqual(result['status'], 'NativeDeletionUnavailable')
        self.assertEqual(result['limitation_scope'], 'schedule-management-only')
        self.assertEqual(result['schedule_ids'], ['native-task-1'])
        self.assertEqual(SCHEDULE.verify(data)['status'], 'NeedsCorrection')

    def test_owner_route_can_run_with_no_scheduler_management_access(self):
        import workflow_checks
        from test_scheduled_outcomes import task
        guard = SCHEDULE.guard(self.execution())
        item = task()
        item['OperatorId'] = guard['operator_id']
        self.assertEqual(workflow_checks.check_resume(
            item, 'scheduled-approved-work', schedule_guard=guard)['status'], 'EligibleForOwnerCheck')

    def test_final_publication_can_run_with_no_scheduler_management_access(self):
        import workflow_checks
        from test_owner_completion import completion_for, TASK, CHECKS
        from test_workflow_checks import task
        guard = SCHEDULE.guard(self.execution())
        data = completion_for('eightdegrees-sales-reply')
        data['registry'].update(policy='scheduled-approved-work', schedule_guard=guard,
                                operator_id=guard['operator_id'])
        item = task('ReviewReplyDraft', 'Automatic')
        item.update(PageId=TASK, OperatorId=guard['operator_id'])
        route = next(check for check in data['completion']['checks'] if check['name'] == 'route')
        route['result'] = workflow_checks.check_resume(item, 'scheduled-approved-work', schedule_guard=guard)
        self.assertEqual(CHECKS.owner_write(data)['status'], 'WithinOwnerScope')

    def test_missing_management_does_not_bypass_stop(self):
        for patch in ({'approved_work_enabled':False},{'desired_state':'Stopped'},{'state':'StopRequested'}):
            data=self.execution();data['scheduling'].update(patch)
            self.assertEqual(SCHEDULE.guard(data)['status'],'Deferred')

    def test_native_identity_and_global_activity_are_no_longer_execution_gates(self):
        data=self.execution();data.pop('invocation')
        data['active_run']={'status':'InProgress','invocation_id':'other-turn'}
        self.assertEqual(SCHEDULE.guard(data)['status'],'EligibleForScheduledCycle')

    def test_tick_prompt_routes_to_execution_without_another_setup_pass(self):
        prompt = SCHEDULE.plan(request())['prompt']
        self.assertIn('references/schedule-execution.md', prompt)
        self.assertIn('management tools are not a tick gate', prompt)
        self.assertNotIn('If this chat cannot manage that runtime', prompt)
        self.assertIn('Only a current EligibleForScheduledCycle guard', prompt)


if __name__ == '__main__':
    unittest.main()
