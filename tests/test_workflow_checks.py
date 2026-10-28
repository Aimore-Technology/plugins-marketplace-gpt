"""Evidence regressions; these tests never call external services or dispatch a workflow."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts/workflow_checks.py"
SPEC = importlib.util.spec_from_file_location("workflow_checks", SCRIPT)
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)
PAGE = "https://app.notion.com/p/" + "a" * 32


def envelope(provider, wrapper=None, error=True):
    return {"isError": error, "structuredContent": wrapper,
            "content": [{"type": "text", "text": json.dumps(provider)}]}


def task(step="SendApprovedReply", mode="Automatic"):
    route = json.loads(CHECKS.ROUTES_PATH.read_text())[step]
    return {"TaskId": "test-task", "RunId": "test-run", "StepId": "test-step",
            "SourceKey": "test-account:inbound:test-message", "ContentVersion": "test-v1",
            "Mode": mode, "State": "WaitingForOperator", "Category": route["categories"][0],
            "OwnerSkill": route["owner"], "ResumeStep": step, "ResumeContractVersion": "resume-v1"}


class ToolResultTests(unittest.TestCase):
    def test_workflow_capability_error_is_not_lost_to_generic_wrapper(self):
        original = {"success": False, "status": 403, "operationId": "search-workflows",
                    "data": {"statusCode": 403, "error": "Forbidden",
                             "code": "WORKFLOW_API_NOT_ENABLED_FOR_LOCATION",
                             "message": "The workflow API is not enabled for this test location."}}
        result = CHECKS.inspect_result(envelope(original, {"error_code": "INVALID_ARGUMENT"}))
        self.assertEqual(result["category"], "CapabilityUnavailable")
        self.assertEqual(result["primary_code"], "WORKFLOW_API_NOT_ENABLED_FOR_LOCATION")
        self.assertEqual(result["http_status"], 403)
        self.assertIn("INVALID_ARGUMENT", result["all_codes"])
        self.assertFalse(result["automatic_retry"])

    def test_upstream_access_refusal_beats_generic_invalid_argument(self):
        result = CHECKS.inspect_result(envelope({"success": False, "status": 403,
                                                 "data": {"error": "Forbidden"}},
                                                {"error_code": "INVALID_ARGUMENT"}))
        self.assertEqual((result["category"], result["http_status"]), ("AccessDenied", 403))

    def test_nested_gmail_rate_limit_is_distinguished_from_permission(self):
        result = CHECKS.inspect_result(envelope({"error_code": "FORBIDDEN", "error": "read failed",
            "error_data": {"code": "RATE_LIMIT_EXCEEDED", "response": {"status": 403}}}))
        self.assertEqual((result["category"], result["http_status"]), ("RateLimited", 403))
        self.assertIn("FORBIDDEN", result["all_codes"])

    def test_json_error_payload_is_examined(self):
        result = CHECKS.inspect_result(envelope({"error": "read failed", "error_data": {
            "response": {"status": 403, "payload": json.dumps({"error": {"code": 403,
                "details": [{"reason": "RATE_LIMIT_EXCEEDED"}]}})}}}))
        self.assertEqual(result["category"], "RateLimited")

    def test_plain_success_with_null_structured_content_stays_accepted(self):
        result = CHECKS.inspect_result({"isError": False, "structuredContent": None,
                                        "content": [{"type": "text", "text": "Action completed."}]})
        self.assertEqual(result["status"], "Accepted")
        self.assertIn("not delivery", result["scope"])

    def test_mcp_error_context_preserves_a_code_only_structured_error(self):
        result = CHECKS.inspect_result({"isError": True, "structuredContent": {"code": "FORBIDDEN"}, "content": []})
        self.assertEqual(result["category"], "AccessDenied")
        self.assertEqual(result["primary_code"], "FORBIDDEN")

    def test_known_error_is_not_hidden_by_other_success_text(self):
        result = CHECKS.inspect_result({"isError": True, "structuredContent": {"error_code": "FORBIDDEN"},
                                        "content": [{"type": "text", "text": "Action completed."}]})
        self.assertEqual(result["status"], "Error")

    def test_customer_prose_is_not_an_error_envelope(self):
        result = CHECKS.inspect_result(envelope({"success": True, "data": {
            "body": "Customer mentioned an error", "error_code": "a quoted customer field"}}, error=False))
        self.assertEqual(result["status"], "Accepted")
        result = CHECKS.inspect_result({"content": [{"type": "text", "text": "Customer said error yesterday."}]})
        self.assertEqual(result["status"], "Unclassified")


class NotionLinkTests(unittest.TestCase):
    def test_bare_url_before_publication_catches_swallowed_prose(self):
        result = CHECKS.check_links(PAGE + "\uff1bscope=live")
        self.assertEqual(result["issue_count"], 1)
        self.assertIn("MalformedNotionPageTarget", result["issues"][0]["reasons"])

    def test_explicit_links_are_not_double_counted_as_bare_urls(self):
        result = CHECKS.check_links(f'[task]({PAGE}) <mention url="{PAGE}" />')
        self.assertEqual(result["links_examined"], 2)

    def test_bare_literal_file_url_is_ignored_in_code_only(self):
        self.assertEqual(CHECKS.check_links("http://note.py")["issue_count"], 1)
        self.assertEqual(CHECKS.check_links("`http://note.py`")["links_examined"], 0)

    def test_script_skill_filename_and_encoded_host_all_get_reviewed(self):
        text = "[note.py](http://note.py) [SKILL.md](http://SKILL.md) [example](http://%E4%B8%8Dexample.com)"
        result = CHECKS.check_links(text)
        self.assertEqual(result["issue_count"], 3)

    def test_tables_prose_and_history_are_all_checked(self):
        text = "| file | ref |\n| --- | --- |\n| x | [x](http://x.py) |\n\n## History\n[x](http://x.md)\n"
        result = CHECKS.check_links(text)
        self.assertEqual([x["line"] for x in result["issues"]], [3, 6])

    def test_notions_target_suffix_and_encoded_punctuation_are_flagged(self):
        text = f"[task]({PAGE}%EF%BC%9Bscope)"
        result = CHECKS.check_links(text)
        self.assertIn("MalformedNotionPageTarget", result["issues"][0]["reasons"])
        self.assertIn("PunctuationInTarget", result["issues"][0]["reasons"])

    def test_native_mentions_are_checked_too(self):
        result = CHECKS.check_links(f'<mention url="{PAGE}wrong" />')
        self.assertEqual(result["issue_count"], 1)

    def test_literal_code_examples_are_not_clickable_targets(self):
        text = "`[x](http://x.py)`\n```text\n[x](http://x.md)\n```\n<code>[x](http://x.json)</code>\n"
        self.assertEqual(CHECKS.check_links(text)["links_examined"], 0)

    def test_exact_verified_file_like_domain_can_be_allowed(self):
        text = "[site](https://readme.md)"
        self.assertEqual(CHECKS.check_links(text)["issue_count"], 1)
        self.assertEqual(CHECKS.check_links(text, ["https://readme.md"])["issue_count"], 0)

    def test_valid_provider_and_upload_links_do_not_claim_network_validation(self):
        result = CHECKS.check_links(f'[task]({PAGE}?pvs=204) [source](https://www.dropbox.com/scl/fi/test) '
                                     '<embed source="notion-file-block://test/file" />')
        self.assertEqual(result["status"], "ClearForCheckedPatterns")
        self.assertIn("no network", result["scope"])

    def test_local_file_links_in_notion_need_literal_presentation(self):
        result = CHECKS.check_links("[report](/home/test/REPORT.md)")
        self.assertEqual(result["issues"][0]["reasons"], ["LocalFileLinkInNotion"])

    def test_notions_actual_mcp_text_is_extracted_and_failed_read_is_not_empty(self):
        text = "[bad](http://SKILL.md)"
        saved = envelope({"id": "test-page", "text": text}, error=False)
        self.assertEqual(CHECKS.notion_text(saved), text)
        with self.assertRaises(ValueError):
            CHECKS.notion_text({"isError": True, "content": []})
        with self.assertRaises(ValueError):
            CHECKS.notion_text({"content": [{"type": "text", "text": "Action completed."}]})


class ResumeRouteTests(unittest.TestCase):
    def test_every_registered_route_has_a_valid_owner_for_each_category(self):
        routes = json.loads(CHECKS.ROUTES_PATH.read_text())
        for step, route in routes.items():
            for category in route["categories"]:
                item = task(step)
                item["Category"] = category
                with self.subTest(step=step, category=category):
                    result = CHECKS.check_resume(item, "owner-workflow")
                    self.assertEqual(result["status"], "EligibleForOwnerCheck")
                    self.assertIn("approval", result["scope"])

    def test_send_task_with_communication_owner_is_rejected(self):
        item = task()
        item["OwnerSkill"] = "eightdegrees-communication-context-process"
        self.assertEqual(CHECKS.check_resume(item, "owner-workflow")["status"], "NeedsCorrection")

    def test_parent_workflow_does_not_override_the_actual_owner(self):
        item = task()
        item["Workflow"] = "eightdegrees-communication-context-process"
        result = CHECKS.check_resume(item, "owner-workflow")
        self.assertEqual(result["owner"], "eightdegrees-sales-reply")

    def test_blank_legacy_resume_is_not_guessed(self):
        item = task()
        item["ResumeStep"] = ""
        result = CHECKS.check_resume(item, "owner-workflow")
        self.assertEqual(result["status"], "NeedsCorrection")
        self.assertIn("ResumeStep", result["missing"])

    def test_wrong_step_category_is_rejected(self):
        item = task()
        item["Category"] = "ContentReview"
        self.assertEqual(CHECKS.check_resume(item, "owner-workflow")["status"], "NeedsCorrection")

    def test_manual_scan_is_deferred_even_with_continue_flag(self):
        item = task("ReviewCommunication", "Manual")
        for explicit in (False, True):
            self.assertEqual(CHECKS.check_resume(item, "one-cycle-no-customer-send", explicit)["status"], "Deferred")

    def test_manual_communication_requires_explicit_continue(self):
        item = task("ReviewCommunication", "Manual")
        self.assertEqual(CHECKS.check_resume(item, "manual-review")["status"], "Deferred")
        self.assertEqual(CHECKS.check_resume(item, "manual-review", True)["status"], "EligibleForOwnerCheck")
        item["Mode"] = "Automatic"
        self.assertEqual(CHECKS.check_resume(item, "manual-review", True)["status"], "Deferred")

    def test_all_five_shortcut_policies_defer_customer_sends(self):
        for policy in CHECKS.POLICIES[:-1]:
            with self.subTest(policy=policy):
                self.assertEqual(CHECKS.check_resume(task(), policy, True)["status"], "Deferred")

    def test_closed_legacy_task_does_not_need_a_route_migration(self):
        self.assertEqual(CHECKS.check_resume({"State": "Completed"}, "owner-workflow")["status"], "Deferred")

    def test_scan_can_record_auto_send_choice_without_executing_it(self):
        result = CHECKS.check_resume(task(), "one-cycle-no-customer-send", phase="observe")
        self.assertEqual(result["status"], "EligibleForInputCheck")
        self.assertEqual(CHECKS.check_resume(task(), "one-cycle-no-customer-send")["status"], "Deferred")
        for policy in ("report-only", "draft-only"):
            self.assertEqual(CHECKS.check_resume(task(), policy, phase="observe")["status"], "Deferred")
        self.assertEqual(CHECKS.check_resume(task(mode="Manual"), "one-cycle-no-customer-send", phase="observe")["status"], "Deferred")

    def test_cli_rejects_wrong_owner_and_reports_saved_link_errors(self):
        item = task()
        item["OwnerSkill"] = "eightdegrees-communication-context-process"
        result = subprocess.run([sys.executable, str(SCRIPT), "resume-task", "--input", "-", "--policy", "owner-workflow"],
                                input=json.dumps(item), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "NeedsCorrection")
        result = subprocess.run([sys.executable, str(SCRIPT), "notion-links", "--input", "-", "--input-format", "markdown"],
                                input="[file](http://SKILL.md)", capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["issue_count"], 1)


if __name__ == "__main__":
    unittest.main()
