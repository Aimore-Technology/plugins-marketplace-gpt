"""Submitted legacy forms must leave needs-input without inventing approval."""
import copy
import json
import re
import unittest

from test_notion_checks import page
from test_operator_experience import source
import operator_experience
import queue_construction
import task_submission

TASK, ACTION = 'b'*32, 'c'*32


def fixture():
    binding = dict(record_type='action-binding', TaskPageId=TASK, ActionPageId=ACTION,
                   TaskId='original:ResolveProjectSources:sources-v1', StepId='ResolveProjectSources',
                   Category='DataCompletion', Mode='Automatic', ContentVersion='sources-v1',
                   OwnerSkill='eightdegrees-sales-reply', ResumeStep='ResolveProjectSources',
                   ResumeContractVersion='resume-v1', OperatorId='configured-operator', SubmissionLabel='Submit sources')
    code = '```json\n'+json.dumps(binding)+'\n```'
    task = page('## Current status\n\nWaiting for input.\n\n## Binding\n\n'+code)
    task['id'] = 'https://app.notion.com/'+TASK
    props = {**{k:v for k,v in binding.items() if k not in {'record_type','SubmissionLabel','TaskPageId','ActionPageId'}},
             'ActionPageURL':'https://app.notion.com/p/'+ACTION, 'ActionFormVersion':'task-action-v1',
             'State':'WaitingForOperator', 'InputSubmitted':'__NO__',
             'SourceKey':'operator@example.com:inbound:message-1', 'url':'https://app.notion.com/'+TASK}
    task['text'] = task['text'].replace('{"title":"Test"}',json.dumps(props))
    action = page('## Current status\n\nAwaiting submission.\n\n## Your input\n\nUse an acknowledgement-only reply; facts unavailable.\n\n- [x] Submit sources\n\n## Binding\n\n'+code)
    action['id'] = ACTION
    return dict(task=task,action=action,now='2026-11-04T13:00:00Z',language='en')


def apply_task(d, writes):
    d = copy.deepcopy(d)
    for write in writes:
        target = 'task' if write['page_id'] == TASK else 'action'
        if write['command'] == 'update_content':
            for patch in write['content_updates']:
                d[target]['text'] = d[target]['text'].replace(patch['old_str'],patch['new_str'])
        else:
            props = json.loads(re.search(r'<properties>(.*?)</properties>',d['task']['text'],re.S)[1])
            props.update(write['properties'])
            d['task']['text'] = re.sub(r'<properties>.*?</properties>',lambda _: '<properties>'+json.dumps(props)+'</properties>',d['task']['text'],flags=re.S)
    return d


class SubmissionProjectionTests(unittest.TestCase):
    def test_native_wake_fingerprints_helpers_without_dumping_python(self):
        import current_rules
        r=current_rules.load()
        self.assertIn('scripts/task_submission.py',r['rule_files'])
        self.assertFalse(any(name.endswith('.py') for name in r['rules']))

    def test_checked_old_form_queues_original_step_without_approving_anything(self):
        d = fixture(); r = task_submission.observe(d)
        self.assertEqual(r['status'],'TaskSubmissionQueued')
        self.assertFalse(r['send_allowed']); self.assertFalse(r['facts_approved'])
        self.assertFalse(r['snapshot']['acceptance'])
        projected = r['writes'][1]['properties']
        self.assertEqual(projected['State'],'ReadyToValidate')
        self.assertEqual(projected['InputSubmitted'],'__YES__')
        self.assertNotIn('Decision',projected)
        saved = apply_task(d,r['writes'])
        from email_presentation import properties
        records = queue_construction.ready_task_records([properties(saved['task'])])
        self.assertEqual(records[0]['events'][0]['step'],'ResolveProjectSources')
        self.assertEqual(task_submission.observe(saved)['writes'],[])

    def test_partial_presentation_failure_repairs_only_the_action_page(self):
        d=fixture(); writes=task_submission.observe(d)['writes']
        saved=apply_task(d,writes[:2])
        r=task_submission.observe(saved)
        self.assertEqual(r['status'],'TaskSubmissionProjectionRepair')
        self.assertEqual(len(r['writes']),1)
        self.assertEqual(r['writes'][0]['page_id'],ACTION)

    def test_new_answers_are_not_deduplicated_as_old_input(self):
        d = fixture(); saved = apply_task(d,task_submission.observe(d)['writes'])
        saved['action']['text'] = saved['action']['text'].replace('facts unavailable','current facts attached')
        self.assertEqual(task_submission.observe(saved)['status'],'TaskSubmissionQueued')

    def test_unsubmitted_and_terminal_input_do_not_reopen(self):
        d = fixture();d['action']['text']=d['action']['text'].replace('[x] Submit','[ ] Submit')
        self.assertEqual(task_submission.observe(d)['writes'],[])
        for state in ('Completed','Cancelled'):
            d=fixture();d['task']['text']=d['task']['text'].replace('WaitingForOperator',state)
            self.assertEqual(task_submission.observe(d)['writes'],[])

    def test_wrong_action_task_version_or_operator_is_rejected(self):
        for key,value in [('id','d'*32),('version','sources-v2'),('operator','different-operator')]:
            d=fixture()
            if key=='id': d['action']['id']=value
            elif key=='version':d['action']['text']=d['action']['text'].replace('sources-v1',value)
            else:d['action']['text']=d['action']['text'].replace('configured-operator',value)
            with self.assertRaises(ValueError):task_submission.observe(d)

    def test_literal_checkbox_is_not_a_submission(self):
        d=fixture();d['action']['text']=d['action']['text'].replace('- [x] Submit sources','```text\n- [x] Submit sources\n```')
        with self.assertRaises(ValueError):task_submission.observe(d)

    def test_results_use_actual_tasks_and_run_history_has_separate_name(self):
        original=source(); r=operator_experience.today_views({'page':page('Today'),'pending_source':original})
        result=next(v for v in r['views'] if v['key']=='task_results')
        self.assertEqual(result['args']['data_source_id'],original['id'])
        self.assertIn('"State" IN ("Completed", "Cancelled")',result['args']['configure'])

    def test_submitted_compatibility_projection_cannot_remain_in_needs_input(self):
        original=source();state=json.loads(re.search(r'<data-source-state>(.*?)</data-source-state>',original['text'])[1])
        state['schema']['InputSubmitted']={'type':'checkbox'}
        original['text']='<data-source-state>'+json.dumps(state)+'</data-source-state>'
        r=operator_experience.today_views({'page':page('Today'),'pending_source':original})
        for v in r['views'][:3]: self.assertIn('"InputSubmitted" = FALSE',v['args']['configure'])
        self.assertIn('"InputSubmitted" = TRUE',r['views'][3]['args']['configure'])

    def test_task_ids_accept_actual_query_urls_with_or_without_p(self):
        from notion_checks import page_id
        for value in ('https://app.notion.com/'+TASK,'https://app.notion.com/p/'+TASK+'?pvs=204'):
            self.assertEqual(page_id(value),TASK)
        with self.assertRaises(ValueError):page_id('https://app.notion.com/Other-'+TASK)


if __name__=='__main__':unittest.main()
