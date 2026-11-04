"""Batch actual phase inputs once; unchanged captures cause no file writes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_reply_transport import SCRIPTS
import capture_bundle
import local_checks


class CaptureBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'phase/captures.json'
        self.data = {'bundle_path': str(self.path), 'root_id': 'a'*32,
                     'cycle_key': 'current-cycle', 'observed_at': '2026-11-04T10:00:00Z',
                     'captures': {'task:rev1': {'content': [{'type': 'text', 'text': 'Original task'}],
                                               'structuredContent': {'id': 'task-original'}}}}

    def test_many_originals_are_saved_in_one_atomic_write(self):
        for i in range(25):
            self.data['captures']['action:'+str(i)] = {'content': [{'type':'text','text':'Original '+str(i)}]}
        with patch.object(capture_bundle.os, 'replace', wraps=capture_bundle.os.replace) as replace:
            r = capture_bundle.commit(self.data)
        self.assertEqual(replace.call_count, 1)
        self.assertEqual((r['captures_added'], r['write_count']), (26, 1))
        self.assertEqual(capture_bundle.unpack(json.loads(self.path.read_text())), self.data['captures'])
        self.assertNotIn('Original task', json.dumps(r))

    def test_repeated_same_capture_leaves_file_and_mtime_unchanged(self):
        capture_bundle.commit(self.data)
        before = self.path.read_bytes(); stamp = self.path.stat().st_mtime_ns
        self.data['observed_at'] = '2026-11-04T10:02:00Z'
        with patch.object(capture_bundle.os, 'replace') as replace:
            r = capture_bundle.commit(self.data)
        self.assertEqual(r['status'], 'CaptureBundleUnchanged')
        self.assertEqual(r['write_count'], 0); replace.assert_not_called()
        self.assertEqual((self.path.read_bytes(),self.path.stat().st_mtime_ns), (before,stamp))

    def test_new_phase_appends_once_without_rewriting_original_alias(self):
        capture_bundle.commit(self.data)
        self.data['captures'] = {'task:rev2': {'content':[{'type':'text','text':'Actual later revision'}]}}
        r = capture_bundle.commit(self.data)
        self.assertEqual((r['captures_added'],r['flush_count']), (1,2))
        self.assertEqual(set(capture_bundle.unpack(json.loads(self.path.read_text()))), {'task:rev1','task:rev2'})

    def test_changed_alias_fails_before_any_mutation(self):
        capture_bundle.commit(self.data); before = self.path.read_bytes()
        self.data['captures']['task:rev1'] = {'id': 'different original'}
        with self.assertRaisesRegex(ValueError, 'alias changed'): capture_bundle.commit(self.data)
        self.assertEqual(self.path.read_bytes(), before)

    def test_root_and_cycle_boundaries_do_not_become_cross_run_cache(self):
        capture_bundle.commit(self.data); before = self.path.read_bytes()
        for k,v in [('root_id','b'*32),('cycle_key','another-cycle')]:
            d = copy.deepcopy(self.data);d[k]=v
            with self.assertRaises(ValueError): capture_bundle.commit(d)
        self.assertEqual(self.path.read_bytes(),before)

    def test_wrapped_failure_and_exception_are_preserved_and_not_success_coverage(self):
        original = {'isError':True, 'structuredContent':{'error':'INVALID_ARGUMENT'},
                    'content':[{'type':'text','text':'{"error":{"code":"RATE_LIMIT_EXCEEDED"}}'}]}
        thrown = {'exception':{'name':'Error','message':'Original connection failure'}}
        self.data['captures'] = {'quota':original,'exception':thrown}
        r = capture_bundle.commit(self.data)
        self.assertEqual(set(r['failures']), {'quota','exception'})
        self.assertEqual(r['failures']['quota']['original'], original)
        self.assertFalse(r['external_actions_allowed'])
        self.assertEqual(capture_bundle.unpack(json.loads(self.path.read_text())), self.data['captures'])

    def test_failed_atomic_replace_preserves_previous_checkpoint(self):
        capture_bundle.commit(self.data); before = self.path.read_bytes()
        self.data['captures']['next'] = {'id':'new-original'}
        with patch.object(capture_bundle.os,'replace',side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError): capture_bundle.commit(self.data)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(list(self.path.parent.glob('.captures.json.*')),[])

    def test_plugin_and_symlink_destinations_are_refused(self):
        d = copy.deepcopy(self.data); d['bundle_path'] = str(SCRIPTS/'invalid-capture.json')
        with self.assertRaises(ValueError): capture_bundle.commit(d)
        link = Path(self.temp.name)/'link'; link.symlink_to(Path(self.temp.name), target_is_directory=True)
        d['bundle_path'] = str(link/'other.json')
        with self.assertRaises(ValueError): capture_bundle.commit(d)

    def test_local_cli_checks_inline_captures_without_preliminary_file_save(self):
        plan = {'captures':{'write':{'id':'saved-original'}},
                'checks':[{'name':'write','operation':'write.confirm',
                           'input':{'service':'notion','response':{'$capture':'write'},'expected_id':'saved-original'}}]}
        r = subprocess.run([sys.executable,str(SCRIPTS/'local_checks.py'),'--input','-'],
                           input=json.dumps(plan),text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'],'LocalChecksPassed')
        self.assertFalse(self.path.exists())

    def test_one_local_batch_can_commit_inputs_and_check_original_ack(self):
        captures = {'write':{'id':'saved-original'}}
        d = {**self.data,'captures':{'write':{'$capture':'write'}}}
        plan = {'checks':[{'name':'capture','operation':'capture.commit','input':d},
                          {'name':'ack','operation':'write.confirm','input':{'service':'notion',
                           'response':{'$capture':'write'},'expected_id':'saved-original'}}]}
        r = local_checks.run(plan,captures)
        self.assertEqual(r['status'],'LocalChecksPassed')
        self.assertEqual(r['checks'][0]['result']['write_count'],1)

    def test_existing_bundle_and_legacy_capture_dictionary_both_load(self):
        capture_bundle.commit(self.data)
        self.assertEqual(capture_bundle.unpack(json.loads(self.path.read_text())),self.data['captures'])
        self.assertIs(capture_bundle.unpack(self.data['captures']),self.data['captures'])
        with self.assertRaises(ValueError): capture_bundle.unpack({'record_type':'capture-bundle-v1'})

    def test_output_cannot_overwrite_capture_bundle_created_by_inline_plan(self):
        plan={'captures':{},'checks':[{'name':'capture','operation':'capture.commit','input':self.data}]}
        r=subprocess.run([sys.executable,str(SCRIPTS/'local_checks.py'),'--input','-',
                          '--output',str(self.path)],input=json.dumps(plan),text=True,capture_output=True)
        self.assertEqual(r.returncode,2)
        self.assertEqual(json.loads(self.path.read_text())['record_type'],'capture-bundle-v1')
