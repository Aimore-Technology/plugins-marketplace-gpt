"""Reproduce seven-cycle 0.1.34 findings without provider access."""

import copy
import hashlib
import json
import unittest

from test_unattended import cycle_fixture
from test_event_probe import fixture, saved
from test_email_presentation import page, block
from test_notion_checks import source_schema, PARENT
import scan_cycle
import runtime_records
import notion_mutation
import discovery_watch
import connector_capture
import event_probe
import local_checks


def run_call(operation='report'):
    meta = runtime_records.prepare({'owner_skill': 'eightdegrees-daily-brief-and-handover' if operation=='report' else 'eightdegrees-email-scanning',
                                   'invocation_id': 'actual-turn', 'operation': operation})['properties']
    schema = source_schema()
    state = json.loads(schema['text'].split('<data-source-state>')[1].split('</data-source-state>')[0])
    state['schema'].update({k: {'type': 'text'} for k in meta})
    schema['text'] = '<data-source-state>'+json.dumps(state)+'</data-source-state>'
    return {'data_source': schema, 'call': {'tool': 'mcp__codex_apps__notion_notion_create_pages',
            'args': {'parent': {'data_source_id': PARENT}, 'pages': [{'properties':meta, 'content':'Frozen plan.'}]}}}


class BudgetAndPriority(unittest.TestCase):
    def boundary(self, remaining, estimate):
        data=cycle_fixture();data.update(budget_seconds=900,reserve_seconds=120,now=f'2026-11-01T00:{(780-remaining)//60:02d}:{(780-remaining)%60:02d}Z')
        data['items'][0].update(step='SendNotificationSms',estimated_seconds=estimate)
        return data

    def test_live_179_vs_180_and_89_vs_90_admit_without_extending_deadline(self):
        for remaining,estimate in [(179,180),(89,90)]:
            result=scan_cycle.advance(self.boundary(remaining,estimate))
            self.assertEqual(len(result['work']),1)
            self.assertEqual(result['estimated_reserve_use_seconds'],1)
            self.assertEqual(result['deadline'],'2026-11-01T00:15:00+00:00')
            self.assertFalse(result['external_actions_allowed'])

    def test_large_estimate_overrun_and_admission_deadline_still_defer(self):
        for remaining,estimate in [(179,195),(29,30),(0,1)]:
            self.assertEqual(scan_cycle.advance(self.boundary(remaining,estimate))['work'],[])

    def test_small_reserve_has_no_slack_and_unknown_is_not_retried(self):
        data=self.boundary(179,180);data['reserve_seconds']=30;data['now']='2026-11-01T00:11:31Z'
        self.assertEqual(scan_cycle.advance(data)['estimate_slack_seconds'],0)
        data=self.boundary(179,180);data['items'][0].update(unknown_attempt=True,attempt_id='original')
        self.assertEqual(scan_cycle.advance(data)['work'][0]['action'],'reconcile')

    def test_notification_precedes_reviews_and_display_but_never_mail_intake(self):
        data=self.boundary(179,180);item=data['items'][0]
        data['items'] += [item|{'source_key':'review','step':'ReviewCommunication'},item|{'source_key':'display','step':'RefreshEmailOutcome'}]
        self.assertEqual(scan_cycle.advance(data)['work'][0]['step'],'SendNotificationSms')
        data['items'].append(item|{'source_key':'new-mail','step':'ReadMessageBody'})
        self.assertEqual(scan_cycle.advance(data)['work'][0]['step'],'ReadMessageBody')

    def test_unfitting_unrelated_item_does_not_hide_fitting_one(self):
        data=self.boundary(179,180);data['items'][0].update(step='ReviewCommunication',priority=1,estimated_seconds=600)
        data['items'].append(data['items'][0]|{'source_key':'other','priority':2,'estimated_seconds':90})
        self.assertEqual(scan_cycle.advance(data)['work'][0]['source_key'],'other')

    def test_stop_and_unknown_barriers_cannot_be_skipped(self):
        for patch in [{'step':'ObserveStop'},{'unknown_attempt':True,'attempt_id':'original'}]:
            data=self.boundary(179,180);data['items'][0].update(estimated_seconds=600,**patch)
            data['items'].append({'source_key':'notify','step':'SendNotificationSms','version':'v1','input_digest':'new','estimated_seconds':60})
            self.assertEqual(scan_cycle.advance(data)['work'],[])

    def test_final_dispatch_rechecks_only_remaining_call_cost(self):
        from test_pre_action_order import dispatch
        from test_notion_checks import page as simple_page
        import dispatch_admission
        data=dispatch('sms');data['scan'].update(self.boundary(179,180))
        data['scan']['policy']='one-cycle-approved-work'
        data['scan']['root_id']=data['notification']['authority']['root_id']
        data['scan']['items'][0]['version']=data['notification']['payload']['content_version']
        data['work_key']=scan_cycle.key(data['scan']['items'][0])
        self.assertEqual(len(scan_cycle.advance(data['scan'])['work']),1)
        record=dispatch_admission.prepare(data)['record']
        data['saved_run']=simple_page(block(record));data['saved_run']['id']=data['run_page_id']
        # Ninety seconds of preparation have actually elapsed. The full 180s
        # estimate must not be charged again before a remaining 30s API call.
        data['now']='2026-11-01T00:11:31Z';data['current_scan']=copy.deepcopy(data['scan']);data['current_scan']['now']=data['now']
        self.assertEqual(dispatch_admission.release(data)['call'],data['call'])
        data['current_scan']['items'][0]['stopped']=True
        with self.assertRaises(ValueError):dispatch_admission.release(data)
        data['current_scan']['items'][0]['stopped']=False
        data['now']='2026-11-01T00:13:00Z';data['current_scan']['now']=data['now']
        with self.assertRaises(ValueError):dispatch_admission.release(data)


