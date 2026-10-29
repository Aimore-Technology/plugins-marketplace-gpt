"""Publication regressions; all fixtures are offline, with no connector calls."""

import hashlib
import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("notion_checks", SCRIPTS / "notion_checks.py")
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)
REPORT, RUN, LOGS, TASK, PARENT = [c * 32 for c in "abcde"]
FILE = "12345678-1234-1234-1234-123456789abc"
HTML = "<!doctype html><p>Frozen \\n text</p>\n"


def page(text):
    return {"id": REPORT, "metadata": {"type": "page"}, "text": '<page>\n<properties>{"title":"Test"}</properties>\n<content>\n' + text + '\n</content>\n</page>'}


def completion():
    return {"invocation_id": "report-1", "publication_version": "revision-1",
            "required_checks": {"saved-report": {"kind": "page-links", "entity_id": REPORT}},
            "checks": [{"name": "saved-report", "invocation_id": "report-1", "publication_version": "revision-1",
                        "exit_code": 0, "result": CHECKS.page_links({"page": page("Report content")})}]}


def source_schema():
    state = {"url": "collection://" + PARENT, "schema": {
        "Status": {"type": "select", "options": [{"name": x} for x in ["Saved", "Waiting", "Completed"]]},
        "Tags": {"type": "multi_select", "options": [{"name": "TEST"}]},
        "Created": {"type": "date", "readOnly": True}}}
    return {"id": state["url"], "metadata": {"type": "data_source"},
            "text": '<data-source-state>\n' + json.dumps(state) + '\n</data-source-state>'}


def preview(text=None):
    return {"page": page(text if text is not None else f'<embed source="file-upload://{FILE}" />'),
            "html_file_id": FILE, "html_sha256": hashlib.sha256(HTML.encode()).hexdigest(),
            "download": {"file_upload_id": FILE, "content_type": "text/html; charset=utf-8", "content": HTML}}


def write(tool="notion_notion_update_page", **args):
    return {"registry": {"report_page_ids": [REPORT], "report_run_page_ids": [RUN],
                         "operation_log_source_ids": [LOGS], "invocation_id": "report-1", "publication_version": "revision-1"},
            "call": {"tool": "mcp__codex_apps__" + tool,
                     "args": args or {"page_id": REPORT, "command": "update_content", "content_updates": []}}}


class SectionPatchTests(unittest.TestCase):
    def test_transition_replaces_only_current_section_and_preserves_answers_history_children(self):
        old = "## Current status\n\nWaiting for input."
        suffix = '\n\n## Your input\n\nAnswer kept.\n- [x] Submit\n\n## History\n\nOld v1.\n<page url="child">Keep</page>'
        current = old + suffix
        new = "## Current status\n\nCompleted v2; no action required."
        result = CHECKS.section_patch({"page": page(current), "heading": "Current status", "replacement": new})
        self.assertEqual(result["status"], "PatchPlanned")
        changed = current.replace(result["old_str"], result["new_str"])
        self.assertEqual(changed, new + suffix)

    def test_repeated_application_is_no_change(self):
        text = "## Current status\n\nCompleted v2."
        self.assertEqual(CHECKS.section_patch({"page": page(text), "heading": "Current status", "replacement": text})["status"], "NoChange")

    def test_duplicate_historical_heading_does_not_choose_arbitrarily(self):
        text = "## Current status\n\nWaiting\n\n## Current status\n\nOld"
        result = CHECKS.section_patch({"page": page(text), "heading": "Current status", "replacement": "## Current status\n\nDone"})
        self.assertEqual((result["status"], result["matches"]), ("NeedsCorrection", 2))

    def test_nonexistent_waiting_text_is_not_invented(self):
        result = CHECKS.section_patch({"page": page("Already accepted."), "heading": "Current status", "replacement": "## Current status\n\nDone"})
        self.assertEqual(result["status"], "NeedsCorrection")

    def test_replacement_cannot_smuggle_another_top_level_section(self):
        with self.assertRaises(ValueError):
            CHECKS.section_patch({"page": page("## Current status\n\nWaiting"), "heading": "Current status",
                "replacement": "## Current status\n\nDone\n\n## Your input\n\nOverwritten"})

    def test_input_or_child_inside_target_section_blocks_broad_patch(self):
        for protected in ('- [x] Confirm', '<page url="child">Keep</page>', '<todo checked="true">Keep</todo>'):
            with self.subTest(protected=protected):
                result = CHECKS.section_patch({"page": page("## Current status\n\n" + protected),
                    "heading": "Current status", "replacement": "## Current status\n\nDone"})
                self.assertEqual(result["status"], "NeedsCorrection")

    def test_localized_heading_is_supported_without_runtime_language_assumption(self):
        heading = "\u5f53\u524d\u72b6\u6001"
        result = CHECKS.section_patch({"page": page("## " + heading + "\n\nOld"),
            "heading": heading, "replacement": "## " + heading + "\n\nNew"})
        self.assertEqual(result["status"], "PatchPlanned")

    def test_code_example_heading_is_not_a_real_second_status(self):
        text = "## Current status\n\nDone\n\n## History\n\n```text\n## Current status\nOld\n```"
        result = CHECKS.section_patch({"page": page(text), "heading": "Current status", "replacement": "## Current status\n\nDone"})
        self.assertEqual(result["status"], "NoChange")

    def test_failed_or_explicitly_incomplete_fetch_cannot_plan_a_write(self):
        for capture in ({"isError": True}, {**page("x"), "truncated": True}, {**page("x"), "unknown_block_count": 1}):
            with self.assertRaises(ValueError):
                CHECKS.section_patch({"page": capture, "heading": "Current status", "replacement": "## Current status\n\nDone"})


