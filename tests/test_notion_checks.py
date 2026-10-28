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
    return {"id": REPORT, "text": '<page>\n<properties>{"title":"Test"}</properties>\n<content>\n' + text + '\n</content>\n</page>'}


def preview(text=None):
    return {"page": page(text if text is not None else f'<embed source="file-upload://{FILE}" />'),
            "html_file_id": FILE, "html_sha256": hashlib.sha256(HTML.encode()).hexdigest(),
            "download": {"file_upload_id": FILE, "content_type": "text/html; charset=utf-8", "content": HTML}}


def write(tool="notion_notion_update_page", **args):
    return {"registry": {"report_page_ids": [REPORT], "report_run_page_ids": [RUN],
                         "operation_log_source_ids": [LOGS]},
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


if __name__ == "__main__":
    unittest.main()
