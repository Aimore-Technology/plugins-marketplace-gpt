"""The actual 0.1.35 init failed on an escaped SourceKey readback."""

import copy
import json
import unittest

from test_execution_preflight import request, capture
from test_scan_regressions_035 import run_call
import execution_preflight
import runtime_records
import notion_mutation


class ReadbackIdentity(unittest.TestCase):
    def test_original_colon_underscore_projection_matches_without_changing_capture(self):
        prepared = execution_preflight.prepare(request())
        original = capture(prepared)
        props = prepared['execution_plan']['run_properties']
        escaped = props['SourceKey'].replace(':', '\\:')
        original['text'] = original['text'].replace(json.dumps(props['SourceKey']), json.dumps(escaped), 1)
        before = copy.deepcopy(original)
        self.assertEqual(execution_preflight.ready({'prepared': prepared, 'saved_plan': original})['status'], 'ExecutionPlanReady')
        self.assertEqual(original, before)
        self.assertTrue(runtime_records.matches_readback({'SourceKey': 'scan\\:turn\\_one'}, {'SourceKey': 'scan:turn_one'}))

    def test_real_identity_changes_and_literal_backslashes_are_not_normalized_away(self):
        for value in ['scan\\:another', 'scan\\\\:turn', '[scan:turn](https://example.com)', ' scan:turn', 'scan\\q:turn']:
            self.assertFalse(runtime_records.matches_readback({'SourceKey': value}, {'SourceKey': 'scan:turn'}))

    def test_saved_scan_projection_can_close_but_escaped_write_cannot_be_emitted(self):
        data = run_call('scan')
        props = data['call']['args']['pages'][0]['properties']
        observed = {**props, 'SourceKey': props['SourceKey'].replace(':', '\\:')}
        runtime_records.validate(observed, creating=False)
        with self.assertRaises(ValueError): runtime_records.validate(observed, creating=True)
        data['call']['args']['pages'][0]['properties'] = observed
        with self.assertRaises(ValueError): notion_mutation.prepare(data)

    def test_wrong_version_or_scan_predecessor_still_fails(self):
        props = runtime_records.prepare({'owner_skill': 'eightdegrees-email-scanning', 'invocation_id': 'turn', 'operation': 'scan'})['properties']
        self.assertFalse(runtime_records.matches_readback(props | {'SourceKey': 'scan\\:old-turn'}, props))
        self.assertFalse(runtime_records.matches_readback(props | {'SkillVersion': '0.1.35'}, props))


if __name__ == '__main__': unittest.main()