class PreviewTests(unittest.TestCase):
    def test_saved_embed_and_original_download_match(self):
        result = CHECKS.check_preview(preview())
        self.assertEqual(result["status"], "SavedEmbedAndBytesMatch")
        self.assertIn("host visual", result["scope"])

    def test_raw_uri_file_and_code_do_not_satisfy_saved_preview(self):
        for text in (f'file-upload://{FILE}', f'<file source="file-upload://{FILE}" />',
                     f'```text\n<embed source="file-upload://{FILE}" />\n```',
                     f'`<embed source="file-upload://{FILE}" />`'):
            with self.subTest(text=text):
                self.assertEqual(CHECKS.check_preview(preview(text))["status"], "NeedsCorrection")

    def test_embed_for_another_file_does_not_approve_current_version(self):
        self.assertEqual(CHECKS.check_preview(preview('<embed source="file-upload://old-version" />'))["status"], "NeedsCorrection")

    def test_stable_reference_requires_real_mapping_instead_of_assumed_identity(self):
        result = CHECKS.check_preview(preview(f'<embed source="notion-file-block://{FILE}" />'))
        self.assertEqual(result["status"], "NeedsCorrection")
        self.assertIn("original fetched mapping", result["scope"])

    def test_stable_saved_embed_requires_resolved_reference_and_matching_actual_bytes(self):
        ref, url = "notion-file-block://saved-block/asset", "https://files.example.invalid/actual.html?signature=test"
        data = preview(f'<embed source="{ref}" />')
        data["page"]["metadata"] = {"references": {ref: url}}
        data["embedded_asset"] = {"source": ref, "resolved_url": url, "content_base64": base64.b64encode(HTML.encode()).decode()}
        self.assertEqual(CHECKS.check_preview(data)["status"], "SavedEmbedAndBytesMatch")
        data["embedded_asset"]["content_base64"] = base64.b64encode(b"different file").decode()
        self.assertEqual(CHECKS.check_preview(data)["status"], "NeedsCorrection")

    def test_stable_source_filename_or_guessed_url_cannot_prove_the_mapping(self):
        ref = "notion-file-block://saved-block/asset"
        data = preview(f'<embed source="{ref}" />')
        data["page"]["metadata"] = {"references": {ref: "https://files.example.invalid/original.html"}}
        data["embedded_asset"] = {"source": ref, "resolved_url": "https://files.example.invalid/guessed.html", "content_base64": base64.b64encode(HTML.encode()).decode()}
        self.assertEqual(CHECKS.check_preview(data)["status"], "NeedsCorrection")

    def test_changed_bytes_and_wrong_download_identity_are_rejected(self):
        for key, value in (("content", HTML + "changed"), ("file_upload_id", REPORT), ("content_type", "text/plain")):
            data = preview(); data["download"][key] = value
            self.assertEqual(CHECKS.check_preview(data)["status"], "NeedsCorrection")

    def test_text_json_result_is_read_once_preserving_literal_backslash(self):
        data = preview()
        data["download"] = {"isError": False, "structuredContent": None,
                            "content": [{"type": "text", "text": json.dumps(data["download"])}]}
        self.assertEqual(CHECKS.check_preview(data)["status"], "SavedEmbedAndBytesMatch")

    def test_error_envelope_cannot_be_hidden_by_successful_download_fields(self):
        data = preview()
        data["download"] = {"isError": True, "structuredContent": data["download"],
                            "content": [{"type": "text", "text": '{"error_code":"FORBIDDEN"}'}]}
        with self.assertRaises(ValueError):
            CHECKS.check_preview(data)


