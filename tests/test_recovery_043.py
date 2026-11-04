"""Regression: unchanged backlog, truthful baseline, fresh rules and independent progress."""
import copy
import unittest
import backlog_recovery
import cycle_metrics
import current_rules
import event_probe
import scan_control
import schedule_checks
from test_event_probe import fixture, changed, saved, work
from test_email_presentation import page
from test_flow_regressions_038 import scoped_cycle, scope
import scan_cycle

class Recovery043(unittest.TestCase):
    def test_scope_change_preserves_backlog_without_new_mail(self):
        d=changed(fixture());first=event_probe.probe(d);d['index_page']=saved(first)
        d['scope_sha256']='2'*64;d['observations']['mail']['records']=[]
        result=event_probe.probe(d)
        self.assertEqual(result['ready'],first['ready'])
        self.assertTrue(result['coverage_complete'])
        self.assertEqual(result['baseline_state'],'Complete')

    def test_missing_feed_does_not_starve_original_backlog(self):
        d=changed(fixture());first=event_probe.probe(d);d['index_page']=saved(first)
        d['observations']['mail']['records']=[];del d['observations']['actions']
        r=event_probe.probe(d)
        self.assertEqual(r['status'],'ScanWorkReady')
        self.assertEqual(r['ready'],first['ready'])
        self.assertEqual(r['recovery_actions'][0]['feed'],'actions')
        self.assertFalse(r['coverage_complete'])
        self.assertEqual(r['baseline_state'],'NeedsBaseline')
        d['index_page']=saved(r);d['observations']['actions']=fixture()['observations']['actions']
        r=event_probe.probe(d);self.assertEqual(r['baseline_state'],'Complete')
        self.assertEqual(r['ready'],first['ready'])

    def test_source_persisted_without_handoff_recovers_original_no_recreation(self):
        root='a'*32
        source=page('b'*32,'Original body',{'Account':'user@example.com','MessageId':'m1',
              'Direction':'Inbound','ContentVersion':'source-v1'})
        source['text']='<ancestor-1-page url="https://app.notion.com/p/'+root+'">Aimore</ancestor-1-page>\n'+source['text']
        d={'root_id':root,'sources_complete':True,'tasks_complete':True,
           'source_pages':[source],'tasks':[],
           'events':[work(source_key='user@example.com:inbound:m1'),work(source_key='user@example.com:inbound:m2')]}
        before=copy.deepcopy(d);r=backlog_recovery.plan(d)
        self.assertEqual([w['step'] for w in r['work']],['RecoverSourceHandoff','ReadMessageBody'])
        self.assertFalse(r['work'][0]['create_source']);self.assertTrue(r['work'][1]['create_source'])
        self.assertEqual(d,before)
        for item in r['work']:self.assertTrue(scan_cycle.key(item))
        d['tasks']=[{'SourceKey':'user@example.com\\:inbound\\:m1','State':'WaitingForOperator',
                     'ResumeStep':'ReviewCommunication','ContentVersion':'v1','url':'notion:existing'}]
        r=backlog_recovery.plan(d);self.assertEqual(len(r['waiting']),1)
        self.assertEqual(len(r['work']),1)
        d['tasks'][0]['AcceptedSubmission']='actual-current-submission'
        self.assertEqual(backlog_recovery.plan(d)['work'][0]['action'],'ResumeOriginalTask')
        d['tasks'][0]['State']='Completed'
        self.assertEqual(len(backlog_recovery.plan(d)['terminal_handoffs']),1)
        d['sources_complete']=False
        with self.assertRaises(ValueError):backlog_recovery.plan(d)

    def test_notion_email_link_projection_reuses_waiting_task_and_rejects_conflict(self):
        root='a'*32
        source=page('b'*32,'Saved original',{'Account':'user@example.com','MessageId':'m1','Direction':'Inbound','ContentVersion':'source-v1'})
        source['text']='<ancestor-1-page url="https://app.notion.com/p/'+root+'">Aimore</ancestor-1-page>\n'+source['text']
        row={'SourceKey':'[user@example.com](mailto:user%40example.com)\\:inbound\\:m1',
             'SourceURL':'https://app.notion.com/p/'+'b'*32,'State':'WaitingForOperator',
             'ResumeStep':'VerifyCustomer','ContentVersion':'match-v1','url':'notion:original-task'}
        d={'root_id':root,'sources_complete':True,'tasks_complete':True,'source_pages':[source],
           'tasks':[row],'events':[work(source_key='user@example.com:inbound:m1')]}
        r=backlog_recovery.plan(d);self.assertEqual(r['work'],[]);self.assertEqual(len(r['waiting']),1)
        row['SourceKey']='[different@example.com](mailto:user%40example.com):inbound:m1'
        r=backlog_recovery.plan(d);self.assertEqual(r['work'],[]);self.assertEqual(len(r['blocks']),1)
        row['SourceKey']='[user@example.com](https://untrusted.example):inbound:m1'
        r=backlog_recovery.plan(d);self.assertEqual(r['work'],[]);self.assertEqual(len(r['blocks']),1)
        # A contradictory task must not suppress another original customer.
        d['events'].append(work(source_key='other@example.com:inbound:m2'))
        r=backlog_recovery.plan(d);self.assertEqual(len(r['work']),1);self.assertTrue(r['work'][0]['create_source'])

    def test_existing_completed_read_cannot_suppress_distinct_handoff(self):
        d=scoped_cycle();source='user@example.com:inbound:m1'
        d['items']=[dict(source_key=source,step='ReadMessageBody',version='v1',input_digest='mail')]
        first=scan_cycle.advance(d);key=scan_cycle.key(d['items'][0])
        d['results']=[dict(key=key,state='completed',receipt_ref='notion:original-source')]
        d['items'].append(dict(d['items'][0],step='RecoverSourceHandoff'))
        result=scan_cycle.advance(d)
        self.assertEqual(result['work'][0]['step'],'RecoverSourceHandoff')

    def test_unknown_sms_does_not_block_same_customer_other_channel(self):
        d=scoped_cycle();d['items'][0]['scope']=scope('A',channel='sms')
        d['items'][1].update(step='SendApprovedReply',scope=scope('A',channel='email'))
        self.assertEqual(scan_cycle.advance(d)['work'][0]['source_key'],'customer-B')
        d['items'][1]['scope']['channel']='sms'
        self.assertEqual(scan_cycle.advance(d)['work'],[])

    def test_explicit_start_registers_existing_not_native_management_gate(self):
        old={'scan_control':{'contract':'scan-control-v1','enabled':False},
             'scheduling':{'schedule_ids':['existing']},'attempt':'original-unknown'}
        observation=dict(task_id='existing',status='ACTIVE',rrule='INTERVAL=30',
                         observed_at='2026-11-03T22:00:00Z',evidence_ref='actual:task-config')
        d=dict(operation='start',settings=old,native_observation=observation)
        result=scan_control.plan(d);actual=copy.deepcopy(old)|result['patch']
        self.assertEqual(actual['scan_control']['native_registration'],observation)
        self.assertEqual(scan_control.verify(d|{'saved_settings':actual})['status'],'ScanningEnabled')
        actual['scan_control']['native_configuration_verified']=False
        self.assertEqual(scan_control.gate({'settings':actual})['status'],'ScanEnabled')
        actual['scan_control']['enabled']=False
        self.assertEqual(scan_control.gate({'settings':actual})['status'],'ScanStopped')
        observation['task_id']='replacement'
        with self.assertRaises(ValueError):scan_control.plan(d)

    def test_current_loader_ignores_history_and_management_fields(self):
        r=current_rules.load({'rule_version':'old','native_runtime_verified':False})
        self.assertEqual(r['status'],'CurrentScheduledRulesLoaded')
        self.assertEqual(r['owner'],'eightdegrees-email-scanning')
        self.assertEqual(len(r['rule_sha256']),64)
        self.assertIn('scripts/event_probe.py',r['rule_files'])
        self.assertEqual(current_rules.load()['rule_sha256'],r['rule_sha256'])

    def test_metrics_require_progress_or_evidenced_block_and_deduplicate(self):
        d=dict(started_at='2026-11-03T22:00:00Z',ended_at='2026-11-03T22:01:12Z',
               discovery={'ready_count':2,'pending_count':2,'coverage_complete':False},
               guard={'status':'EligibleForScheduledCycle'},rule_version='current',rule_sha256='1'*64)
        with self.assertRaises(ValueError):cycle_metrics.summarize(d)
        d['blocks']=[dict(code='MissingSource',reason='Actual connector unavailable',
                          resume_step='ReadProject',evidence_ref='capture:failed',source_key='mail:1')]
        r=cycle_metrics.summarize(d);self.assertFalse(r['record']['business_progress'])
        self.assertFalse(r['record']['timer_trigger_verified']);self.assertEqual(r['record']['elapsed_seconds'],72)
        d['previous_notice_keys']=[r['notify'][0]['key']];d['blocks'][0]['reason']='Same fault later'
        self.assertEqual(cycle_metrics.summarize(d)['notify'],[])
        d['steps']=[dict(state='waiting',receipt_ref='notion:actual-review')]
        d['waits']=['notion:actual-review'];d['timer_evidence']=dict(task_id='existing',run_ref='actual:wake',observed_at=d['started_at'])
        r=cycle_metrics.summarize(d)['record'];self.assertTrue(r['business_progress']);self.assertTrue(r['timer_trigger_verified'])
        self.assertEqual(r['waiting_review_count'],1)
        d['steps']=[];d['blocks']=[];d['waits']=[]
        d['discovery']={'status':'ScanIdle','coverage_complete':True,'ready_count':0}
        self.assertEqual(cycle_metrics.summarize(d)['record']['state'],'ScanIdle')
        d['discovery']['coverage_complete']=False
        self.assertEqual(cycle_metrics.summarize(d)['record']['state'],'DiscoveryIncomplete')

if __name__=='__main__':unittest.main()
