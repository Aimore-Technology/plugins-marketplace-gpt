"""Failure/order regressions using captured-shape fixtures, never live services."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from test_notion_checks import source_schema, PARENT, CHECKS
from test_reply_transport import fixture, SCRIPTS
from fixtures_intake import handoff

SPEC = importlib.util.spec_from_file_location("execution_preflight", SCRIPTS / "execution_preflight.py")
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)
RUN, TASK, ACTION, HTML, IMAGE = [c * 32 for c in "12345"]


def request():
    return {"owner_skill": "eightdegrees-sales-reply", "policy": "draft-only", "operation": "content",
            "invocation_id": "synthetic-invocation", "publication_version": "reply-v2",
            "facts": {"finance_status": "unconfirmed", "finance_approved": None}, "intake_handoff": handoff(),
            "resources": [{"role": "run", "type": "run", "entity_id": RUN},
                          {"role": "review", "type": "task", "entity_id": TASK, "content_version": "reply-v2", "resume_step": "ReviewReplyDraft"},
                          {"role": "review-input", "type": "action", "entity_id": ACTION, "task_role": "review"}],
            "notion_rows": [{"role": "run", "data_source": source_schema(), "data_source_id": PARENT,
                             "properties": {"Status": "Saved"}}]}


def capture(prepared, identity=RUN):
    saved = {k: prepared[k] for k in ("execution_plan", "plan_sha256")}
    return {"id": identity, "metadata": {"type": "page"},
            "text": '<properties>'+json.dumps(prepared['execution_plan'].get('run_properties', {}))+'</properties>\n<content>\n## Execution plan\n\n```json\n' + json.dumps(saved) + '\n```\n</content>'}


class ExecutionPreflightTests(unittest.TestCase):
    def test_automatic_execution_cannot_prepare_an_initialization_owner(self):
        for policy in ('one-cycle-approved-work', 'scheduled-approved-work'):
            with self.assertRaisesRegex(ValueError, 'Owner conflicts'):
                PREFLIGHT.prepare({'owner_skill': 'eightdegrees-initialization', 'policy': policy, 'operation': 'setup'})

    def test_original_fact_refusal_stops_before_schema_and_returns_no_plan(self):
        data = request(); data["facts"]["finance_status"] = "Undecided"
        with patch.object(PREFLIGHT, "schema_values") as schema:
            result = PREFLIGHT.prepare(data)
        schema.assert_not_called()
        self.assertEqual(result["status"], "NeedsCorrection")
        self.assertEqual(result["checks"][-1]["exit_code"], 2)
        self.assertNotIn("execution_plan", result)
        self.assertNotIn("outputs", result)

    def test_valid_canonical_output_keeps_unknown_null_and_input_intact(self):
        data = request(); before = copy.deepcopy(data)
        result = PREFLIGHT.prepare(data)
        self.assertEqual(result["status"], "PreflightPrepared")
        self.assertEqual(result["outputs"]["facts"], {"finance_status": "Not confirmed", "finance_approved": None})
        self.assertEqual(data, before)
        data["facts"]["finance_approved"] = False
        self.assertEqual(PREFLIGHT.prepare(data)["status"], "NeedsCorrection")

    def test_missing_facts_for_content_projection_cannot_prepare(self):
        data = request(); del data["facts"]
        with self.assertRaises(ValueError):
            PREFLIGHT.prepare(data)

    def test_unknown_status_or_wrong_source_prevents_plan(self):
        for field, value in [("properties", {"Status": "NeedsData"}), ("data_source_id", "f" * 32)]:
            data = request(); data["notion_rows"][0][field] = value
            self.assertEqual(PREFLIGHT.prepare(data)["status"], "NeedsCorrection")

    def test_property_write_outside_declared_roles_is_rejected(self):
        data = request(); data["notion_rows"][0]["role"] = "another-owner"
        with self.assertRaises(ValueError):
            PREFLIGHT.prepare(data)

    def test_required_coverage_is_generated_instead_of_caller_handwritten_checks(self):
        result = PREFLIGHT.prepare(request())
        kinds = {s["kind"] for s in result["execution_plan"]["required_checks"].values()}
        self.assertEqual(kinds, {"page-links", "route", "task-display", "reply-draft", "task-summary"})
        self.assertEqual(len(result["execution_plan"]["required_checks"]), 7)

    def test_missing_action_task_or_multiple_owner_runs_cannot_prepare(self):
        for edit in (lambda rs: rs.pop(), lambda rs: rs[2].update(task_role="absent"),
                     lambda rs: rs.append({"role": "child-run", "type": "run"})):
            data = request(); edit(data["resources"])
            with self.assertRaises(ValueError):
                PREFLIGHT.prepare(data)

    def test_ready_uses_actual_persisted_run_and_resolves_unchanged_plan(self):
        prepared = PREFLIGHT.prepare(request())
        result = PREFLIGHT.ready({"prepared": prepared, "saved_plan": capture(prepared)})
        self.assertEqual(result["status"], "ExecutionPlanReady")
        self.assertEqual(result["registry"]["action_bindings"], {ACTION: TASK})
        self.assertEqual(result["registry"]["task_versions"], {TASK: "reply-v2"})
        self.assertEqual(result["registry"]["required_checks"]["review-input:task-display"]["entity_id"], ACTION)

    def test_actual_mcp_envelope_with_metadata_page_readback_is_supported(self):
        prepared = PREFLIGHT.prepare(request()); saved = capture(prepared)
        wrapped = {"content": [{"type": "text", "text": json.dumps(saved)}],
                   "structuredContent": saved, "isError": False}
        self.assertEqual(PREFLIGHT.ready({"prepared": prepared, "saved_plan": wrapped})["status"], "ExecutionPlanReady")

    def test_unknown_precheck_type_cannot_pass_with_missing_success_status(self):
        prepared = PREFLIGHT.prepare(request())
        prepared["execution_plan"]["prechecks"][0]["kind"] = "unsupported"
        prepared["checks"][0]["kind"] = "unsupported"
        prepared["checks"][0]["result"] = {}
        hashed = PREFLIGHT.digest({})
        prepared["execution_plan"]["prechecks"][0]["result_sha256"] = hashed
        prepared["checks"][0]["result_sha256"] = hashed
        prepared["plan_sha256"] = PREFLIGHT.digest(prepared["execution_plan"])
        with self.assertRaisesRegex(ValueError, "Preflight is failed"):
            PREFLIGHT.ready({"prepared": prepared, "saved_plan": capture(prepared)})

    def test_declared_new_id_slots_resolve_without_rewriting_frozen_plan(self):
        data = request(); data["resources"][1]["entity_id"] = None
        prepared = PREFLIGHT.prepare(data); saved = capture(prepared)
        with self.assertRaises(ValueError):
            PREFLIGHT.ready({"prepared": prepared, "saved_plan": saved})
        result = PREFLIGHT.ready({"prepared": prepared, "saved_plan": saved, "bindings": {"review": TASK}})
        self.assertEqual(result["status"], "ExecutionPlanReady")
        self.assertIsNone(prepared["execution_plan"]["resources"][1]["entity_id"])

    def test_existing_id_replacement_and_undeclared_binding_are_rejected(self):
        prepared = PREFLIGHT.prepare(request())
        for bindings in ({"review": HTML}, {"new-child": HTML}, {"run": TASK}):
            with self.assertRaises(ValueError):
                PREFLIGHT.ready({"prepared": prepared, "saved_plan": capture(prepared), "bindings": bindings})

    def test_late_added_dependency_cannot_match_the_original_saved_plan(self):
        prepared = PREFLIGHT.prepare(request()); saved = capture(prepared)
        plan = prepared["execution_plan"]
        plan["resources"].append({"role": "new-html", "type": "html-preview", "entity_id": HTML})
        plan["required_checks"] = PREFLIGHT.compile_checks(plan["resources"])
        prepared["plan_sha256"] = PREFLIGHT.digest(plan)
        with self.assertRaisesRegex(ValueError, "saved plan"):
            PREFLIGHT.ready({"prepared": prepared, "saved_plan": saved})

    def test_digest_only_duplicate_or_other_run_page_is_not_saved_plan_proof(self):
        prepared = PREFLIGHT.prepare(request())
        saved = capture(prepared)
        duplicate = copy.deepcopy(saved)
        duplicate["text"] = saved["text"].replace("\n</content>", "\n" + PREFLIGHT.page_body(saved) + "\n</content>")
        digest_only = copy.deepcopy(saved); digest_only["text"] = prepared["plan_sha256"]
        for candidate in (capture(prepared, TASK), duplicate, digest_only):
            with self.assertRaises(ValueError):
                PREFLIGHT.ready({"prepared": prepared, "saved_plan": candidate})

    def test_truncated_failed_or_nonpage_capture_is_rejected(self):
        prepared = PREFLIGHT.prepare(request())
        for mutation in ({"truncated": True}, {"isError": True}, {"metadata": {"type": "database"}}):
            saved = capture(prepared); saved.update(mutation)
            with self.assertRaises(ValueError):
                PREFLIGHT.ready({"prepared": prepared, "saved_plan": saved})

    def test_missing_or_changed_precheck_result_blocks_ready(self):
        prepared = PREFLIGHT.prepare(request()); saved = capture(prepared)
        for mutation in (lambda cs: cs.pop(), lambda cs: cs[0].update(exit_code=False),
                         lambda cs: cs[0]["result"].update(status="NeedsCorrection"),
                         lambda cs: cs[0]["result"].update(facts={"finance_approved": False})):
            changed = copy.deepcopy(prepared); mutation(changed["checks"])
            with self.assertRaises(ValueError):
                PREFLIGHT.ready({"prepared": changed, "saved_plan": saved})

    def test_same_html_version_image_and_transport_evidence_are_in_plan(self):
        data = request(); data["resources"].extend([
            {"role": "html", "type": "html-preview", "entity_id": HTML},
            {"role": "png", "type": "image-preview", "entity_id": IMAGE,
             "content_version": "reply-v2", "html_sha256": "a" * 64}])
        data["resources"][1]["evidence"] = ["reply-draft"]
        prepared = PREFLIGHT.prepare(data)
        checks = PREFLIGHT.ready({"prepared": prepared, "saved_plan": capture(prepared)})["registry"]["required_checks"]
        self.assertEqual(checks["png:preview-image"]["html_sha256"], "a" * 64)
        self.assertEqual(checks["review:reply-draft"]["entity_id"], TASK)

    def test_canonical_outputs_cannot_change_after_preparation(self):
        prepared = PREFLIGHT.prepare(request()); saved = capture(prepared)
        prepared["outputs"]["facts"]["finance_approved"] = False
        with self.assertRaisesRegex(ValueError, "outputs changed"):
            PREFLIGHT.ready({"prepared": prepared, "saved_plan": saved})

    def test_completion_plan_evidence_is_bound_to_original_digest_and_phase(self):
        prepared = PREFLIGHT.prepare(request())
        ready = PREFLIGHT.ready({"prepared": prepared, "saved_plan": capture(prepared)})
        spec = ready["registry"]["required_checks"]["execution-plan"]
        data = {"invocation_id": ready["invocation_id"], "publication_version": ready["publication_version"],
                "required_checks": {"plan": spec}, "checks": [{"name": "plan", "invocation_id": ready["invocation_id"],
                    "publication_version": ready["publication_version"], "exit_code": 0, "result": ready}]}
        self.assertEqual(CHECKS.completion_gate(data)["status"], "EligibleForCompletion")
        for key, changed in [("execution_plan_sha256", "f" * 64), ("invocation_id", "later-run"),
                             ("publication_version", "later-version"), ("entity_id", TASK)]:
            invalid = copy.deepcopy(data); invalid["checks"][0]["result"][key] = changed
            self.assertEqual(CHECKS.completion_gate(invalid)["status"], "NeedsCorrection")

    def test_wrong_recipient_type_is_rejected_before_patch_arguments_are_exposed(self):
        data = request(); data.update(operation="reply-patch", reply=fixture())
        data["reply"]["manifest"]["to"] = ["receiver@example.invalid"]
        result = PREFLIGHT.prepare(data)
        self.assertEqual(result["status"], "NeedsCorrection")
        self.assertNotIn("outputs", result)
        data["reply"]["manifest"]["to"] = "receiver@example.invalid"
        result = PREFLIGHT.prepare(data)
        self.assertIsInstance(result["outputs"]["reply_args"]["to"], str)
        self.assertNotIn("reply_message_id", result["outputs"]["reply_args"])

    def test_cli_failure_is_nonzero_with_no_usable_plan(self):
        data = request(); data["facts"]["finance_status"] = "Undecided"
        result = subprocess.run([sys.executable, str(SCRIPTS / "execution_preflight.py"), "prepare", "--input", "-"],
                                input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("execution_plan", json.loads(result.stdout))

    def test_cli_prepare_then_persisted_readback_ready(self):
        command = [sys.executable, str(SCRIPTS / "execution_preflight.py")]
        result = subprocess.run(command + ["prepare", "--input", "-"], input=json.dumps(request()), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        prepared = json.loads(result.stdout)
        result = subprocess.run(command + ["ready", "--input", "-"], input=json.dumps({"prepared": prepared, "saved_plan": capture(prepared)}),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "ExecutionPlanReady")


if __name__ == "__main__":
    unittest.main()