class ReportScopeTests(unittest.TestCase):
    def test_targeted_report_update_is_permitted(self):
        self.assertEqual(CHECKS.report_write(write())["status"], "WithinReportScope")

    def test_task_preview_health_and_hub_writes_are_deferred(self):
        # The actual report43 failure was a preview update followed by task-history inserts.
        for command in ("update_content", "insert_content", "update_properties"):
            result = CHECKS.report_write(write(page_id=TASK, command=command, content="History repair"))
            self.assertEqual(result["status"], "Deferred")

    def test_report_whole_page_template_or_deletion_operation_is_not_allowed(self):
        for args in ({"command": "replace_content"}, {"command": "apply_template"},
                     {"command": "update_content", "template_id": TASK},
                     {"command": "update_content", "allow_deleting_content": True}):
            self.assertEqual(CHECKS.report_write(write(page_id=REPORT, **args))["status"], "Deferred")

    def test_only_own_report_run_status_fields_can_be_changed(self):
        good = write(page_id=RUN, command="update_properties", properties={"State": "Completed", "Result": "Published"})
        good["completion"] = completion()
        self.assertEqual(CHECKS.report_write(good)["status"], "WithinReportScope")
        good["call"]["args"]["properties"]["Decision"] = "Approve"
        self.assertEqual(CHECKS.report_write(good)["status"], "Deferred")

    def test_append_log_is_allowed_but_task_creation_is_not(self):
        for parent, status in ((LOGS, "WithinReportScope"), (TASK, "Deferred")):
            data = write("notion_notion_create_pages", parent={"data_source_id": parent}, pages=[{"properties": {"Name": "Evidence"}}])
            self.assertEqual(CHECKS.report_write(data)["status"], status)

    def test_create_own_report_run_requires_exact_invocation_and_skill(self):
        data = write("notion_notion_create_pages", parent={"data_source_id": RUN}, pages=[{"properties": {
            "RunId": "report-invocation-1", "Skill": "eightdegrees-daily-brief-and-handover"}}])
        data["registry"].update(workflow_run_source_ids=[RUN], report_run_id="report-invocation-1")
        self.assertEqual(CHECKS.report_write(data)["status"], "WithinReportScope")
        data["call"]["args"]["pages"][0]["properties"]["RunId"] = "another-run"
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")

    def test_new_report_requires_registered_exact_parent_and_title(self):
        data = write("notion_notion_create_pages", parent={"page_id": PARENT}, pages=[{"properties": {"title": "Daily report"}}])
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")
        data["registry"]["report_creations"] = [{"parent_page_id": PARENT, "title": "Daily report"}]
        self.assertEqual(CHECKS.report_write(data)["status"], "WithinReportScope")
        data["call"]["args"]["pages"].append({"properties": {"title": "Repair task"}})
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")

    def test_daily_brief_database_creation_uses_exact_registered_title_property(self):
        data = write("notion_notion_create_pages", parent={"data_source_id": PARENT}, pages=[{"properties": {"Name": "Daily report"}}])
        data["registry"]["report_creations"] = [{"parent_data_source_id": PARENT, "title_property": "Name", "title": "Daily report"}]
        self.assertEqual(CHECKS.report_write(data)["status"], "WithinReportScope")
        data["call"]["args"]["pages"][0]["properties"]["Name"] = "Another task"
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")

    def test_provider_schema_attachment_navigation_and_owner_calls_are_excluded(self):
        for tool in ("leadconnector_mcp_execute_operation", "gmail_send_email", "notion_notion_create_attachment",
                     "notion_notion_update_data_source", "notion_notion_update_view", "notion_notion_move_pages"):
            with self.subTest(tool=tool):
                self.assertEqual(CHECKS.report_write(write(tool, operationId="create-note"))["status"], "Deferred")

    def test_id_representation_normalizes_registered_url_uuid_and_compact_id(self):
        data = write(page_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", command="insert_content", content="Report only")
        data["registry"]["report_page_ids"] = ["https://app.notion.com/p/" + REPORT]
        self.assertEqual(CHECKS.report_write(data)["status"], "WithinReportScope")

    def test_unregistered_business_id_cannot_pass_because_of_its_title(self):
        data = write(page_id=TASK, command="update_properties", properties={"title": "Daily report"})
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")

    def test_cli_deferred_write_returns_nonzero_without_execution(self):
        data = write("gmail_send_email", to="test@example.invalid")
        result = subprocess.run([sys.executable, str(SCRIPTS / "notion_checks.py"), "report-write", "--input", "-"],
                                input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "Deferred")


class NativePatchRegressionTests(unittest.TestCase):
    def test_native_reference_cannot_be_a_whole_section_match_anchor(self):
        for native in (f'<mention url="https://app.notion.com/p/{TASK}">Task</mention>',
                       f'<mention url="https://app.notion.com/p/{TASK}" />',
                       '<date start="2026-10-29" />', '<embed source="file-upload://asset" />'):
            old = "## Current status\n\n" + native
            result = CHECKS.section_patch({"page": page(old), "heading": "Current status", "replacement": "## Current status\n\nUpdated"})
            self.assertEqual(result["status"], "NeedsCorrection")
            self.assertNotIn("old_str", result)

    def test_already_matching_native_section_does_not_require_a_write(self):
        text = '## Current status\n\n<mention url="https://app.notion.com/p/' + TASK + '" />'
        self.assertEqual(CHECKS.section_patch({"page": page(text), "heading": "Current status", "replacement": text})["status"], "NoChange")

    def test_native_reference_in_another_section_preserves_plain_status_patch(self):
        text = f'## Current status\n\nOld\n\n## Source\n\n<mention url="https://app.notion.com/p/{TASK}" />'
        result = CHECKS.section_patch({"page": page(text), "heading": "Current status", "replacement": "## Current status\n\nNew"})
        self.assertEqual(result["status"], "PatchPlanned")
        self.assertNotIn("mention", result["old_str"])


class PageCoverageTests(unittest.TestCase):
    def test_only_page_content_not_fetch_wrapper_is_scanned(self):
        data = page("Clean page")
        data["text"] = 'Wrapper http://SKILL.md}}\n' + data["text"]
        self.assertEqual(CHECKS.page_links({"page": data})["issue_count"], 0)

    def test_database_view_and_source_are_excluded_not_passed_as_pages(self):
        for kind in ("database", "view", "saved_view", "data_source"):
            data = {"id": PARENT, "metadata": {"type": kind}, "text": "http://SKILL.md}}"}
            self.assertEqual(CHECKS.page_links({"page": data})["status"], "ExcludedNonPage")

    def test_actual_page_bad_link_still_fails(self):
        self.assertEqual(CHECKS.page_links({"page": page("[bad](http://SKILL.md)")})["status"], "NeedsCorrection")

    def test_unknown_entity_type_is_not_inferred_from_arbitrary_text(self):
        data = page("Clean")
        del data["metadata"]
        self.assertEqual(CHECKS.page_links({"page": data})["status"], "NeedsCorrection")

    def test_metadata_omitted_blocks_or_truncation_block_page_check(self):
        for key, value in (("unknown_block_ids", ["missing"]), ("unknown_block_count", 1), ("truncated", True)):
            data = page("Clean"); data["metadata"][key] = value
            with self.assertRaises(ValueError):
                CHECKS.page_links({"page": data})


class EnumPreflightTests(unittest.TestCase):
    def test_current_schema_values_pass_without_schema_mutation(self):
        for value in ("Saved", "Waiting", "Completed", None):
            result = CHECKS.schema_values({"data_source": source_schema(), "data_source_id": PARENT, "properties": {"Status": value}})
            self.assertEqual(result["status"], "ValidSelectValues")

    def test_observed_invalid_status_and_wrong_case_fail_before_write(self):
        for value in ("NeedsData", "waiting"):
            result = CHECKS.schema_values({"data_source": source_schema(), "data_source_id": PARENT, "properties": {"Status": value}})
            self.assertEqual(result["status"], "NeedsCorrection")
            self.assertEqual(result["issues"][0]["allowed"], ["Saved", "Waiting", "Completed"])

    def test_another_database_schema_cannot_validate_the_target(self):
        with self.assertRaises(ValueError):
            CHECKS.schema_values({"data_source": source_schema(), "data_source_id": TASK, "properties": {"Status": "Waiting"}})

    def test_unknown_or_readonly_property_is_not_silently_accepted(self):
        for key in ("NotAProperty", "date:Created:start"):
            self.assertEqual(CHECKS.schema_values({"data_source": source_schema(), "data_source_id": PARENT, "properties": {key: "x"}})["status"], "NeedsCorrection")

    def test_multiselect_checks_all_options_and_representation(self):
        for value, status in ((["TEST"], "ValidSelectValues"), ([], "ValidSelectValues"), (["TEST", "Other"], "NeedsCorrection"), ("TEST", "NeedsCorrection")):
            self.assertEqual(CHECKS.schema_values({"data_source": source_schema(), "data_source_id": PARENT, "properties": {"Tags": value}})["status"], status)


class DisplayRegressionTests(unittest.TestCase):
    def display(self, result="Pause recorded; no action required.", controls="Historical answers retained."):
        return {"page": page("## Current status\n\nPaused. Version: draft-v2.\n\n## Your input\n\n" + controls
                             + "\n\n## Processing result\n\n" + result),
                "task": {"State": "WaitingForOperator", "ContentVersion": "draft-v2", "Decision": "Pause", "DecisionVersion": "draft-v2"}}

    def test_paused_header_and_unsubmitted_result_conflict_is_caught(self):
        for text in ("Not yet submitted; saving is not approval.", "\u5c1a\u672a\u63d0\u4ea4\uff1b\u4fdd\u5b58\u4e0d\u7b49\u4e8e\u6279\u51c6\u3002"):
            result = CHECKS.task_display(self.display(result=text))
            self.assertEqual(result["status"], "NeedsCorrection")
            self.assertTrue(any(x["section"] == "result" for x in result["issues"]))

    def test_paused_form_cannot_retain_choose_one_or_submission_controls(self):
        for text in ("Choose one:", "\u8bf7\u9009\u62e9\u4e00\u9879\uff1a", "- [ ] Submit content decision"):
            self.assertEqual(CHECKS.task_display(self.display(controls=text))["status"], "NeedsCorrection")

    def test_consistent_current_sections_ignore_original_quotes_and_history(self):
        data = self.display()
        data["page"]["text"] = data["page"]["text"].replace("\n</content>", "\n\n## Review material\n\nCustomer said: not yet submitted.\n\n## History\n\nChoose one: old version.\n</content>")
        self.assertEqual(CHECKS.task_display(data)["status"], "DisplayConsistentForCheckedPatterns")

    def test_completed_task_cannot_request_another_submission(self):
        data = self.display(controls="- [ ] Submit information")
        data["task"].update(State="Completed", Decision="", DecisionVersion="")
        self.assertEqual(CHECKS.task_display(data)["status"], "NeedsCorrection")

    def test_an_old_version_decision_does_not_mean_new_unsubmitted_copy_is_accepted(self):
        data = self.display(result="Not yet submitted", controls="Choose one:")
        data["task"]["DecisionVersion"] = "draft-v1"
        self.assertEqual(CHECKS.task_display(data)["status"], "DisplayConsistentForCheckedPatterns")

    def test_duplicate_missing_and_stale_current_sections_fail(self):
        for text in ("## Current status\n\nVersion: draft-v2.",
                     "## Current status\n\nVersion: draft-v1.\n\n## Processing result\n\nRecorded.",
                     "## Current status\n\nVersion: draft-v2.\n\n## Processing result\n\nRecorded.\n\n## Processing result\n\nOld"):
            data = self.display(); data["page"] = page(text)
            self.assertEqual(CHECKS.task_display(data)["status"], "NeedsCorrection")


class CompletionGateTests(unittest.TestCase):
    def test_current_successful_required_checks_allow_completion_only(self):
        self.assertEqual(CHECKS.completion_gate(completion())["status"], "EligibleForCompletion")

    def test_empty_or_missing_required_results_cannot_pass_vacuously(self):
        data = completion(); data["checks"] = []
        self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")
        data["required_checks"] = {}
        with self.assertRaises(ValueError):
            CHECKS.completion_gate(data)

    def test_nonzero_exit_cannot_be_hidden_by_successful_json(self):
        data = completion(); data["checks"][0]["exit_code"] = 1
        self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")

    def test_failed_exception_and_missing_json_block_completion(self):
        for result in ({"status": "NeedsCorrection"}, None, "Traceback", {}):
            data = completion(); data["checks"][0]["result"] = result
            self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")

    def test_skip_or_wrong_entity_cannot_fulfil_a_required_page(self):
        for kind, status in (("database", "ExcludedNonPage"), ("database", "ClearForCheckedPatterns")):
            data = completion(); data["checks"][0]["result"].update(entity_type=kind, status=status)
            self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")

    def test_stale_invocation_version_or_target_cannot_be_reused(self):
        for key, value in (("invocation_id", "old-run"), ("publication_version", "old-revision"), ("exit_code", False)):
            data = completion(); data["checks"][0][key] = value
            self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")
        data = completion(); data["checks"][0]["result"]["entity_id"] = TASK
        self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")

    def test_duplicate_and_unexpected_results_block_ambiguous_aggregation(self):
        for name in ("saved-report", "unexpected-database"):
            data = completion(); extra = dict(data["checks"][0]); extra["name"] = name; data["checks"].append(extra)
            self.assertEqual(CHECKS.completion_gate(data)["status"], "NeedsCorrection")

    def test_final_run_completion_requires_evidence_and_all_report_targets(self):
        data = write(page_id=RUN, command="update_properties", properties={"Status": "Completed"})
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")
        data["completion"] = completion()
        self.assertEqual(CHECKS.report_write(data)["status"], "WithinReportScope")
        data["registry"]["report_page_ids"].append(TASK)
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")

    def test_premature_success_log_is_deferred_even_for_correct_log_source(self):
        data = write("notion_notion_create_pages", parent={"data_source_id": LOGS}, pages=[{"properties": {"Name": "Report result", "Result": "Success", "Phase": "Result"}}])
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")
        data["completion"] = completion()
        self.assertEqual(CHECKS.report_write(data)["status"], "WithinReportScope")
        data["completion"]["checks"][0]["exit_code"] = 2
        self.assertEqual(CHECKS.report_write(data)["status"], "Deferred")

    def test_cli_gate_failure_returns_nonzero(self):
        data = completion(); data["checks"] = []
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "notion_checks.py"), "completion-gate", "--input", "-"], input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "NeedsCorrection")


if __name__ == "__main__":
    unittest.main()
