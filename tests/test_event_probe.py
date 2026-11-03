"""No-input ticks, changed forms, clock events and crash-safe discovery."""

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'plugins/eightdegrees-sales-workflow/scripts'))
import event_probe
import local_checks

ROOT = 'a' * 32
NOW = '2026-11-02T12:00:00Z'


def fixture():
    return {'settings': {'scan_control': {'contract':'scan-control-v1','enabled':True}}, 'root_id': ROOT, 'now': NOW, 'scope_sha256': '1' * 64,
            'required_feeds': sorted(event_probe.REQUIRED),
            'observations': {name: {'mode': 'snapshot', 'complete': True, 'observed_at': NOW,
                                    'records': [], 'next_cursor': 'c1'} for name in event_probe.REQUIRED}}


def work(kind='mail', version='v1', **extra):
    return {'source_key': 'gmail:original1', 'step': 'ReadMessageBody', 'version': version,
            'input_digest': 'original-input-sha', 'kind': kind, 'evidence_ref': 'capture:original1', **extra}


def changed(data, feed='mail', revision='r1', events=None):
    data['observations'][feed]['records'] = [{'id': feed + ':1', 'revision': revision,
                                             'events': [work()] if events is None else events}]
    return data


def saved(result):
    return {'id': ROOT, 'metadata': {'type': 'page'},
            'text': '<content>\n```json\n' + json.dumps(result['candidate_index']) + '\n```\n</content>'}


