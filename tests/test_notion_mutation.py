"""Pre-call refusal regressions for Q19-01/Q19-02; no connector writes."""

import copy
import json
import subprocess
import sys
import unittest

from test_notion_checks import source_schema, page, PARENT, REPORT, SCRIPTS
import notion_mutation as MUTATION


def create():
    return {"call": {"tool": "mcp__codex_apps__notion_notion_create_pages", "args": {
        "parent": {"data_source_id": PARENT}, "pages": [
            {"properties": {"Status": "Saved"}, "content": "## Current status\n\nWaiting."}]}},
        "data_source": source_schema()}


def update():
    target = page("## Current status\n\nWaiting.")
    target["text"] = '<parent-data-source url="collection://' + PARENT + '"/>\n' + target["text"]
    return {"call": {"tool": "mcp__codex_apps__notion_notion_update_page", "args": {
        "page_id": REPORT, "command": "update_properties", "properties": {"ExternalIds": "message: one"}}},
        "target": target, "data_source": source_schema()}


class NotionMutationTests(unittest.TestCase):
    def test_initial_page_cannot_publish_a_bad_link_even_with_valid_properties(self):
        data = create(); data['call']['args']['pages'][0]['content'] = '[local](/tmp/reply.html)'
        result = MUTATION.prepare(data)
        self.assertEqual(result['status'], 'NeedsCorrection')
        self.assertNotIn('call', result)

    def test_batch_returns_no_partial_arguments_when_second_page_fails(self):
        data = create(); data['call']['args']['pages'].append({'properties': {'Status': 'Invented'}, 'content': 'Valid text'})
        result = MUTATION.prepare(data)
        self.assertEqual(result['status'], 'NeedsCorrection'); self.assertNotIn('call', result)

    def test_exact_external_ids_rejection_is_before_result_or_log_write(self):
        data = update(); data['call']['args']['properties']['ExternalIds'] = '{"message":"one"}'
        self.assertEqual(MUTATION.prepare(data)['status'], 'NeedsCorrection')
        self.assertEqual(MUTATION.prepare(update())['status'], 'NotionMutationPrepared')

    def test_missing_or_wrong_original_schema_blocks_metadata_only_write(self):
        for change in (lambda d: d.pop('data_source'),
                       lambda d: d['data_source'].update(id='f'*32)):
            data = update(); change(data)
            with self.assertRaises((KeyError, ValueError)): MUTATION.prepare(data)

    def test_title_only_exception_cannot_bypass_database_schema(self):
        data = update(); data['call']['args']['properties'] = {'title': 'Fake ordinary page'}
        self.assertEqual(MUTATION.prepare(data)['status'], 'NeedsCorrection')

    def test_content_edits_checked_without_requiring_an_unrelated_schema_read(self):
        data = update(); del data['data_source']
        data['call']['args'].update(command='update_content', content_updates=[{'old_str': 'Waiting.', 'new_str': '[bad](/tmp/preview.png)'}])
        del data['call']['args']['properties']
        self.assertEqual(MUTATION.prepare(data)['status'], 'NeedsCorrection')
        data['call']['args']['content_updates'][0]['new_str'] = 'Sent message-one; no action required.'
        self.assertEqual(MUTATION.prepare(data)['status'], 'NotionMutationPrepared')

    def test_new_arguments_have_a_new_digest_not_an_old_schema_pass(self):
        data = update(); original = copy.deepcopy(data)
        result = MUTATION.prepare(data); self.assertEqual(data, original)
        data['call']['args']['properties']['ExternalIds'] = 'message: two'
        changed = MUTATION.prepare(data)
        self.assertNotEqual(result['call_sha256'], changed['call_sha256'])
        self.assertEqual(result['call']['args']['properties']['ExternalIds'], 'message: one')

    def test_actual_target_identity_and_complete_capture_required(self):
        for values in ({'id': 'f'*32}, {'truncated': True}, {'metadata': {'type': 'database'}}):
            data = update(); data['target'].update(values)
            with self.assertRaises(ValueError): MUTATION.prepare(data)

    def test_private_root_and_child_page_keep_the_real_host_contract(self):
        data = {'call': {'tool': 'mcp__codex_apps__notion_notion_create_pages', 'args': {
            'creation_mode': 'draft', 'pages': [{'properties': {'title': 'Aimore'}, 'content': 'Start here.'}]}}}
        self.assertEqual(MUTATION.prepare(data)['status'], 'NotionMutationPrepared')
        del data['call']['args']['creation_mode']; data['call']['args']['parent'] = {'page_id': REPORT}
        data['target'] = page('Existing parent')
        self.assertEqual(MUTATION.prepare(data)['status'], 'NotionMutationPrepared')
        data['call']['args']['pages'][0]['properties']['Status'] = 'Completed'
        with self.assertRaises(ValueError): MUTATION.prepare(data)

    def test_cli_refusal_is_nonzero_and_exposes_no_executable_call(self):
        data = create(); data['call']['args']['pages'][0]['content'] = '[bad](/tmp/a.md)'
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS/'notion_mutation.py'), '--input', '-'],
                                input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2); self.assertNotIn('call', json.loads(result.stdout))


if __name__ == '__main__':
    unittest.main()
