"""Stopped entry performs no discovery/admission or state mutation."""
import copy
import unittest
from unittest.mock import patch

import scan_control
import event_probe
import scan_cycle
import discovery_watch
import dispatch_admission
import local_checks
from test_event_probe import fixture, changed, saved
from test_unattended import cycle_fixture
from test_pre_action_order import dispatch, ready
from test_email_presentation import page, block


def settings(enabled=False):
    return {'scan_control': {'contract': 'scan-control-v1', 'enabled': enabled}}


class ScanControlTests(unittest.TestCase):
    def test_stopped_probe_exits_before_required_feeds_clock_or_source_normalization(self):
        with patch.object(event_probe, 'page_id', side_effect=AssertionError('Discovery ran')):
            result = event_probe.probe({'settings': settings()})
        self.assertEqual(result['status'], 'ScanStopped')
        self.assertFalse(result['persist_required'])
        self.assertNotIn('candidate_index', result)

    def test_stopped_queue_exits_before_items_clock_or_checkpoint_processing(self):
        with patch.object(scan_cycle, 'timestamp', side_effect=AssertionError('Queue ran')):
            result = scan_cycle.advance({'settings': settings()})
        self.assertEqual(result['status'], 'ScanStopped')
        self.assertEqual(result['work'], [])

    def test_stopped_watch_plan_requires_no_task_listing(self):
        data = {'settings_page': page('a' * 32, block({'settings_schema_version': 2, **settings()}), {})}
        self.assertEqual(discovery_watch.plan(data)['status'], 'ScanStopped')

    def test_disabled_entry_does_not_consume_pending_events_or_change_input(self):
        data = changed(fixture())
        data['index_page'] = saved(event_probe.probe(data))
        data['settings'] = settings(False)
        before = copy.deepcopy(data)
        result = event_probe.probe(data)
        self.assertEqual(result['status'], 'ScanStopped')
        self.assertFalse(result['persist_required'])
        self.assertEqual(data, before)

    def test_start_resumes_pending_event_from_original_index(self):
        data = changed(fixture())
        first = event_probe.probe(data)
        data['index_page'] = saved(first)
        data['settings'] = settings(False)
        self.assertEqual(event_probe.probe(data)['status'], 'ScanStopped')
        data['settings'] = settings(True)
        resumed = event_probe.probe(data)
        self.assertEqual(resumed['status'], 'ScanWorkReady')
        self.assertEqual(resumed['ready'], first['ready'])

    def test_stop_after_dispatch_admission_blocks_release(self):
        data = ready(dispatch())
        data['current_scan']['settings'] = settings(False)
        with self.assertRaises(ValueError):
            dispatch_admission.release(data)

    def test_stop_blocks_preparing_dispatch_without_touching_approved_payload(self):
        data = dispatch()
        data['scan']['settings'] = settings(False)
        before = copy.deepcopy(data)
        with self.assertRaises(ValueError):
            dispatch_admission.prepare(data)
        self.assertEqual(data, before)

    def test_missing_or_unreadable_switch_never_assumes_enabled(self):
        for data in ({}, {'settings': None}, {'settings': {'scan_control': None}}):
            result = scan_control.gate(data)
            self.assertEqual(result['status'], 'ScanControlUnknown')
            self.assertFalse(result['external_actions_allowed'])

    def test_explicit_malformed_switch_never_falls_back_to_running_legacy(self):
        legacy = {'enabled': True, 'approved_work_enabled': True, 'state': 'Running', 'desired_state': 'Running'}
        for value in ('false', 1, None):
            data = {'settings': {'scan_control': {'contract': 'scan-control-v1', 'enabled': value},
                                 'scheduling': legacy}}
            self.assertEqual(scan_control.gate(data)['status'], 'ScanControlUnknown')

    def test_fresh_unconfigured_installation_is_stopped(self):
        self.assertEqual(scan_control.gate({'settings': {}})['status'], 'ScanStopped')

    def test_explicit_new_switch_supersedes_legacy_scheduler_state(self):
        data = settings(True) | {'scheduling': {'enabled': False, 'state': 'Stopped', 'runtime': None}}
        self.assertEqual(scan_control.gate({'settings': data})['status'], 'ScanEnabled')
        data = settings(False) | {'scheduling': {'enabled': True, 'approved_work_enabled': True,
                                               'state': 'Running', 'desired_state': 'Running'}}
        self.assertEqual(scan_control.gate({'settings': data})['status'], 'ScanStopped')

    def test_stop_start_preserves_due_time_unknown_attempt_and_budget(self):
        data = cycle_fixture()
        data['items'][0].update(unknown_attempt=True, attempt_id='original-unknown', due_at=data['now'])
        before = copy.deepcopy(data)
        data['settings'] = settings(False)
        self.assertEqual(scan_cycle.advance(data)['status'], 'ScanStopped')
        data['settings'] = settings(True)
        self.assertEqual(scan_cycle.advance(data)['work'], [])
        self.assertEqual(data['items'], before['items'])
        self.assertEqual(data['started_at'], before['started_at'])

    def test_only_switch_patch_is_returned_even_with_pending_native_mutation(self):
        current = settings(True) | {'scheduling': {'schedule_ids': ['original-native-job'],
                                                  'pending_attempt': {'status': 'Unknown'}},
                                    'approved_payload': 'unchanged', 'cursor': 'original-cursor'}
        result = scan_control.plan({'operation': 'stop', 'settings': current})
        self.assertEqual(set(result['patch']), {'scan_control'})
        self.assertFalse(result['native_task_mutation_allowed'])
        self.assertEqual(current['cursor'], 'original-cursor')

    def test_control_readback_cannot_claim_success_from_an_unsaved_plan(self):
        data = {'operation': 'start', 'settings': settings(False), 'saved_settings': settings(False)}
        self.assertEqual(scan_control.verify(data)['status'], 'NeedsCorrection')

    def test_local_batch_stopped_result_has_no_executable_call_or_plan(self):
        result = local_checks.run({'checks': [{'name': 'entry', 'operation': 'scan.entry',
                                               'input': {'settings': settings(False)}}]}, {})
        self.assertEqual(result['status'], 'LocalChecksPassed')
        entry = result['checks'][0]['result']
        self.assertEqual(entry['status'], 'ScanStopped')
        self.assertNotIn('call', entry)
        self.assertFalse(entry['persist_required'])

    def test_malformed_legacy_settings_is_unknown_not_an_exception_or_enabled(self):
        result = scan_control.gate({'settings': {'scheduling': 'invalid'}})
        self.assertEqual(result['status'], 'ScanControlUnknown')
        self.assertFalse(result['persist_required'])

    def test_default_package_does_not_enable_scanning(self):
        import json
        from pathlib import Path
        default = json.loads((Path(__file__).resolve().parents[1] /
           'plugins/eightdegrees-sales-workflow/references/pilot-defaults.json').read_text())
        self.assertEqual(scan_control.gate({'settings': default})['status'], 'ScanStopped')


if __name__ == '__main__':
    unittest.main()