class RunMetadata(unittest.TestCase):
    def test_generated_version_and_current_scan_identity_are_required_before_create(self):
        for operation in ['scan','report']:
            data=run_call(operation)
            self.assertEqual(notion_mutation.prepare(data)['status'],'NotionMutationPrepared')
            props=data['call']['args']['pages'][0]['properties']
            self.assertEqual(props['SkillVersion'],runtime_records.VERSION)
            for field in ['SkillVersion','SourceKey','RunId','Skill']:
                broken=copy.deepcopy(data);broken['call']['args']['pages'][0]['properties'][field]=''
                with self.subTest(operation=operation,field=field),self.assertRaises(ValueError):notion_mutation.prepare(broken)

    def test_stale_scan_source_and_incorrect_report_version_refuse(self):
        for operation,field,value in [('scan','SourceKey','scan:previous-turn'),('report','SkillVersion','0.1.34')]:
            data=run_call(operation);data['call']['args']['pages'][0]['properties'][field]=value
            with self.assertRaises(ValueError):notion_mutation.prepare(data)

    def test_metadata_guard_applies_to_actual_completion_properties(self):
        data=run_call();props=data['call']['args']['pages'][0]['properties'];props['SkillVersion']=''
        data['target']=page('1'*32,'Frozen plan.',props)
        data['target']['text']='<parent-data-source url="collection://'+PARENT+'"/>\n'+data['target']['text']
        data['call']={'tool':'mcp__codex_apps__notion_notion_update_page','args':{'page_id':'1'*32,'command':'update_properties','properties':{'Summary':'Published'}}}
        with self.assertRaises(ValueError):notion_mutation.prepare(data)

    def test_omitting_record_type_cannot_bypass_the_run_schema_guard(self):
        data=run_call();del data['call']['args']['pages'][0]['properties']['RecordType']
        with self.assertRaises(ValueError):notion_mutation.prepare(data)

    def test_saved_plan_cannot_proceed_with_missing_or_stale_run_metadata(self):
        from test_execution_preflight import request, capture
        import execution_preflight
        prepared=execution_preflight.prepare(request())
        for field in ['SkillVersion','SourceKey','RunId']:
            original=capture(prepared)
            original['text']=original['text'].replace(json.dumps(prepared['execution_plan']['run_properties'][field]),json.dumps('stale'),1)
            with self.subTest(field=field),self.assertRaises(ValueError):execution_preflight.ready({'prepared':prepared,'saved_plan':original})


