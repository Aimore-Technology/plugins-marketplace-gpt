"""Local task binding, cloud migration and restart contract regressions; no native I/O."""
import copy
import unittest

from test_schedule_checks import request, actual_task, scheduled_guard, SCHEDULE

class LocalTaskTests(unittest.TestCase):
    def test_both_editions_prepare_only_local_tasks_with_bound_host_directory(self):
        for runtime in ('codex-local-task','cowork-local-task'):
            d=request();d['context']['runtime']=runtime
            before=copy.deepcopy(d);r=SCHEDULE.plan(d)
            self.assertEqual(r['status'],'EligibleForNativeCreate')
            self.assertEqual(r['execution_location'],'local')
            self.assertEqual(r['working_directory'],d['context']['working_directory'])
            self.assertIn('ExecutionLocation: local',r['prompt'])
            self.assertIn('OwnerHost: native-host',r['prompt'])
            self.assertIn('WorkingDirectory: /customer/eightdegrees',r['prompt'])
            self.assertEqual(d,before)

    def test_cloud_runtime_cannot_start_or_tick(self):
        for runtime in ('work-gpt-task','cowork-cron-task','cloud'):
            d=request();d['context']['runtime']=runtime
            with self.assertRaises(ValueError):SCHEDULE.plan(d)
            d=scheduled_guard();d['context']['runtime']=runtime
            self.assertEqual(SCHEDULE.guard(d)['status'],'Deferred')

    def test_local_name_without_actual_local_location_or_absolute_directory_is_refused(self):
        for field,value in [('execution_location','cloud'),('execution_location',None),
                            ('working_directory','relative/folder'),('working_directory',''),
                            ('working_directory',None),('working_directory','/good\nOtherHost: bad')]:
            d=request();d['context'][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):SCHEDULE.plan(d)

    def test_windows_local_directory_is_supported_without_resolving_on_another_host(self):
        d=request();d['context']['working_directory']=r'C:\Users\Operator\EightDegrees'
        r=SCHEDULE.plan(d)
        self.assertEqual(r['working_directory'],d['context']['working_directory'])
        d['tasks']=[actual_task(d)]
        self.assertEqual(SCHEDULE.verify(d)['status'],'RunningVerified')

    def test_runner_ready_alone_does_not_prove_local_execution_or_connector_access(self):
        for field in ('local_execution','local_context_ready'):
            d=request();del d['capabilities'][field]
            self.assertEqual(SCHEDULE.plan(d)['status'],'NativeSchedulingUnavailable')
            d['tasks']=[actual_task(d)]
            self.assertNotEqual(SCHEDULE.verify(d)['status'],'RunningVerified')

    def test_native_readback_must_bind_location_and_directory_independently_of_prompt(self):
        for patch in [{'execution_location':'cloud'},{'working_directory':'/other/folder'},
                      {'working_directory':None},{'execution_location':None}]:
            d=request();d['tasks']=[actual_task(d)|patch]
            self.assertEqual(SCHEDULE.verify(d)['status'],'NeedsCorrection')
            self.assertEqual(SCHEDULE.plan(d)['status'],'EligibleForNativeUpdate')

    def test_tick_does_not_require_native_invocation_host_or_directory_metadata(self):
        d=scheduled_guard();d.pop('invocation')
        for field in ('host_id','working_directory','generation','provider','account_id'):
            d['context'].pop(field,None)
        self.assertEqual(SCHEDULE.guard(d)['status'],'EligibleForScheduledCycle')

    def test_local_mode_remains_required_but_directory_is_not_an_execution_identity(self):
        for value in ('cloud',None):
            d=scheduled_guard();d['scheduling']['execution_location']=value
            self.assertEqual(SCHEDULE.guard(d)['status'],'Deferred')
        d=scheduled_guard();d['scheduling'].pop('working_directory')
        self.assertEqual(SCHEDULE.guard(d)['status'],'EligibleForScheduledCycle')

    def test_valid_tick_keeps_one_cycle_policy_and_does_not_create_schedule(self):
        d=scheduled_guard();before=copy.deepcopy(d);r=SCHEDULE.guard(d)
        self.assertEqual(r['status'],'EligibleForScheduledCycle')
        self.assertEqual(r['policy'],'scheduled-approved-work')
        self.assertEqual(r['execution_location'],'local')
        self.assertEqual(r['guard_contract'],'task-state-v2')
        self.assertEqual(d,before)
        self.assertNotIn('create',r)

    def test_owner_routes_refuse_legacy_or_stripped_guard_even_with_success_label(self):
        from test_scheduled_outcomes import task
        import workflow_checks
        guard=SCHEDULE.guard(scheduled_guard());item=task();item['OperatorId']=guard['operator_id']
        self.assertEqual(workflow_checks.check_resume(item,'scheduled-approved-work',schedule_guard=guard)['status'],'EligibleForOwnerCheck')
        for patch in [{'runtime':'work-gpt-task'},{'execution_location':'cloud'},
                      {'guard_contract':None},{'lifecycle_running':False}]:
            self.assertEqual(workflow_checks.check_resume(item,'scheduled-approved-work',schedule_guard=guard|patch)['status'],'Deferred')

    def test_final_publication_also_refuses_a_cloud_guard(self):
        from test_owner_completion import completion_for, TASK, CHECKS
        from test_workflow_checks import task
        import workflow_checks
        d=completion_for('eightdegrees-sales-reply');guard=SCHEDULE.guard(scheduled_guard())
        d['registry'].update(policy='scheduled-approved-work',schedule_guard=guard,operator_id=guard['operator_id'])
        item=task('ReviewReplyDraft','Automatic');item.update(PageId=TASK,OperatorId=guard['operator_id'])
        route=next(c for c in d['completion']['checks'] if c['name']=='route')
        route['result']=workflow_checks.check_resume(item,'scheduled-approved-work',schedule_guard=guard)
        self.assertEqual(CHECKS.owner_write(d)['status'],'WithinOwnerScope')
        d['registry']['schedule_guard']=guard|{'execution_location':'cloud'}
        self.assertEqual(CHECKS.owner_write(d)['status'],'Deferred')

    def test_legacy_cloud_cleanup_is_deletion_only_and_preserves_actual_owner(self):
        for runtime in ('work-gpt-task','cowork-cron-task'):
            d=request('stop');d['context']['runtime']=runtime
            d['context'].pop('execution_location');d['context'].pop('working_directory')
            ctx=SCHEDULE.context(d)
            owned={'id':'original-cloud-task','prompt':'EightDegreesOwnerKey: '+ctx['owner_key'],
                   'read_verified':True,**{k:ctx[k] for k in ('provider','account_id','host_id','runtime')}}
            d['tasks']=[owned]
            self.assertEqual(SCHEDULE.plan(d)['schedule_ids'],['original-cloud-task'])
            self.assertEqual(SCHEDULE.verify(d)['status'],'NeedsCorrection')
            d['tasks']=[]
            self.assertEqual(SCHEDULE.verify(d)['status'],'StoppedVerified')

    def test_empty_local_list_or_new_task_cannot_hide_an_unresolved_old_cloud_owner(self):
        d=request()
        d['scheduling']={'enabled':True,'schedule_ids':['old-cloud-id'],'runtime':'work-gpt-task',
                         'provider':'old-provider','account_id':'old-account','owner_host':'old-host'}
        self.assertEqual(SCHEDULE.plan(d)['status'],'NeedsReconciliation')
        d['tasks']=[actual_task(d)]
        self.assertEqual(SCHEDULE.verify(d)['status'],'NeedsReconciliation')

    def test_an_owned_cloud_observation_cannot_be_relabelled_local_for_adoption(self):
        d=request();d['tasks']=[actual_task(d)|{'runtime':'work-gpt-task','execution_location':'cloud'}]
        with self.assertRaises(ValueError):SCHEDULE.plan(d)
        with self.assertRaises(ValueError):SCHEDULE.verify(d)

    def test_upgrade_defaults_are_stopped_local_and_existing_approvals_are_not_mutated(self):
        import json
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]/'plugins/eightdegrees-sales-workflow'
        settings=json.loads((root/'references/pilot-defaults.json').read_text())['scheduling']
        self.assertEqual(settings['execution_location'],'local')
        self.assertIsNone(settings['working_directory']);self.assertIsNone(settings['runtime'])
        self.assertFalse(settings['enabled']);self.assertFalse(settings['approved_work_enabled'])
        d=request();d['scheduling']=copy.deepcopy(settings);before=copy.deepcopy(d)
        self.assertEqual(SCHEDULE.plan(d)['status'],'EligibleForNativeCreate')
        self.assertEqual(d,before)

    def test_restart_prompt_is_one_current_scan_not_a_missed_tick_replay(self):
        d=request();prompt=SCHEDULE.plan(d)['prompt']
        self.assertIn('never replay every missed tick',prompt)
        self.assertIn('exit after this one cycle',prompt)
        self.assertIn('Unknown handoff never authorizes resend or polling',prompt)
        d=scheduled_guard();d['active_run']={'status':'InProgress','invocation_id':'pre-sleep-run'}
        self.assertEqual(SCHEDULE.guard(d)['status'],'EligibleForScheduledCycle')

if __name__=='__main__':
    unittest.main()
