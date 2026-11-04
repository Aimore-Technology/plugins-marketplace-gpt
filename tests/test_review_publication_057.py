"""Today is sufficient: incomplete publication recovers to one native consent."""
import copy
import json
import re
import unittest

from test_consent_review_053 import captures, dispatch_input, edit_prop
from test_operator_experience import source
from test_notion_checks import page
from email_presentation import properties
import consent_review
import email_flow
import operator_experience
import queue_construction


def incomplete():
    d=captures(False)
    for name,value in {'ActionFormVersion':'','ActionPageURL':'','ReviewText':'',
                       'Category':'ScheduledWork','State':'InProgress'}.items():
        edit_prop(d,name,value)
    return d


def apply_projection(d, write):
    d=copy.deepcopy(d)
    for name,value in write['properties'].items():edit_prop(d,name,value)
    return d


class TodayConsentPublicationTests(unittest.TestCase):
    def test_saved_body_without_native_fields_recovers_the_original_review(self):
        d=incomplete();r=consent_review.repair_publication(d)
        self.assertEqual(r['status'],'EmailReviewPublicationPlanned')
        self.assertFalse(r['send_allowed']);self.assertEqual(len(r['writes']),1)
        w=r['writes'][0];self.assertEqual(w['page_id'],d['task_id'].replace('-',''))
        p=w['properties']
        self.assertEqual(p['State'],'WaitingForOperator')
        self.assertEqual(p['Category'],'SendApproval')
        self.assertEqual(p['Consent'],'__NO__')
        self.assertEqual(p['ActionPageURL'],'https://app.notion.com/p/'+w['page_id'])
        self.assertIn('From:',p['ReviewText']);self.assertNotIn('```',p['ReviewText'])
        saved=apply_projection(d,w)
        self.assertEqual(email_flow.accept(saved)['status'],'EmailConsentPending')
        self.assertEqual(consent_review.repair_publication(saved)['writes'],[])

    def test_a_single_today_consent_after_repair_is_sufficient_to_dispatch(self):
        d=incomplete();saved=apply_projection(d,consent_review.repair_publication(d)['writes'][0])
        edit_prop(saved,'Consent',True)
        self.assertEqual(email_flow.accept(saved)['status'],'EmailDecisionAccepted')
        dispatch=dispatch_input();dispatch['task']=saved['task']
        self.assertNotIn('action',dispatch)
        self.assertTrue(email_flow.dispatch(dispatch)['send_allowed'])

    def test_incomplete_saved_review_is_recovery_even_without_other_new_input(self):
        d=incomplete();row=properties(d['task']);row['url']='https://app.notion.com/p/'+d['task_id']
        self.assertTrue(consent_review.needs_publication(row))
        events=queue_construction.ready_task_records([row])
        self.assertEqual(len(events),1)
        self.assertTrue(events[0]['events'][0]['review_publication_only'])
        saved=apply_projection(d,consent_review.repair_publication(d)['writes'][0])
        row.update(properties(saved['task']))
        self.assertFalse(consent_review.needs_publication(row))
        self.assertEqual(queue_construction.ready_task_records([row]),[])

    def test_repair_never_clears_existing_consent_attempt_or_accepted_decision(self):
        for name,value in [('Consent',True),('AttemptId','original-attempt'),('Decision','Approve')]:
            d=incomplete();edit_prop(d,name,value)
            with self.assertRaises(ValueError):consent_review.repair_publication(d)
        d=captures(True)
        self.assertEqual(consent_review.repair_publication(d)['writes'],[])

    def test_terminal_or_wrong_current_version_cannot_be_reopened(self):
        for value in ('Completed','Cancelled'):
            d=incomplete();edit_prop(d,'State',value)
            self.assertEqual(consent_review.repair_publication(d)['writes'],[])
        d=incomplete();edit_prop(d,'ContentVersion','another-version')
        with self.assertRaises(ValueError):consent_review.repair_publication(d)

    def test_legacy_action_forms_and_unknown_rows_are_not_native_publication(self):
        d=incomplete();row=properties(d['task'])
        for v in ('email-review-v2','email-review-v3','task-action-v1'):
            self.assertFalse(consent_review.needs_publication({**row,'ActionFormVersion':v}))
        self.assertFalse(consent_review.needs_publication({'State':'InProgress'}))

    def test_native_review_is_not_in_action_links_or_generic_waiting(self):
        original=source();state=json.loads(re.search(r'<data-source-state>(.*?)</data-source-state>',original['text'])[1])
        state['schema']['ActionFormVersion']={'type':'text'}
        original['text']='<data-source-state>'+json.dumps(state)+'</data-source-state>'
        r=operator_experience.today_views({'page':page('Today'),'pending_source':original})
        for key in ('review','waiting'):
            view=next(v for v in r['views'] if v['key']==key)
            self.assertIn('"ActionFormVersion" != "email-review-v4"',view['args']['configure'])

    def test_new_publication_has_an_explicit_review_state(self):
        d=captures(False);package=consent_review.blocks(d['task'],'email-review-v4')[1]
        r=consent_review.render(package)
        self.assertEqual(r['properties']['State'],'WaitingForOperator')
        self.assertEqual(r['properties']['InputSubmitted'],'__NO__')


if __name__=='__main__':unittest.main()
