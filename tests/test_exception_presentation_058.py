"""System failures are not operator homework; keep machine evidence off the first screen."""
import copy
import json
import re
import unittest

from test_notion_checks import page
from test_operator_experience import source
from email_presentation import blocks
import exception_presentation as display
import operator_experience


def fixture():
    proof={'record_type':'material-handoff-recovery-v1','send_complete':True,'retry_send_allowed':False,'original_message_id':'original-mail'}
    body='## Current status\n\nTechnical failure.\n\n```json\n'+json.dumps(proof)+'\n```'
    task=page(body);task['id']='b'*32
    props={'Category':'ExecutionExceptions','State':'NeedsCorrection','ActionPageURL':'https://app.notion.com/p/'+'c'*32}
    task['text']=task['text'].replace('{"title":"Test"}',json.dumps(props))
    action=page(body);action['id']='c'*32
    return dict(task=task,action=action,resolution_owner='System',problem='The follow-up was not registered.',
                impact='The email and CRM record are complete; the notification is not queued.',
                next_step='System maintenance will repair the original inquiry association.')


class SystemExceptionPresentationTests(unittest.TestCase):
    def test_system_failure_preserves_state_and_provider_history_without_human_request(self):
        d=fixture();r=display.plan(d)
        self.assertFalse(r['operator_action_required']);self.assertFalse(r['business_complete'])
        p=r['writes'][0]['properties'];self.assertEqual(p['ResolutionOwner'],'System')
        self.assertEqual(p['RequiredInputs'],'');self.assertNotIn('State',p)
        self.assertNotIn('Consent',p);self.assertFalse(r['send_allowed'])
        old=blocks(d['task'],'material-handoff-recovery-v1')[1]
        for w in r['writes'][1:]:
            self.assertIn('No action required',w['new_str'])
            self.assertNotIn('```',w['new_str'].split('<toggle>')[0])
            saved=page(w['new_str'])
            self.assertEqual(blocks(saved,'material-handoff-recovery-v1')[1],old)

    def test_operator_exception_needs_a_specific_question_and_existing_input_route(self):
        d=fixture();d['resolution_owner']='Operator'
        with self.assertRaises(ValueError):display.plan(d)
        d['question']='Please choose the correct recipient email address.'
        r=display.plan(d);self.assertTrue(r['operator_action_required'])
        self.assertEqual(r['writes'][0]['properties']['RequiredInputs'],d['question'])
        self.assertTrue(all(w['command'] != 'replace_content' for w in r['writes']))
        self.assertIn(d['question'],r['writes'][1]['content_updates'][0]['new_str'])

    def test_controls_and_child_records_cannot_be_hidden_by_system_classification(self):
        for content in ('- [x] Confirm','<page url="https://app.notion.com/p/'+'d'*32+'">Child</page>'):
            d=fixture();d['action']['text']=d['action']['text'].replace('</content>',content+'\n</content>')
            with self.assertRaises(ValueError):display.plan(d)

    def test_machine_payload_or_vague_ownership_is_not_business_copy(self):
        for field,value in [('problem','{"record_type":"error"}'),('next_step','TaskId = internal'),('resolution_owner','Unknown')]:
            d=fixture();d[field]=value
            with self.assertRaises(ValueError):display.plan(d)

    def test_system_feedback_never_asks_to_fill_or_rerun(self):
        r=operator_experience.feedback({'task':{'PageId':'b'*32,'State':'NeedsCorrection','Mode':'Automatic',
                    'Category':'ExecutionExceptions','ContentVersion':'v1','ResolutionOwner':'System'}})
        self.assertFalse(r['operator_action_required']);self.assertIsNone(r['continue_command'])
        self.assertEqual(r['stage'],'system_recovery')

    def test_new_mail_records_have_a_closed_technical_container(self):
        from test_consent_review_053 import prepared
        import consent_review
        r=consent_review.render(prepared()['package'])
        self.assertTrue(r['technical_content'].startswith('<toggle>'))
        self.assertEqual(blocks(page(r['technical_content']),'email-review-v4')[1],prepared()['package'])

    def test_repeated_same_presentation_has_zero_writes(self):
        d=fixture();r=display.plan(d)
        for w in r['writes']:
            key='task' if w['page_id']=='b'*32 else 'action'
            if w['command']=='replace_content':
                d[key]['text']=re.sub(r'<content>.*?</content>',lambda _: '<content>\n'+w['new_str']+'\n</content>',d[key]['text'],flags=re.S)
            else:
                props=json.loads(re.search(r'<properties>(.*?)</properties>',d[key]['text'],re.S)[1]);props.update(w['properties'])
                d[key]['text']=re.sub(r'<properties>.*?</properties>',lambda _:'<properties>'+json.dumps(props)+'</properties>',d[key]['text'],flags=re.S)
        self.assertEqual(display.plan(d)['writes'],[])

    def test_human_attention_requires_ownership_question_and_input_route(self):
        s=source();state=json.loads(re.search(r'<data-source-state>(.*?)</data-source-state>',s['text'])[1]);state['schema']['ResolutionOwner']={'type':'text'}
        s['text']='<data-source-state>'+json.dumps(state)+'</data-source-state>'
        r=operator_experience.today_views({'page':page('Today'),'pending_source':s})
        attention=next(v for v in r['views'] if v['key']=='attention')['args']['configure']
        for requirement in ('"ResolutionOwner" = "Operator"','"RequiredInputs" IS NOT EMPTY','"ActionPageURL" IS NOT EMPTY'):
            self.assertIn(requirement,attention)
        system=display.system_view({'page':page('Dashboard'),'pending_source':s})
        self.assertEqual(system['statements'],'')
        self.assertIn('"ResolutionOwner" IS EMPTY',system['view']['configure'])
        self.assertIn('"ResolutionOwner" != "Operator"',system['view']['configure'])


if __name__=='__main__':unittest.main()