class EventProbe(unittest.TestCase):
    def test_empty_complete_bootstrap_is_idle_without_executable_effect(self):
        result = event_probe.probe(fixture())
        self.assertEqual(result['status'], 'ScanIdle')
        self.assertEqual(result['ready'], [])
        self.assertTrue(result['persist_required'])
        self.assertFalse(result['external_actions_allowed'])

    def test_seven_quiet_ticks_have_zero_owner_admissions_and_no_index_rewrites(self):
        data = fixture(); data['index_page'] = saved(event_probe.probe(data))
        for minute in range(1, 8):
            data['now'] = '2026-11-02T12:%02d:00Z' % minute
            for observation in data['observations'].values():
                observation['observed_at'] = data['now']
            result = event_probe.probe(data)
            self.assertEqual(result['status'], 'ScanIdle')
            self.assertFalse(result['persist_required'])
            self.assertEqual(result['ready'], [])

    def test_discovery_is_not_completion_and_pending_survives_a_crash_or_source_removal(self):
        data = changed(fixture()); before = copy.deepcopy(data)
        first = event_probe.probe(data)
        self.assertEqual(event_probe.probe(data), first)  # Crash before save.
        data['index_page'] = saved(first)
        data['observations']['mail']['records'] = []
        after = event_probe.probe(data)
        self.assertEqual(after['ready'], first['ready'])  # Crash after cursor save.
        self.assertEqual(before, changed(fixture()))

    def test_new_mail_and_old_thread_reply_are_distinct_inputs(self):
        data = changed(fixture()); first = event_probe.probe(data)
        data['index_page'] = saved(first)
        data['observations']['mail']['records'].append({'id': 'reply2', 'revision': 'r2',
            'events': [work(source_key='gmail:reply2', step='ObserveStop', kind='stop')]})
        result = event_probe.probe(data)
        self.assertEqual(len(result['ready']), 2)
        self.assertEqual(result['ready'][0]['kind'], 'stop')

    def test_same_task_row_but_changed_submitted_action_wakes_processing(self):
        data = changed(fixture(), 'actions', events=[])
        data['index_page'] = saved(event_probe.probe(data))
        changed(data, 'actions', revision='answers-plus-submission-v2',
                events=[work(kind='submission', source_key='action:1', step='ReviewCommunication')])
        result = event_probe.probe(data)
        self.assertEqual(result['status'], 'ScanWorkReady')
        self.assertEqual(result['ready'][0]['step'], 'ReviewCommunication')

    def test_edited_unsubmitted_form_is_not_business_demand(self):
        data = changed(fixture(), 'actions', events=[])
        data['index_page'] = saved(event_probe.probe(data))
        changed(data, 'actions', revision='unsubmitted-edit', events=[])
        result = event_probe.probe(data)
        self.assertEqual(result['status'], 'ScanIdle')
        self.assertTrue(result['persist_required'])

    def test_future_timer_wakes_when_due_with_unchanged_sources(self):
        data = changed(fixture(), 'scheduled', events=[work(kind='timer', step='SendNotificationSms',
                                                         due_at='2026-11-02T12:10:00Z')])
        first = event_probe.probe(data)
        self.assertEqual(first['status'], 'ScanIdle')
        self.assertEqual(first['next_due_at'], '2026-11-02T12:10:00Z')
        data['index_page'] = saved(first); data['now'] = '2026-11-02T12:10:00Z'
        result = event_probe.probe(data)
        self.assertEqual(result['status'], 'ScanWorkReady')
        self.assertEqual(result['ready'][0]['step'], 'SendNotificationSms')

    def test_missing_partial_or_paginated_feed_cannot_claim_idle(self):
        for mode in ('missing', 'partial'):
            data = fixture()
            if mode == 'missing': del data['observations']['actions']
            else: data['observations']['actions'].update(complete=False, next_cursor='page2')
            result = event_probe.probe(data)
            self.assertEqual(result['status'], 'ScanDiscoveryRequired')
            self.assertIn('actions', result['missing_feeds'])
            self.assertFalse(result['coverage_complete'])
            if mode == 'partial': self.assertIsNone(result['candidate_index']['feeds']['actions']['cursor'])

    def test_partial_observation_retains_discovered_event_without_false_coverage(self):
        data = changed(fixture()); data['observations']['mail']['complete'] = False
        result = event_probe.probe(data)
        self.assertEqual(result['status'], 'ScanWorkReady')
        self.assertFalse(result['coverage_complete'])
        self.assertFalse(result['external_actions_allowed'])

    def test_delta_requires_saved_matching_cursor(self):
        for has_index in (False, True):
            data = fixture()
            if has_index: data['index_page'] = saved(event_probe.probe(data))
            data['observations']['mail'].update(mode='delta', from_cursor='wrong')
            result = event_probe.probe(data)
            self.assertEqual(result['status'], 'ScanDiscoveryRequired')
            self.assertIn('mail', result['missing_feeds'])

    def test_valid_delta_and_handled_event_do_not_requeue(self):
        data = changed(fixture()); first = event_probe.probe(data); identity = first['ready'][0]['key']
        data['index_page'] = saved(first)
        data['acknowledgements'] = [{'key': identity, 'state': 'completed', 'receipt_ref': 'notion:owner-result'}]
        data['observations']['mail'].update(mode='delta', from_cursor='c1', next_cursor='c2')
        second = event_probe.probe(data)
        self.assertEqual(second['status'], 'ScanIdle')
        data['index_page'] = saved(second); data['acknowledgements'] = []
        data['observations']['mail']['from_cursor'] = 'c2'
        changed(data, revision='workflow-status-edit', events=[])
        self.assertEqual(event_probe.probe(data)['status'], 'ScanIdle')

    def test_next_daily_occurrence_is_new_input_even_with_same_template_version(self):
        data = changed(fixture(), 'scheduled', events=[work(kind='timer', step='DailyBrief', due_at=NOW)])
        first = event_probe.probe(data); data['index_page'] = saved(first)
        data['acknowledgements'] = [{'key': first['ready'][0]['key'], 'state': 'completed', 'receipt_ref': 'saved:today-brief'}]
        changed(data, 'scheduled', 'tomorrow', [work(kind='timer', step='DailyBrief',
                input_digest='next-business-date', due_at='2026-11-03T12:00:00Z')])
        second = event_probe.probe(data)
        self.assertEqual(second['status'], 'ScanIdle')
        self.assertEqual(second['pending_count'], 1)
        data['index_page'] = saved(second); data['acknowledgements'] = []
        data['now'] = '2026-11-03T12:00:00Z'
        for observed in data['observations'].values(): observed['observed_at'] = data['now']
        self.assertEqual(event_probe.probe(data)['status'], 'ScanWorkReady')

    def test_partial_pagination_resumes_without_losing_prior_page_or_pending_input(self):
        data = changed(fixture()); data['observations']['mail'].update(complete=False, next_cursor='page2')
        first = event_probe.probe(data)
        self.assertEqual(first['candidate_index']['feeds']['mail']['resume_cursor'], 'page2')
        data['index_page'] = saved(first)
        # A caller cannot skip the saved next page and claim an empty complete feed.
        data['observations']['mail'].update(complete=True, records=[], next_cursor='new-head')
        incomplete = event_probe.probe(data)
        self.assertIn('mail', incomplete['missing_feeds'])
        data['observations']['mail'].update(page_cursor='page2')
        second = event_probe.probe(data)
        self.assertTrue(second['coverage_complete'])
        self.assertEqual(second['ready'], first['ready'])
        self.assertEqual(second['candidate_index']['feeds']['mail']['revisions'], {'mail:1': 'r1'})
        self.assertNotIn('resume_cursor', second['candidate_index']['feeds']['mail'])

    def test_waiting_result_needs_wake_pointer_and_new_submission_can_resume(self):
        data = changed(fixture(), 'actions', events=[work(kind='submission')])
        first = event_probe.probe(data); data['index_page'] = saved(first)
        data['acknowledgements'] = [{'key': first['ready'][0]['key'], 'state': 'waiting', 'receipt_ref': 'saved:owner'}]
        with self.assertRaises(ValueError): event_probe.probe(data)
        data['acknowledgements'][0]['wake_ref'] = 'notion:current-action'
        second = event_probe.probe(data); self.assertEqual(second['status'], 'ScanIdle')
        data['index_page'] = saved(second); data['acknowledgements'] = []
        changed(data, 'actions', 'new-submit', [work(kind='submission', input_digest='new-answers')])
        self.assertEqual(event_probe.probe(data)['status'], 'ScanWorkReady')

    def test_wrong_root_scope_or_stale_empty_capture_cannot_suppress_work(self):
        data = fixture(); first = event_probe.probe(data)
        data['index_page'] = saved(first); data['root_id'] = 'b' * 32
        with self.assertRaises(ValueError): event_probe.probe(data)
        data['root_id'] = ROOT; data['scope_sha256'] = '2' * 64
        self.assertEqual(event_probe.probe(data)['status'], 'ScanDiscoveryRequired')
        data = fixture(); data['now'] = '2026-11-02T14:00:00Z'
        with self.assertRaises(ValueError): event_probe.probe(data)

    def test_malformed_or_unregistered_inputs_fail_batch_without_calls(self):
        for corrupt in ('timer', 'feed', 'receipt'):
            data = fixture()
            if corrupt == 'timer': changed(data, 'scheduled', events=[work(kind='timer')])
            elif corrupt == 'feed': data['observations']['undeclared'] = data['observations']['mail']
            else: data['acknowledgements'] = [{'key': 'unknown', 'state': 'completed', 'receipt_ref': 'x'}]
            result = local_checks.run({'checks': [{'name': 'probe', 'operation': 'scan.probe', 'input': data}]}, {})
            self.assertEqual(result['status'], 'NeedsCorrection')
            self.assertNotIn('call', result['checks'][0]['result'])

    def test_batch_distinguishes_idle_from_partial_without_granting_send(self):
        for missing in (False, True):
            data = fixture()
            if missing: del data['observations']['mail']
            result = local_checks.run({'checks': [{'name': 'probe', 'operation': 'scan.probe', 'input': data}]}, {})
            self.assertEqual(result['status'], 'LocalChecksPassed')
            self.assertEqual(result['checks'][0]['result']['status'], 'ScanDiscoveryRequired' if missing else 'ScanIdle')
            self.assertFalse(result['checks'][0]['result']['external_actions_allowed'])


if __name__ == '__main__': unittest.main()