class ActiveWatches(unittest.TestCase):
    def fixture(self):
        config={'settings_schema_version':2,'project_sources':{},'sales_replies':{}}
        for n in [1,2,3]:
            config['project_sources'][str(n)]={'context_key':str(n),'index':{'file_id':f'index{n}'},'files':{'current':{'file_id':f'current{n}','status':'Current'},'old':{'file_id':f'old{n}','status':'Superseded'}}}
            config['sales_replies'][str(n)]={'context_key':str(n),'content_task_page_id':format(n,'032x'),'send_task_page_id':format(n+10,'032x')}
        return {'settings_page':page('a'*32,block(config),{}),'tasks_complete':True,'tasks':[],
                'index_page':page('b'*32,block({'record_type':'scan-event-index-v1','root_id':'a'*32,'pending':{}}),{})}

    def test_completed_projects_and_only_machine_notice_require_zero_metadata_reads(self):
        data=self.fixture();data['tasks']=[{'url':'1'*32,'State':'Completed','ResumeStep':'ReviewReplyDraft'},{'url':'9'*32,'State':'InProgress','Category':'ScheduledWork','ResumeStep':'SendNotificationSms'}]
        result=discovery_watch.plan(data)
        self.assertEqual(result['source_metadata'],[]);self.assertEqual(result['action_page_urls'],[])
        self.assertTrue(result['mail_scope_unchanged'])

    def test_active_email_keeps_its_index_and_current_sources_only(self):
        data=self.fixture();data['tasks']=[{'url':format(2,'032x'),'State':'WaitingForOperator','Category':'ContentReview','ResumeStep':'ReviewReplyDraft','ActionPageURL':'original-action'}]
        result=discovery_watch.plan(data)
        self.assertEqual({x['file_id'] for x in result['source_metadata']},{'index2','current2'})
        self.assertEqual(result['action_page_urls'],['original-action'])

    def test_new_unmapped_work_or_pending_source_event_is_conservative(self):
        data=self.fixture();data['tasks']=[{'url':'f'*32,'State':'InProgress','ResumeStep':'ResolveProjectSources'}]
        self.assertEqual(len(discovery_watch.plan(data)['source_metadata']),6)
        data['tasks']=[];data['index_page']=page('b'*32,block({'record_type':'scan-event-index-v1','root_id':'a'*32,'pending':{'one':{'kind':'source'}}}),{})
        self.assertEqual(len(discovery_watch.plan(data)['source_metadata']),6)

    def test_partial_view_or_missing_active_action_route_refuses(self):
        data=self.fixture();data['tasks_complete']=False
        with self.assertRaises(ValueError):discovery_watch.plan(data)
        data['tasks_complete']=True;data['tasks']=[{'url':'1'*32,'State':'WaitingForOperator','Category':'ContentReview'}]
        with self.assertRaises(ValueError):discovery_watch.plan(data)

    def test_missing_original_event_index_cannot_hide_source_backlog(self):
        data=self.fixture();del data['index_page']
        self.assertEqual(len(discovery_watch.plan(data)['source_metadata']),6)


class FailureCapture(unittest.TestCase):
    def test_original_error_survives_failed_probe_and_recovery(self):
        original={'isError':True,'structuredContent':{'error':{'code':'RATE_LIMIT_EXCEEDED','message':'retry later','retry_after_seconds':12}},'content':[{'type':'text','text':'Original diagnostic'}]}
        result=connector_capture.normalize({'response':original,'capture_ref':'capture:mail','observed_at':'2026-11-02T12:00:00Z'})
        self.assertEqual(result['original'],original);self.assertTrue(result['failed'])
        data=fixture();data['observations']['mail'].update(complete=False,failure=result,next_cursor=None)
        first=event_probe.probe(data);self.assertEqual(first['status'],'ScanDiscoveryRequired')
        self.assertEqual(first['candidate_index']['feeds']['mail']['last_failure']['capture_ref'],'capture:mail')
        data['index_page']=saved(first);data['observations']['mail'].update(complete=True);del data['observations']['mail']['failure']
        recovered=event_probe.probe(data);failure=recovered['candidate_index']['feeds']['mail']['last_failure']
        self.assertIn('recovered_at',failure);self.assertEqual(failure['capture_sha256'],result['capture_sha256'])

    def test_thrown_error_message_is_not_an_empty_serialized_object(self):
        for original in [{},{'exception':{}},{'exception':{'name':'Error'}}]:
            with self.assertRaises(ValueError):connector_capture.normalize({'response':original,'capture_ref':'capture:x','observed_at':'2026-11-02T12:00:00Z'})
        result=connector_capture.normalize({'response':{'exception':{'name':'Error','message':'connection closed'}},'capture_ref':'capture:x','observed_at':'2026-11-02T12:00:00Z'})
        self.assertTrue(result['failed']);self.assertEqual(result['original']['exception']['message'],'connection closed')

    def test_error_cannot_claim_complete_coverage_and_customer_error_prose_is_not_failure(self):
        data=fixture();capture=connector_capture.normalize({'response':{'isError':True},'capture_ref':'capture:x','observed_at':data['now']})
        data['observations']['mail']['failure']=capture
        with self.assertRaises(ValueError):event_probe.probe(data)
        result=connector_capture.normalize({'response':{'text':'Customer says there was an error in the brochure'},'capture_ref':'capture:y','observed_at':data['now']})
        self.assertFalse(result['failed'])

    def test_new_helpers_work_in_one_capture_batch_and_do_not_mutate_inputs(self):
        original={'isError':True,'content':[{'type':'text','text':'failure'}]};before=copy.deepcopy(original)
        result=local_checks.run({'checks':[{'name':'raw','operation':'connector.capture','input':{'response':{'$capture':'failure'},'capture_ref':'capture:x','observed_at':'2026-11-02T12:00:00Z'}}]}, {'failure':original})
        self.assertEqual(result['status'],'LocalChecksPassed');self.assertEqual(original,before)


if __name__=='__main__':unittest.main()
