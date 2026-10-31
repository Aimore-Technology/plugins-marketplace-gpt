"""Pre-call refusal regressions for Q19-01/Q19-02; no connector writes."""

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
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
    def test_first_create_and_update_refuse_display_markup_in_machine_identity(self):
        for factory in (create, update):
            for value in ('[task](https://app.notion.com/p/' + REPORT + ')', '**task-id**', '<mention url="x"/>', '`task-id`'):
                data = factory()
                props = data['call']['args'].get('properties', data['call']['args'].get('pages', [{}])[0].get('properties'))
                props['TaskId'] = value
                with self.assertRaisesRegex(ValueError, 'Canonical TaskId'):
                    MUTATION.prepare(data)

    def test_exact_identity_is_preserved_without_rewriting_a_title_or_business_prose(self):
        data = create()
        state = json.loads(data['data_source']['text'].split('<data-source-state>')[1].split('</data-source-state>')[0])
        state['schema']['TaskId'] = {'type': 'text'}
        data['data_source']['text'] = '<data-source-state>' + json.dumps(state) + '</data-source-state>'
        data['call']['args']['pages'][0]['properties']['TaskId'] = 'location:contact:step-1'
        result = MUTATION.prepare(data)
        self.assertEqual(result['status'], 'NotionMutationPrepared')
        self.assertEqual(result['call'], data['call'])

    def test_same_parent_schema_appendix_is_not_a_second_parent(self):
        data=update()
        data['target']['text']+='\n<parent-data-source-schema url="collection://'+PARENT+'">\nCREATE TABLE source;\n</parent-data-source-schema>'
        result=MUTATION.prepare(data)
        self.assertEqual(result['status'],'NotionMutationPrepared')
        self.assertEqual(result['call'],data['call'])

    def test_schema_documentation_cannot_supply_or_redirect_the_parent(self):
        data=update()
        data['target']['text']+='\n<parent-data-source-schema url="collection://'+'f'*32+'">Docs</parent-data-source-schema>'
        self.assertEqual(MUTATION.prepare(data)['status'],'NotionMutationPrepared')
        data['target']['text']=data['target']['text'].replace('<parent-data-source url="collection://'+PARENT+'"/>\n','')
        with self.assertRaises(ValueError):MUTATION.prepare(data)

    def test_two_real_parent_tags_still_refuse_instead_of_choosing_one(self):
        data=update();data['target']['text']+='\n<parent-data-source url="collection://'+'f'*32+'"/>'
        with self.assertRaisesRegex(ValueError,'Ambiguous original parent'):MUTATION.prepare(data)

    def test_large_call_file_output_preserves_exact_args_without_echoing_body(self):
        data=create();data['call']['args']['pages'][0]['content']='Private capture text. '*1000
        with tempfile.TemporaryDirectory() as folder:
            original=Path(folder)/'input.json';saved=Path(folder)/'checked.json';original.write_text(json.dumps(data))
            result=subprocess.run([sys.executable,'-B',str(SCRIPTS/'notion_mutation.py'),'--input',str(original),'--output',str(saved)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0)
            summary=json.loads(result.stdout);full=json.loads(saved.read_text())
            self.assertNotIn('call',summary);self.assertNotIn('Private capture text',result.stdout)
            self.assertEqual(full['call'],data['call']);self.assertEqual(full['call_sha256'],summary['call_sha256'])

    def test_checked_call_output_cannot_overwrite_its_original_input(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'input.json';original=json.dumps(create());p.write_text(original)
            result=subprocess.run([sys.executable,'-B',str(SCRIPTS/'notion_mutation.py'),'--input',str(p),'--output',str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertEqual(p.read_text(),original)

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
