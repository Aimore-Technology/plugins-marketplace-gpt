"""The switch replaces native task management; keep regression coverage for no I/O."""
import copy
import unittest
from test_schedule_checks import request, scheduled_guard, SCHEDULE
from test_scheduled_outcomes import task
import workflow_checks


class LocalSwitchTests(unittest.TestCase):
    def test_legacy_cloud_or_local_metadata_cannot_trigger_task_management(self):
        for runtime in ('work-gpt-task','cowork-cron-task','codex-local-task','cowork-local-task'):
            data=request();data['settings']['scheduling']['runtime']=runtime
            result=SCHEDULE.plan(data)
            self.assertEqual(set(result['patch']),{'scan_control'})
            self.assertFalse(result['native_task_mutation_allowed'])

    def test_windows_or_other_saved_working_directory_is_not_required_for_start(self):
        data=request();data['settings']['scheduling']['working_directory']='C:\\existing'
        self.assertEqual(SCHEDULE.plan(data)['status'],'ScanControlPlanned')

    def test_unknown_old_native_mutation_does_not_block_stop_switch(self):
        data=request('stop');data['settings']['scheduling']['pending_attempt']={'status':'Unknown','id':'old'}
        before=copy.deepcopy(data)
        self.assertFalse(SCHEDULE.plan(data)['patch']['scan_control']['enabled'])
        self.assertEqual(data,before)

    def test_live_task_ids_are_preserved_on_start_readback(self):
        data=request();data['saved_settings']=data['settings']|SCHEDULE.plan(data)['patch']
        self.assertEqual(SCHEDULE.verify(data)['status'],'ScanningEnabled')
        self.assertEqual(data['saved_settings']['scheduling']['schedule_ids'],['existing-native-task'])

    def test_owner_route_needs_a_current_enabled_scan_guard(self):
        guard=SCHEDULE.guard(scheduled_guard());item=task();item['OperatorId']=guard['operator_id']
        self.assertEqual(workflow_checks.check_resume(item,'scheduled-approved-work',schedule_guard=guard)['status'],'EligibleForOwnerCheck')
        for patch in ({'scan_enabled':False},{'guard_contract':None},{'root_id':None}):
            self.assertEqual(workflow_checks.check_resume(item,'scheduled-approved-work',schedule_guard=guard|patch)['status'],'Deferred')

    def test_another_active_session_is_still_not_a_global_blocker(self):
        data=scheduled_guard();data['active_run']={'status':'InProgress','invocation_id':'other'}
        self.assertEqual(SCHEDULE.guard(data)['status'],'EligibleForScheduledCycle')


if __name__=='__main__':unittest.main()
