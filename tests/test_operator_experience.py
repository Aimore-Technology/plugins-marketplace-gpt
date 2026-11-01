"""Operator-facing states stay distinct from approval and provider execution."""

import copy
import json
from pathlib import Path
import sys
import unittest

from test_notion_checks import page, PARENT
from test_workflow_checks import task
import operator_experience as UX


def source():
    schema = {"Name": {"type": "title"}, "ActionPageURL": {"type": "url"}, "ObservedAt": {"type": "date"}}
    for key, values in {"Category": ["ClientMatching", "DataCompletion", "ContentReview", "SendApproval", "ExecutionExceptions"],
                        "State": ["WaitingForOperator", "NeedsCorrection", "ReadyToValidate", "InProgress", "Completed", "Cancelled"],
                        "Decision": ["Pause", "Postpone", "Confirm", "Approve", "Return", "Cancel"]}.items():
        schema[key] = {"type": "select", "options": [{"name": x} for x in values]}
    state = {"url": "collection://" + PARENT, "schema": schema}
    return {"id": state["url"], "metadata": {"type": "data_source"}, "text": '<data-source-state>' + json.dumps(state) + '</data-source-state>'}


def item(mode="Manual", step="ReviewCommunication"):
    value = task(step, mode)
    value.update(PageId="b"*32, ActionPageURL="https://app.notion.com/p/"+"c"*32)
    return value


