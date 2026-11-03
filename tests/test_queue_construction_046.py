"""Full ready-event construction prevents model-selected queue omissions."""
import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'plugins/eightdegrees-sales-workflow/scripts'))
import queue_construction as queue
import event_probe,scan_cycle
from test_event_probe import fixture,changed,saved,work
from test_email_presentation import page,block
from test_unattended import cycle_fixture

class CompleteQueue(unittest.TestCase):
 def fixture(self):
  d=changed(fixture(),events=[work(source_key='mail:'+str(n),input_digest='message'+str(n)) for n in range(3)])
  d['observations']['scheduled']['records']=[dict(id='brief',revision='date',events=[work(kind='timer',source_key='operator:brief',step='BuildDailyBrief',due_at=d['now'])])]
  index=event_probe.probe(d)
  return dict(settings=d['settings'],root_id=d['root_id'],now=d['now'],index_page=saved(index),tasks=[],tasks_complete=True,source_pages=[],sources_complete=True,items=[])
 def test_all_three_mail_and_due_brief_survive_a_narrow_owner_list(self):
  d=self.fixture();d['items']=[work(kind='recovery',source_key='customer:large',step='ResolveProjectSources',estimated_seconds=600)]
  before=copy.deepcopy(d);r=queue.build(d)
  self.assertEqual(r['ready_event_count'],4);self.assertEqual(r['accounted_event_count'],4)
  self.assertEqual(len(r['items']),5);self.assertEqual(d,before)
  self.assertEqual(sum(v['step']=='ReadMessageBody' for v in r['items']),3)
  self.assertTrue(any(v['step']=='BuildDailyBrief' for v in r['items']))
 def test_fitting_mail_is_selected_when_600_second_phase_does_not_fit(self):
  d=self.fixture();large=work(kind='recovery',source_key='customer:large',step='ResolveProjectSources',estimated_seconds=600)
  d['items']=[large];q=queue.build(d);scan=cycle_fixture()
  scan.update(root_id=d['root_id'],settings=d['settings'],started_at='2026-11-02T11:48:40Z',now=d['now'],budget_seconds=900,reserve_seconds=120,queue_plan=q,items=[large])
  result=scan_cycle.advance(scan)
  self.assertEqual(result['seconds_available_for_work'],100)
  self.assertEqual(result['work'][0]['step'],'ReadMessageBody')
  self.assertEqual(len(result['checkpoint']['work_items']),5)
 def test_incomplete_mail_registry_does_not_block_independent_due_work(self):
  d=self.fixture();d['sources_complete']=False;q=queue.build(d)
  self.assertEqual(len(q['blocks']),3)
  self.assertEqual(len(q['items']),1);self.assertEqual(q['items'][0]['step'],'BuildDailyBrief')
  self.assertEqual(len(q['event_coverage']),4)
 def test_ready_source_preparation_is_backlog_with_unchanged_inputs(self):
  task={'url':'https://app.notion.com/p/'+'c'*32,'TaskId':'original:source',
        'SourceKey':'user@example.com:inbound:m1','Mode':'Automatic','State':'ReadyToValidate',
        'OwnerSkill':'eightdegrees-sales-reply','ResumeStep':'ResolveProjectSources','ContentVersion':'sources-v1'}
  records=queue.ready_task_records([task]);self.assertEqual(len(records),1)
  self.assertEqual(records[0]['events'][0]['estimated_seconds'],600)
  d=fixture();d['ready_task_records']=records;r=event_probe.probe(d)
  self.assertEqual(r['status'],'ScanWorkReady');self.assertEqual(r['ready'][0]['step'],'ResolveProjectSources')
  d['index_page']=saved(r);self.assertEqual(event_probe.probe(d)['ready'],r['ready'])
  d['observations'].pop('recovery');r=event_probe.probe(d)
  self.assertEqual(r['status'],'ScanWorkReady');self.assertFalse(r['coverage_complete'])
 def test_manual_waits_and_sends_are_never_created_from_ready_state(self):
  base={'url':'https://app.notion.com/p/'+'c'*32,'TaskId':'original','SourceKey':'mail:x',
        'Mode':'Automatic','State':'ReadyToValidate','OwnerSkill':'eightdegrees-sales-reply',
        'ResumeStep':'SendApprovedReply','ContentVersion':'v1'}
  self.assertEqual(queue.ready_task_records([base]),[])
  base.update(ResumeStep='ResolveProjectSources',Mode='Manual')
  self.assertEqual(queue.ready_task_records([base]),[])
  base.update(Mode='Automatic',State='WaitingForOperator')
  self.assertEqual(queue.ready_task_records([base]),[])
 def test_future_preparation_waits_and_due_change_has_new_identity(self):
  task={'url':'https://app.notion.com/p/'+'c'*32,'TaskId':'original','SourceKey':'mail:x',
        'Mode':'Automatic','State':'ReadyToValidate','OwnerSkill':'eightdegrees-sales-reply',
        'ResumeStep':'ResolveProjectSources','ContentVersion':'v1','date:NextDue:start':'2026-11-02T13:00:00Z'}
  first=queue.ready_task_records([task]);d=fixture();d['ready_task_records']=first
  r=event_probe.probe(d);self.assertEqual(r['status'],'ScanIdle');self.assertEqual(r['pending_count'],1)
  task['date:NextDue:start']='2026-11-02T14:00:00Z'
  self.assertNotEqual(first[0]['revision'],queue.ready_task_records([task])[0]['revision'])
 def test_original_producer_event_is_not_duplicated_by_ready_task_supplement(self):
  d=changed(fixture(),'recovery',events=[work(kind='recovery',step='ResolveProjectSources')])
  first=event_probe.probe(d);d['index_page']=saved(first)
  d['ready_task_records']=[dict(id='ready:task',revision='derived',events=[work(kind='recovery',step='ResolveProjectSources',input_digest='derived')])]
  self.assertEqual(len(event_probe.probe(d)['ready']),1)
 def test_stopped_construction_does_not_need_any_discovery_or_write(self):
  r=queue.build({'settings':{'scan_control':{'contract':'scan-control-v1','enabled':False}}})
  self.assertEqual(r['status'],'ScanStopped');self.assertFalse(r['persist_required'])
 def test_one_malformed_ready_task_is_a_scoped_issue_not_a_global_block(self):
  d=self.fixture();d['tasks']=[dict(url='https://app.notion.com/p/'+'c'*32,SourceKey='',Mode='Automatic',State='ReadyToValidate',ResumeStep='ResolveProjectSources',OwnerSkill='eightdegrees-sales-reply',ContentVersion='v1')]
  q=queue.build(d);self.assertEqual(len(q['items']),4);self.assertTrue(any(b['code']=='ReadyTaskMetadataMissing' for b in q['blocks']))
  records=queue.ready_task_records(d['tasks'],q['blocks']);probe=fixture();probe['ready_task_records']=records;probe['ready_task_blocks']=q['blocks']
  self.assertEqual(event_probe.probe(probe)['status'],'ScanDiscoveryRequired')
 def test_queue_merging_preserves_original_unknown_attempt_and_scope(self):
  scan=cycle_fixture();original=scan['items'][0];original.update(unknown_attempt=True,attempt_id='original',scope={'location_id':'loc','contact_id':'customer','channel':'email'})
  q=dict(status='ReadyQueueConstructed',root_id=scan['root_id'],items=[{k:v for k,v in original.items() if k not in {'unknown_attempt','attempt_id','scope'}}])
  scan['queue_plan']=q;result=scan_cycle.advance(scan);self.assertEqual(result['work'],[])
  stored=result['checkpoint']['work_items'][0];self.assertEqual(stored['attempt_id'],'original');self.assertEqual(stored['scope'],original['scope'])
 def test_terminal_source_steps_keep_original_readback_pointer(self):
  d=self.fixture();d['tasks']=[dict(SourceKey='operator:brief',ResumeStep='BuildDailyBrief',ContentVersion='v1',State='Completed',url='notion:original-result')]
  r=queue.build(d);self.assertEqual(len(r['terminal_readbacks']),1)
  self.assertFalse(any(v['step']=='BuildDailyBrief' for v in r['items']))

if __name__=='__main__':unittest.main()
