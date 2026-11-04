"""One artifact saves originals/results; unchanged consent rows need no fetch."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_reply_transport import SCRIPTS
from test_event_probe import fixture, saved
import capture_bundle
import consent_review
import event_probe
import local_checks


def plan():
    return {'captures': {'ack': {'id': 'actual-original-id'}},
            'checks': [{'name': 'write', 'operation': 'write.confirm',
                        'input': {'service':'notion', 'response':{'$capture':'ack'},
                                  'expected_id':'actual-original-id'}}]}


def row(number=1, consent=False):
    return {'url':'https://app.notion.com/p/'+format(number,'032x'),
            'State':'WaitingForOperator', 'ActionFormVersion':'email-review-v4',
            'Mode':'Automatic', 'OwnerSkill':'eightdegrees-sales-reply',
            'ResumeStep':'SendApprovedReply', 'ContentVersion':'reply-v1',
            'SourceKey':'sender@example.com:inbound:m'+str(number),
            'Consent':consent, 'ReviewText':'To: customer@example.com\nFull exact reply '+str(number)}


def observed_index(records, pending=None):
    d=fixture();base=event_probe.probe(d)
    base['candidate_index']['feeds']['actions']['revisions']={r['id']:r['revision'] for r in records}
    if pending:base['candidate_index']['pending']=pending
    return saved(base)


class PhaseArtifactTests(unittest.TestCase):
    def run_cli(self,p,output,other_args=()):
        return subprocess.run([sys.executable,str(SCRIPTS/'local_checks.py'),'--input','-',
                               '--output',str(output),*other_args],input=json.dumps(p),
                              capture_output=True,text=True)

    def test_single_output_artifact_keeps_originals_and_results_without_save_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'phase.json';r=self.run_cli(plan(),output)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            summary=json.loads(r.stdout);artifact=json.loads(output.read_text())
            self.assertTrue(summary['original_inputs_saved'])
            self.assertFalse(summary['separate_capture_save_required'])
            self.assertEqual(artifact['captures'],plan()['captures'])
            self.assertEqual(artifact['checks'][0]['result']['status'],'APIWriteConfirmed')
            self.assertNotIn('captures',summary)

    def test_next_phase_references_existing_artifact_and_merges_only_new_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            first=Path(tmp)/'one.json';second=Path(tmp)/'two.json'
            self.assertEqual(self.run_cli(plan(),first).returncode,0)
            p=plan();p['captures']={'new':{'id':'new-original'}}
            r=self.run_cli(p,second,('--captures',str(first)))
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual(set(json.loads(second.read_text())['captures']),{'ack','new'})

    def test_identical_phase_result_causes_no_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'phase.json';self.run_cli(plan(),p);stamp=p.stat().st_mtime_ns
            r=self.run_cli(plan(),p)
            self.assertFalse(json.loads(r.stdout)['output_written'])
            self.assertEqual(p.stat().st_mtime_ns,stamp)

    def test_conflicting_input_alias_is_not_silently_replaced(self):
        with self.assertRaises(ValueError):
            capture_bundle.merge_originals({'x':{'id':'original'}},{'x':{'id':'different'}})

    def test_failed_check_still_saves_exact_original_errors_without_executable_call(self):
        p=plan();p['captures']['ack']={'isError':True,'content':[{'type':'text','text':'Original provider refusal'}]}
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'failed.json';r=self.run_cli(p,output)
            self.assertEqual(r.returncode,2)
            artifact=json.loads(output.read_text())
            self.assertEqual(artifact['captures'],p['captures'])
            self.assertNotIn('call',artifact['checks'][0]['result'])

    def test_atomic_failure_preserves_previous_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'phase.json';capture_bundle.save_private(output,{'original':True})
            with patch.object(capture_bundle.os,'replace',side_effect=OSError('disk unavailable')):
                with self.assertRaises(OSError):capture_bundle.save_private(output,{'new':True})
            self.assertEqual(json.loads(output.read_text()),{'original':True})


class ConsentReadPlanTests(unittest.TestCase):
    def inputs(self,rows):
        return {'rows':rows,'rows_complete':True,'root_id':'a'*32,'now':'2026-11-04T12:00:00Z'}

    def test_one_hundred_unchanged_waits_need_zero_page_fetches(self):
        d=self.inputs([row(i) for i in range(1,101)])
        first=consent_review.read_plan(d);d['index_page']=observed_index(first['row_records'])
        r=consent_review.read_plan(d)
        self.assertEqual(r['page_fetches_required'],0)
        self.assertEqual(r['unchanged_or_unsubmitted_skipped'],100)
        self.assertFalse(r['external_actions_allowed'])

    def test_two_changed_consents_fetch_only_those_two_original_tasks(self):
        d=self.inputs([row(i) for i in range(1,101)])
        first=consent_review.read_plan(d);d['index_page']=observed_index(first['row_records'])
        d['rows'][2]['Consent']=True;d['rows'][65]['Consent']='__YES__'
        r=consent_review.read_plan(d)
        self.assertEqual(r['task_page_urls'],sorted([d['rows'][2]['url'],d['rows'][65]['url']]))
        self.assertEqual(r['page_fetches_required'],2)

    def test_pending_handoff_remains_read_demand_without_row_edits(self):
        d=self.inputs([row(1,True)]);first=consent_review.read_plan(d)
        pending={'actual-key':{'source_key':d['rows'][0]['SourceKey'],'step':'SendApprovedReply',
                              'version':'reply-v1','kind':'recovery'}}
        d['index_page']=observed_index(first['row_records'],pending)
        self.assertEqual(consent_review.read_plan(d)['task_page_urls'],[d['rows'][0]['url']])

    def test_incomplete_query_refuses_and_missing_projection_falls_back_to_original(self):
        d=self.inputs([row()]);d['rows_complete']=False
        with self.assertRaises(ValueError):consent_review.read_plan(d)
        d['rows_complete']=True;del d['rows'][0]['ReviewText']
        r=consent_review.read_plan(d)
        self.assertEqual(r['fallback_task_urls'],[d['rows'][0]['url']])

    def test_withdrawal_and_text_edits_fetch_current_task_but_log_timestamp_does_not(self):
        d=self.inputs([row(1,True)]);first=consent_review.read_plan(d)
        d['index_page']=observed_index(first['row_records']);d['rows'][0]['ObservedAt']='later'
        self.assertEqual(consent_review.read_plan(d)['task_page_urls'],[])
        d['rows'][0]['Consent']=False
        self.assertEqual(consent_review.read_plan(d)['page_fetches_required'],1)
        d['rows'][0]['Consent']=True;d['rows'][0]['ReviewText']='User edited reply'
        self.assertEqual(consent_review.read_plan(d)['page_fetches_required'],1)

    def test_closed_rows_and_other_installations_are_not_reused(self):
        d=self.inputs([row()]);d['rows'][0]['State']='Completed'
        self.assertEqual(consent_review.read_plan(d)['task_page_urls'],[])
        d['index_page']=observed_index([]);d['root_id']='b'*32
        with self.assertRaises(ValueError):consent_review.read_plan(d)

    def test_normal_scan_watches_reuses_rows_instead_of_requesting_all_consent_pages(self):
        import discovery_watch
        from test_pre_action_order import page
        rows=[row(i) for i in range(1,101)]
        first=consent_review.read_plan(self.inputs(rows))
        config={'settings_schema_version':2,'scan_control':{'contract':'scan-control-v1','enabled':True},
                'customer_setup':{'notion_root_id':'a'*32},'project_sources':{},'sales_replies':{}}
        settings=page('```json\n'+json.dumps(config)+'\n```')
        d={'settings_page':settings,'tasks_complete':True,'tasks':rows,
           'index_page':observed_index(first['row_records']),'now':'2026-11-04T12:00:00Z'}
        before=copy.deepcopy(d);r=discovery_watch.plan(d)
        self.assertEqual(r['consent_task_urls'],[])
        self.assertEqual(r['action_page_urls'],[])
        self.assertEqual(len(r['consent_row_records']),100)
        self.assertEqual(d,before)
