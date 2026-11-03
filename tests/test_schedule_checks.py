"""start/stop only changes the scanning switch; native schedules are untouched."""
import copy
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'plugins/eightdegrees-sales-workflow/scripts/schedule_checks.py'
SPEC = importlib.util.spec_from_file_location('schedule_checks', PATH)
SCHEDULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCHEDULE)


def request(operation='start'):
    return {'operation': operation, 'settings': {'scan_control': {'contract':'scan-control-v1','enabled':False},
            'scheduling': {'schedule_ids':['existing-native-task'],'runtime':'codex-local-task'},
            'queue_execution': {'event_index_page_id':'original-index'}, 'approval':'original-approval'}}


def scheduled_guard():
    return {'trigger':'scheduled','context':{'root_id':'a'*32,'operator_id':'operator-local-demo',
             'mailbox':'operator@example.com','runtime':'codex-local-task','host_id':'native-host',
             'generation':1,'execution_location':'local','working_directory':'/customer/eightdegrees'},
            'setup':{'notion_root_id':'a'*32,'operator_id':'operator-local-demo','gmail_account':'operator@example.com'},
            'scheduling':{'enabled':True,'approved_work_enabled':True,'state':'Running','desired_state':'Running',
              'runtime':'codex-local-task','execution_location':'local','schedule_ids':['native-task-1'],
              'owner_host':'native-host','generation':1,'working_directory':'/customer/eightdegrees'},
            'invocation':{'schedule_id':'native-task-1','invocation_id':'scan-invocation-1'},
            'capabilities':{}}


class ScanSwitchTests(unittest.TestCase):
    def test_start_prepares_only_a_settings_patch_without_scheduler_access(self):
        data=request();before=copy.deepcopy(data);result=SCHEDULE.plan(data)
        self.assertEqual(result['status'],'ScanControlPlanned')
        self.assertEqual(set(result['patch']),{'scan_control'})
        self.assertTrue(result['patch']['scan_control']['enabled'])
        self.assertFalse(result['native_task_mutation_allowed'])
        self.assertEqual(data,before)

    def test_stop_does_not_delete_or_pause_existing_native_tasks(self):
        data=request('stop');data['settings']['scan_control']['enabled']=True
        result=SCHEDULE.plan(data)
        self.assertFalse(result['patch']['scan_control']['enabled'])
        self.assertNotIn('schedule_ids',result['patch'])
        self.assertNotIn('prompt',result)

    def test_readback_only_accepts_the_requested_flag_and_unchanged_other_settings(self):
        for operation,status in [('start','ScanningEnabled'),('stop','ScanningStopped')]:
            data=request(operation);data['saved_settings']=data['settings']|SCHEDULE.plan(data)['patch']
            self.assertEqual(SCHEDULE.verify(data)['status'],status)
            data['saved_settings']['scheduling']={}
            self.assertEqual(SCHEDULE.verify(data)['status'],'NeedsCorrection')

    def test_repeat_control_command_needs_no_redundant_write(self):
        for operation,value in [('start',True),('stop',False)]:
            data=request(operation);data['settings']['scan_control']['enabled']=value
            self.assertFalse(SCHEDULE.plan(data)['write_required'])

    def test_explicit_switch_works_with_no_native_runtime_ids_or_capabilities(self):
        data=scheduled_guard();data['settings']={'scan_control':{'contract':'scan-control-v1','enabled':True}}
        for name in ('scheduling','context','invocation','capabilities'):data.pop(name,None)
        self.assertEqual(SCHEDULE.guard(data)['status'],'EligibleForScheduledCycle')

    def test_stopped_tick_exits_before_even_requiring_setup(self):
        self.assertEqual(SCHEDULE.guard({'settings':request()['settings']})['status'],'ScanStopped')

    def test_scheduled_policy_preserves_operator_and_root_scope(self):
        data=scheduled_guard();self.assertEqual(SCHEDULE.guard(data)['status'],'EligibleForScheduledCycle')
        for field in ('operator_id','gmail_account','notion_root_id'):
            bad=copy.deepcopy(data);bad['setup'][field]='other'
            self.assertEqual(SCHEDULE.guard(bad)['status'],'Deferred')

    def test_manual_cycle_also_obeys_the_scan_switch(self):
        data=scheduled_guard();data['trigger']='manual'
        self.assertEqual(SCHEDULE.guard(data)['status'],'EligibleForManualCycle')
        data['settings']=request()['settings']
        self.assertEqual(SCHEDULE.guard(data)['status'],'ScanStopped')

    def test_legacy_running_state_remains_enabled_without_recreating_a_task(self):
        data=scheduled_guard();self.assertEqual(SCHEDULE.guard(data)['guard_contract'],'scan-control-v1')
        data['scheduling']['approved_work_enabled']=False
        self.assertEqual(SCHEDULE.guard(data)['status'],'ScanStopped')

    def test_new_stop_overrides_legacy_running_without_touching_legacy_metadata(self):
        data=scheduled_guard();data['settings']={'scheduling':data['scheduling'],**request()['settings']}
        self.assertEqual(SCHEDULE.guard(data)['status'],'ScanStopped')


if __name__=='__main__':unittest.main()
