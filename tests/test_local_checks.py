"""Local batching reuses captures without weakening refusal/error layers."""

import copy
import unittest
from unittest.mock import patch

from test_notion_checks import page, source_schema, PARENT
import local_checks as LOCAL
import notion_checks as CHECKS


class LocalCheckTests(unittest.TestCase):
    def test_one_original_capture_reused_for_two_checks_matches_direct_results(self):
        capture=page('Current result.');plan={'checks':[
            {'name':'first','operation':'notion.page-links','input':{'page':{'$capture':'original'}}},
            {'name':'second','operation':'notion.page-links','input':{'page':{'$capture':'original'}}}]}
        before=copy.deepcopy(capture);result=LOCAL.run(plan,{'original':capture})
        self.assertEqual(result['status'],'LocalChecksPassed');self.assertEqual(result['checks_run'],2)
        self.assertEqual(result['distinct_captures_used'],1);self.assertEqual(result['capture_references'],2)
        for check in result['checks']:self.assertEqual(check['result'],CHECKS.page_links({'page':capture}))
        self.assertEqual(capture,before)

    def test_failed_first_check_does_not_run_the_next(self):
        plan={'checks':[{'name':'bad','operation':'notion.schema-values','input':{
            'data_source':{'$capture':'schema'},'data_source_id':PARENT,'properties':{'Status':'Invented'}}},
            {'name':'not-run','operation':'notion.page-links','input':{'page':{'$capture':'missing'}}}]}
        result=LOCAL.run(plan,{'schema':source_schema()})
        self.assertEqual(result['status'],'NeedsCorrection');self.assertEqual(result['checks_run'],1)
        self.assertEqual(result['checks'][0]['exit_code'],2)

    def test_nested_mcp_error_and_omitted_blocks_are_preserved(self):
        captures=[{'structuredContent':page('Fine'),'isError':True},page('Fine')]
        captures[1]['unknown_block_count']=1
        for original in captures:
            result=LOCAL.run({'checks':[{'name':'x','operation':'notion.page-links','input':{'page':{'$capture':'x'}}}]},{'x':original})
            self.assertEqual(result['status'],'NeedsCorrection')

    def test_unknown_operation_or_missing_capture_is_a_refusal_not_a_fallback(self):
        for op in ['notion.page-links','send_email']:
            result=LOCAL.run({'checks':[{'name':'x','operation':op,'input':{'page':{'$capture':'missing'}}}]},{})
            self.assertEqual(result['status'],'NeedsCorrection')

    def test_duplicate_names_and_forward_result_references_are_rejected(self):
        check={'name':'x','operation':'notion.page-links','input':{'page':{'$result':'later'}}}
        with self.assertRaises(ValueError):LOCAL.run({'checks':[check,check]},{})
        self.assertEqual(LOCAL.run({'checks':[check]}, {})['status'],'NeedsCorrection')

    def test_failure_keeps_original_bundle_and_no_captured_body_is_printed(self):
        capture=page('Private source text [bad](/tmp/a.md)');before=copy.deepcopy(capture)
        result=LOCAL.run({'checks':[{'name':'x','operation':'notion.page-links','input':{'page':{'$capture':'x'}}}]},{'x':capture})
        self.assertEqual(result['status'],'NeedsCorrection');self.assertEqual(capture,before)
        self.assertNotIn('Private source text',str(result))


if __name__=='__main__':unittest.main()
