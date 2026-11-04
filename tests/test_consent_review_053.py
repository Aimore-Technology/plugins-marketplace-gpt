"""Native one-click consent on the original task, with no second form/Submit."""
import copy
import json
import unittest

from test_plain_email_051 import prepared as legacy_prepared
from test_email_flow_049 import response
from test_pre_action_order import page
import consent_review
import email_flow
import publication_integrity


def prepared():
    p = legacy_prepared()['package']
    return email_flow.prepare({'transport':{'manifest':p['manifest'],
         'write_result':response(p['manifest']['draft_id'])},
         **{k:p[k] for k in ('root_id','source_page_id','source_key','action_page_id',
                             'operator_id','window','crm_target')},
         'source_write':response(p['source_page_id'])})


def captures(consent=True):
    package = prepared()['package']; rendered = email_flow.render({'package':package})
    props = {**rendered['properties'],'State':'WaitingForOperator','Consent':consent}
    content = '\n'.join('```json\n'+json.dumps(x)+'\n```' for x in rendered['task_records'])
    task=page(content);task['id']=package['task_page_id']
    task['text']=task['text'].replace('<properties>{"title":"Test"}</properties>',
                                     '<properties>'+json.dumps(props)+'</properties>')
    return {'task':task,'task_id':package['task_page_id'],'operator_id':package['operator_id'],
            'now':'2026-11-04T13:00:00+10:30'}


def edit_prop(d,name,value):
    from email_presentation import properties
    original=properties(d['task']);changed={**original,name:value}
    d['task']['text']=d['task']['text'].replace(json.dumps(original),json.dumps(changed),1)


def dispatch_input():
    d=captures();a=email_flow.accept(d)
    d.update(policy='one-cycle-approved-work',sender_account=a['package']['manifest']['from_address'],
             controls={k:True for k in ('scan_enabled','channel_enabled','no_reply_or_stop',
                                        'attempt_clear','approval_current','date_allowed')},
             attempt_id='one-click-attempt',accepted_input_sha256=a['input_sha256'],
             attempt_write=response(d['task_id']),send_tool='mcp__gmail__send_draft')
    return d


class ConsentTests(unittest.TestCase):
    def test_new_plain_reply_is_one_original_row_without_action_form(self):
        p=prepared()['package'];r=email_flow.render({'package':p})
        self.assertEqual(p['record_type'],'email-review-v4')
        self.assertEqual(p['action_page_id'],p['task_page_id'])
        self.assertEqual(r['properties']['Consent'],'__NO__')
        self.assertNotIn('content',r)
        self.assertNotIn('- [ ]',r['properties']['ReviewText'])
        self.assertNotIn('Submit decision',r['properties']['ReviewText'])
        self.assertNotIn('```',r['properties']['ReviewText'])

    def test_checkbox_is_sufficient_without_action_capture_or_second_submit(self):
        r=email_flow.dispatch(dispatch_input())
        self.assertTrue(r['send_allowed'])
        self.assertEqual(r['call']['args'],{'draft_id':'r-draft-1'})

    def test_unchecked_and_revoked_consent_never_send(self):
        self.assertEqual(email_flow.accept(captures(False))['status'],'EmailConsentPending')
        d=dispatch_input();edit_prop(d,'Consent',False)
        self.assertFalse(email_flow.dispatch(d)['send_allowed'])

    def test_narrative_or_window_edits_require_new_synchronized_version(self):
        for old,new in [('918,000','900,000'),('receiver@example.invalid','other@example.invalid'),
                         ('17:00:00','18:00:00')]:
            d=captures();d['task']['text']=d['task']['text'].replace(old,new,1)
            self.assertEqual(email_flow.accept(d)['status'],'EmailRevisionRequired')

    def test_truthy_strings_numbers_and_body_text_never_supply_checkbox_consent(self):
        for value in ('true','yes',1,'Approve'):
            d=captures();edit_prop(d,'Consent',value)
            with self.assertRaises(ValueError):email_flow.accept(d)
        d=captures(False);d['task']['text']=d['task']['text'].replace('</content>',
                       '\n- [x] Agree and send\nConsent: true\n</content>')
        self.assertEqual(email_flow.accept(d)['status'],'EmailConsentPending')

    def test_wrong_actor_version_terminal_and_other_task_are_rejected(self):
        for name,value in [('OperatorId','other'),('ContentVersion','other'),('State','Completed')]:
            d=captures();edit_prop(d,name,value)
            with self.assertRaises(ValueError):email_flow.accept(d)
        d=captures();d['task_id']='b'*32
        with self.assertRaises(ValueError):email_flow.accept(d)

    def test_all_send_guards_still_apply_after_consent(self):
        for name in dispatch_input()['controls']:
            d=dispatch_input();d['controls'][name]=False
            self.assertFalse(email_flow.dispatch(d)['send_allowed'],name)
        for state in ('Unknown','Pending','ProviderAccepted'):
            d=dispatch_input();d['attempt_status']=state
            self.assertFalse(email_flow.dispatch(d)['send_allowed'])

    def test_persisted_consent_remains_checked_and_resumes_without_second_click(self):
        d=dispatch_input();a=email_flow.accept(d)
        d['task']['text']=d['task']['text'].replace('</content>','\n```json\n'+json.dumps(a)+'\n```\n</content>')
        self.assertTrue(email_flow.accept(d)['reused_accepted_snapshot'])
        self.assertTrue(email_flow.dispatch(d)['send_allowed'])
        edit_prop(d,'Consent',False)
        self.assertFalse(email_flow.dispatch(d)['send_allowed'])

    def test_discovery_observes_only_actual_checkbox_and_narrative_changes(self):
        d=captures(False);first=consent_review.observe(d)['record']
        self.assertEqual(first['events'],[])
        d['now']='2026-11-04T13:30:00+10:30'
        self.assertEqual(consent_review.observe(d)['record'],first)
        edit_prop(d,'Consent',True);r=consent_review.observe(d)['record']
        self.assertNotEqual(r['revision'],first['revision'])
        self.assertEqual(r['events'][0]['kind'],'submission')

    def test_new_version_publication_requires_narrative_and_unchecked_consent_together(self):
        p=prepared()['package'];r=email_flow.render({'package':p})
        body='\n'.join('```json\n'+json.dumps(x)+'\n```' for x in r['task_records'])
        consent_review.check_publication('',body,r['properties'])
        for change in ({'Consent':'__YES__'},{'Consent':None},{'ReviewText':'Other text'}):
            with self.assertRaises(ValueError):
                consent_review.check_publication('',body,{**r['properties'],**change})

    def test_old_content_only_confirm_is_not_consent(self):
        d=captures(False);edit_prop(d,'Decision','Confirm')
        self.assertFalse(email_flow.accept(d)['send_allowed'])

    def test_withdraw_then_reconsent_gets_new_event_without_timestamp_only_events(self):
        d=captures(False);previous=consent_review.observe(d)['record']['revision']
        revisions=[]
        for i,value in enumerate((True,False,True)):
            edit_prop(d,'Consent',value);d['previous_revision']=previous
            d['now']='2026-11-04T13:0'+str(i)+':00+10:30'
            previous=consent_review.observe(d)['record']['revision'];revisions.append(previous)
        self.assertNotEqual(revisions[0],revisions[2])
        d['previous_revision']=previous;d['now']='2026-11-04T14:00:00+10:30'
        self.assertEqual(consent_review.observe(d)['record']['revision'],previous)
