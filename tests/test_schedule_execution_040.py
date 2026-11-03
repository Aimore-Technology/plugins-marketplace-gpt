"""No scheduler management tools, runtime identity or cadence proof on start/stop."""
import unittest
from test_schedule_checks import request, scheduled_guard, SCHEDULE


class ControlWithoutManagementTests(unittest.TestCase):
    def test_start_with_all_management_capabilities_missing_still_only_changes_flag(self):
        data=request();data['capabilities']={}
        self.assertEqual(SCHEDULE.plan(data)['status'],'ScanControlPlanned')

    def test_stop_needs_no_native_deletion_capability(self):
        data=request('stop');data['capabilities']={'delete':False}
        self.assertFalse(SCHEDULE.plan(data)['patch']['scan_control']['enabled'])

    def test_start_does_not_require_listing_paused_or_unknown_native_tasks(self):
        data=request();data['tasks']=None;data['list_complete']=False
        self.assertFalse(SCHEDULE.plan(data)['native_task_mutation_allowed'])

    def test_switch_does_not_change_saved_cadence(self):
        data=request();data['settings']['scheduling']['target_scan_minutes']=20
        data['saved_settings']=data['settings']|SCHEDULE.plan(data)['patch']
        self.assertEqual(SCHEDULE.verify(data)['status'],'ScanningEnabled')
        self.assertEqual(data['saved_settings']['scheduling']['target_scan_minutes'],20)

    def test_unknown_switch_never_means_enabled(self):
        data=scheduled_guard();data['settings']={'scan_control':{'enabled':'false'}}
        self.assertEqual(SCHEDULE.guard(data)['status'],'ScanControlUnknown')

    def test_final_publication_accepts_enabled_switch_without_host_identity(self):
        import workflow_checks
        from test_owner_completion import completion_for, TASK, CHECKS
        from test_workflow_checks import task
        guard=SCHEDULE.guard(scheduled_guard());data=completion_for('eightdegrees-sales-reply')
        data['registry'].update(policy='scheduled-approved-work',schedule_guard=guard,operator_id=guard['operator_id'])
        item=task('ReviewReplyDraft','Automatic');item.update(PageId=TASK,OperatorId=guard['operator_id'])
        next(c for c in data['completion']['checks'] if c['name']=='route')['result']=workflow_checks.check_resume(item,'scheduled-approved-work',schedule_guard=guard)
        self.assertEqual(CHECKS.owner_write(data)['status'],'WithinOwnerScope')


if __name__=='__main__':unittest.main()