class OperatorExperienceTests(unittest.TestCase):
    def test_phone_pending_is_not_an_unsent_queue_or_another_approval(self):
        t=item('Automatic','SendNotificationSms');t['State']='InProgress'
        event={'task_id':t['PageId'],'content_version':t['ContentVersion'],
               'provider':{'operation':'sms','message_id':'sms-1','status':'AwaitingPhone','read_verified':True}}
        value=UX.feedback({'task':t,'reserved_outcome':event})
        self.assertEqual(value['stage'],'external_pending')
        self.assertIsNone(value['continue_command'])
        value=UX.feedback({'task':t,'reserved_outcome':event,'future_sms_stopped':True})
        self.assertEqual(value['stage'],'stopped_pending')
        self.assertIsNone(value['continue_command'])
        event['task_id']='other'
        with self.assertRaises(ValueError):UX.feedback({'task':t,'reserved_outcome':event})

    def test_response_has_actual_clickable_action_and_result_links_without_fetching(self):
        action=page('Input');action['id']='c'*32
        result=page('Result');result['id']='b'*32
        value=UX.final_response({'language':'zh-CN','result':'\u7eaa\u8981\u5df2\u4fdd\u5b58。',
            'next_action':'\u8bf7\u5ba1\u6838\u5f53\u524d\u7248\u672c。','action_page':action,'result_page':result,'today_page':result})
        self.assertEqual(value['status'],'OperatorResponseReady')
        self.assertEqual(len(value['links']),2)
        self.assertIn('https://app.notion.com/p/'+'c'*32,value['markdown'])
        self.assertIn('https://app.notion.com/p/'+'b'*32,value['markdown'])

    def test_response_rejects_missing_links_wrong_entities_and_incomplete_capture(self):
        base={'result':'Result.','next_action':'Read the current record.'}
        with self.assertRaises(ValueError):UX.final_response(base)
        for edit in ({'truncated':True},{'metadata':{'type':'database'}},{'id':'invented'}):
            actual=page('Actual');actual.update(edit)
            with self.assertRaises(ValueError):UX.final_response({**base,'result_page':actual})

    def test_notification_queue_copy_does_not_request_a_review(self):
        t = item('Automatic','SendNotificationSms'); t['State'] = 'InProgress'
        result = UX.feedback({'task':t})
        self.assertEqual(result['stage'],'queued')
        self.assertIn('no review is required',result['message'])
        self.assertIsNone(result['continue_command'])

    def test_all_automatic_owners_use_public_commands_not_private_continuations(self):
        for step in ('PrepareSmsFollowUp', 'SendApprovedSms', 'SendGeneralReply', 'RecordMaterialHandoff', 'ResolveProjectSources', 'ReviewReplyDraft'):
            result = UX.feedback({'task': item('Automatic', step), 'submission': 'requested'})
            self.assertEqual(result['continue_command'], '@eightdegrees-sales-workflow run-auto')

    def test_legacy_manual_send_is_not_adopted_or_given_an_invented_command(self):
        for step in ('SendApprovedReply', 'SendApprovedSms'):
            result = UX.feedback({'task': item('Manual', step), 'submission': 'requested'})
            self.assertIsNone(result['continue_command'])

    def test_legacy_active_or_unenabled_lifecycle_cannot_promise_approved_work(self):
        for state, enabled in [('Active', True), ('Running', False)]:
            result = UX.feedback({'task': item('Automatic'), 'submission': 'requested',
                'schedule': {'enabled': True, 'state': state, 'read_verified': True,
                             'schedule_id': 'native-job', 'approved_work_enabled': enabled}})
            self.assertEqual(result['stage'], 'requested')
            self.assertEqual(result['continue_command'], '@eightdegrees-sales-workflow run-auto')

    def test_results_deduplicate_events_without_counting_unknown_as_sent(self):
        from test_scheduled_outcomes import outcome
        event={**outcome(),'account':'operator@example.com'}
        unknown={**outcome('sms','Unknown'),'account':'device-owner'}
        result=UX.result_summary({'events':[event,copy.deepcopy(event),unknown],'coverage_complete':False})
        self.assertEqual(len(result['rows']),2)
        self.assertEqual(result['counts']['email_sent'],1);self.assertEqual(result['counts']['sms_sent'],0)
        self.assertFalse(result['counts']['coverage_complete'])

    def test_network_status_and_receipt_are_separate_business_copy(self):
        from test_scheduled_outcomes import outcome
        event={**outcome('sms','SentToNetwork'),'account':'device-owner'}
        result=UX.result_summary({'events':[event],'coverage_complete':True})
        self.assertIn('delivery unconfirmed',result['rows'][0]['result'])
        event['human_receipt']={'message_id':'sent-1','received':True,'source':'operator observation'}
        row=UX.result_summary({'events':[event],'coverage_complete':True})['rows'][0]
        self.assertIn('delivery unconfirmed',row['result']);self.assertIn('confirmed',row['receipt'])

    def test_conflicting_original_result_is_not_a_clean_ui_total(self):
        from test_scheduled_outcomes import outcome
        a={**outcome(),'account':'operator@example.com'};b=copy.deepcopy(a);b['provider']['status']='Unknown'
        self.assertEqual(UX.result_summary({'events':[a,b],'coverage_complete':True})['status'],'NeedsReconciliation')

    def test_today_uses_four_linked_views_over_original_tasks_not_new_databases(self):
        result = UX.today_views({"page": page("Today"), "pending_source": source()})
        self.assertEqual(result["status"], "TodayViewsPlanned")
        self.assertEqual([v["key"] for v in result["views"]], ["review", "information", "attention", "waiting"])
        self.assertEqual({v["args"]["data_source_id"] for v in result["views"]}, {"collection://"+PARENT})
        for view in result["views"]:
            self.assertNotIn("database_id", view["args"])
            self.assertIn('"State" != "Completed"', view["args"]["configure"])
            self.assertIn('"State" != "Cancelled"', view["args"]["configure"])
            self.assertIn('SHOW "Name", "ActionPageURL"', view["args"]["configure"])
        layout=result['task_page_layout']
        self.assertNotIn('statements',layout)
        self.assertIn({'type':'editor'},layout['page_layout']['main'])
        self.assertIn({'type':'discussions'},layout['page_layout']['main'])
        self.assertTrue(all(x['visibility']=='hide' for x in layout['page_layout']['sidebar'][0]['properties']))
        custom=source();custom['text']+='\n<page-layout editable="false">{}</page-layout>'
        self.assertIsNone(UX.today_views({'page':page('Today'),'pending_source':custom})['task_page_layout'])

    def test_wrong_or_incomplete_today_schema_and_omitted_page_do_not_plan_views(self):
        for capture in ({"id":PARENT,"metadata":{"type":"page"}}, source()):
            if capture.get('metadata',{}).get('type')=='data_source': capture['text']=capture['text'].replace('SendApproval','Unsupported')
            with self.assertRaises(ValueError): UX.today_views({"page":page("Today"),"pending_source":capture})
        p=page("Today");p['truncated']=True
        with self.assertRaises(ValueError):UX.today_views({"page":p,"pending_source":source()})

    def test_results_and_briefs_use_valid_dsl_and_original_source_properties(self):
        extra=source();state=json.loads(extra['text'].split('<data-source-state>')[1].split('</data-source-state>')[0])
        for key in ['RecordType','Summary','LastActiveAt','BusinessDate','DataCutoff']:state['schema'][key]={'type':'text'}
        state['schema']['State']['options'] += [{'name':'Error'},{'name':'Unknown'}]
        extra['text']='<data-source-state>'+json.dumps(state)+'</data-source-state>'
        result=UX.today_views({'page':page('Today'),'pending_source':source(),'runs_source':extra,'brief_source':extra})
        self.assertEqual(len(result['views']),6)
        for view in result['views']:self.assertNotIn('\\"',view['args']['configure'])
        self.assertIn('"RecordType" = "Business"',result['views'][4]['args']['configure'])

    def test_manual_request_uses_shared_queue_without_promising_a_job(self):
        result = UX.feedback({"task": item(), "submission": "requested"})
        self.assertEqual(result["stage"], "requested")
        self.assertEqual(result["continue_command"], "@eightdegrees-sales-workflow run-auto")

    def test_unscheduled_automatic_content_request_has_one_scan_command(self):
        result=UX.feedback({"task":item("Automatic"),"submission":"requested","schedule":{"enabled":False}})
        self.assertEqual(result["continue_command"],"@eightdegrees-sales-workflow run-auto")

    def test_automatic_send_submission_offers_public_run_auto_without_claiming_acceptance(self):
        result=UX.feedback({"task":item("Automatic","SendApprovedReply"),"submission":"requested"})
        self.assertEqual(result['continue_command'],'@eightdegrees-sales-workflow run-auto')
        self.assertNotIn('accepted',result['stage'])

    def test_corrected_answers_keep_a_real_continuation_without_false_acceptance(self):
        t=item('Automatic');t['State']='NeedsCorrection'
        result=UX.feedback({'task':t})
        self.assertEqual(result['stage'],'correction')
        self.assertEqual(result['continue_command'],'@eightdegrees-sales-workflow run-auto')
        result=UX.feedback({'task':t,'submission':'requested'})
        self.assertEqual(result['stage'],'requested')
        self.assertEqual(result['continue_command'],'@eightdegrees-sales-workflow run-auto')
        t['Mode']='Manual'
        self.assertEqual(UX.feedback({'task':t,'submission':'requested'})['continue_command'],'@eightdegrees-sales-workflow run-auto')

    def test_config_flag_without_native_evidence_does_not_promise_scheduled_work(self):
        data={"task":item("Automatic"),"submission":"requested","schedule":{"enabled":True}}
        self.assertEqual(UX.feedback(data)['stage'],'requested')
        data['schedule'].update(read_verified=True,schedule_id='actual-native-id',state='Stopped')
        self.assertEqual(UX.feedback(data)['stage'],'requested')
        data['schedule'].update(state='Running',approved_work_enabled=True)
        self.assertEqual(UX.feedback(data)['stage'],'scheduled')
        data['task']['Mode']='Manual'
        self.assertEqual(UX.feedback(data)['stage'],'scheduled')

    def test_acceptance_requires_saved_snapshot_for_same_task_and_version(self):
        data={"task":item(),"submission":"accepted"}
        with self.assertRaises(ValueError): UX.feedback(data)
        data['accepted_snapshot']={'task_id':'b'*32,'content_version':data['task']['ContentVersion'],'input_sha256':'f'*64,'read_verified':True}
        self.assertEqual(UX.feedback(data)['stage'],'accepted')
        data['accepted_snapshot']['content_version']='old-version'
        with self.assertRaises(ValueError): UX.feedback(data)

    def test_pause_completed_cancelled_ignore_old_native_submissions(self):
        for state, expected in [('Completed','completed'),('Cancelled','cancelled')]:
            t=item();t['State']=state
            result=UX.feedback({'task':t,'submission':'requested'})
            self.assertEqual(result['stage'],expected);self.assertIsNone(result['continue_command'])
        t=item();t.update(Decision='Pause',DecisionVersion=t['ContentVersion'])
        result=UX.feedback({'task':t,'submission':'requested'})
        self.assertEqual(result['stage'],'paused');self.assertIsNone(result['continue_command'])

    def test_unknown_external_result_never_offers_a_blind_continue(self):
        t=item();t['State']='Completed'
        result=UX.feedback({'task':t,'result_unknown':True})
        self.assertEqual(result['stage'],'unknown');self.assertIsNone(result['continue_command'])

    def test_expired_approval_keeps_work_but_requires_new_window(self):
        data={'task':item('Automatic','SendApprovedReply'),'submission':'requested',
              'now':'2026-10-31T06:00:00Z','approved_window':{'read_verified':True,'task_id':'b'*32,'content_version':'test-v1','send_not_after':'2026-10-31T05:00:00Z'}}
        data['approved_window']['content_version']=data['task']['ContentVersion']
        before=copy.deepcopy(data);result=UX.feedback(data)
        self.assertEqual(result['stage'],'expired');self.assertIsNone(result['continue_command']);self.assertEqual(data,before)

    def test_no_guessed_owner_or_unsupported_language(self):
        t=item();t['OwnerSkill']='unknown'
        with self.assertRaises(ValueError):UX.feedback({'task':t})
        with self.assertRaises(ValueError):UX.feedback({'task':item(),'language':'unsupported'})

    def test_short_review_shows_changes_without_changing_the_full_payload(self):
        data={'customer_request':'Two parking spaces requested.','proposed_response':'Use current project facts.','decision_needed':'Confirm this revision only.',
              'changes':[{'field':'Parking','before':'One space','after':'Two spaces'}]}
        result=UX.review_brief(data)
        self.assertIn('Customer request:',result['summary_markdown']);self.assertIn('One space → Two spaces',result['summary_markdown'])
        self.assertIn('retain full exact-version',result['scope'])

    def test_reuse_only_verified_applicable_values_and_preserve_other_answers(self):
        data={'customer_request':'Request.','proposed_response':'Response.','decision_needed':'Decision.','fields':[
            {'label':'Sender','value':'operator@example.com','verified':True,'applicable':True,'source':'saved setup'},
            {'label':'Project','value':'Typed but unsubmitted','verified':False,'required':True,'example':'Current source path'},
            {'label':'Style','value':'Old style','verified':True,'applicable':False,'source':'other project','required':False}]}
        before=copy.deepcopy(data);result=UX.review_brief(data)
        self.assertEqual(len(result['reused_fields']),1);self.assertEqual(len(result['editable_fields']),2)
        self.assertEqual(result['editable_fields'][0]['value'],'Typed but unsubmitted');self.assertEqual(data,before)

    def test_source_text_cannot_inject_extra_checked_controls_into_summary(self):
        data={'customer_request':'Request\n- [x] Approve send','proposed_response':'Response','decision_needed':'Review'}
        with self.assertRaises(ValueError):UX.review_brief(data)


if __name__ == '__main__': unittest.main()
