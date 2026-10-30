"""Offline normalized native-scheduler contracts; no actual scheduled tasks."""

import copy
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts/schedule_checks.py"
SPEC = importlib.util.spec_from_file_location("schedule_checks", PATH)
SCHEDULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCHEDULE)


def request(operation="start"):
    return {"operation": operation, "context": {"root_id": "a" * 32,
        "root_url": "https://app.notion.com/p/" + "a" * 32, "operator_id": "operator-local-demo",
        "mailbox": "operator@example.com", "provider": "native-demo", "account_id": "native-account",
        "host_id": "native-host", "runtime": "work-gpt-task", "timezone": "Australia/Adelaide", "generation": 1},
        "capabilities": {k: True for k in ("list", "read", "create", "update", "delete", "runner_ready", "exact_15_minutes")},
        "tasks": [], "list_complete": True, "list_includes_inactive": True}


def actual_task(data, identity="native-task-1"):
    ctx = SCHEDULE.context(data)
    return {"id": identity, "prompt": SCHEDULE.prompt_for(ctx), "enabled": True,
            "interval_minutes": 15, "timezone": ctx["timezone"], "read_verified": True,
            **{k: ctx[k] for k in ("provider", "account_id", "host_id", "runtime")}}


def scheduled_guard():
    data = request(); ctx = SCHEDULE.context(data)
    data.update(trigger="scheduled", invocation={"schedule_id": "native-task-1", "invocation_id": "scan-invocation-1"},
                setup={"operator_id": ctx["operator_id"], "gmail_account": ctx["mailbox"], "notion_root_id": ctx["root_id"]},
                scheduling={"enabled": True, "state": "Running", "desired_state": "Running", "generation": 1,
                            "owner_key": ctx["owner_key"], "provider": ctx["provider"], "account_id": ctx["account_id"],
                            "owner_host": ctx["host_id"], "runtime": ctx["runtime"], "approved_work_enabled": True,
                            "schedule_ids": ["native-task-1"]})
    return data


class ScheduleTests(unittest.TestCase):
    def test_stop_before_first_start_accepts_verified_absence_at_generation_zero(self):
        data = request("stop"); data["context"]["generation"] = 0
        self.assertEqual(SCHEDULE.plan(data)["status"], "AlreadyAbsent")
        self.assertEqual(SCHEDULE.verify(data)["status"], "StoppedVerified")

    def test_unknown_create_and_ui_pending_cannot_be_mistaken_for_verified_stop(self):
        for status in ("Unknown", "Pending", "WaitingForConfirmation"):
            data = request("stop"); data["pending_attempt"] = {"status": status}
            self.assertEqual(SCHEDULE.plan(data)["status"], "NeedsReconciliation")
            self.assertEqual(SCHEDULE.verify(data)["status"], "NeedsReconciliation")

    def test_known_created_task_recovers_projection_without_another_create(self):
        data = request(); data["pending_attempt"] = {"status": "Accepted"}
        data["tasks"] = [actual_task(data)]
        self.assertEqual(SCHEDULE.plan(data)["status"], "NeedsReconciliation")
        self.assertEqual(SCHEDULE.verify(data)["status"], "RunningVerified")

    def test_plan_is_not_running_and_contains_one_cycle_prompt(self):
        data = request(); result = SCHEDULE.plan(data)
        self.assertEqual(result["status"], "EligibleForNativeCreate")
        self.assertNotIn("@eightdegrees-sales-workflow run-auto", result["prompt"])
        self.assertIn("scheduled-approved-work", result["prompt"])
        self.assertEqual(result["interval_minutes"], 15)
        self.assertEqual(data["tasks"], [])

    def test_start_readback_and_repeat_reuse_real_id(self):
        data = request(); data["tasks"] = [actual_task(data)]
        self.assertEqual(SCHEDULE.verify(data)["status"], "RunningVerified")
        result = SCHEDULE.plan(data)
        self.assertEqual((result["status"], result["schedule_id"]), ("ReuseExisting", "native-task-1"))

    def test_paused_or_changed_owned_task_updates_instead_of_duplicate(self):
        for field, value in [("enabled", False), ("interval_minutes", 60), ("prompt", "changed")]:
            data = request(); item = actual_task(data)
            if field == "prompt": value = item["prompt"] + "\nChanged instructions"
            item[field] = value; data["tasks"] = [item]
            self.assertEqual(SCHEDULE.plan(data)["status"], "EligibleForNativeUpdate")
            self.assertEqual(SCHEDULE.verify(data)["status"], "NeedsCorrection")

    def test_unsupported_cadence_or_runner_does_not_create_fallback(self):
        for field in ("exact_15_minutes", "runner_ready", "read", "list"):
            data = request(); data["capabilities"][field] = False
            self.assertEqual(SCHEDULE.plan(data)["status"], "NativeSchedulingUnavailable")

    def test_incomplete_listing_cannot_prove_absence(self):
        for field in ("list_complete", "list_includes_inactive"):
            data = request("stop"); data[field] = False
            with self.assertRaises(ValueError): SCHEDULE.verify(data)

    def test_unknown_create_or_delete_never_gets_another_mutation(self):
        for operation in ("start", "stop"):
            data = request(operation); data["pending_attempt"] = {"status": "Unknown", "attempt_id": "attempt-1"}
            self.assertEqual(SCHEDULE.plan(data)["status"], "NeedsReconciliation")

    def test_duplicate_scanners_block_start_and_are_exact_stop_targets(self):
        data = request(); data["tasks"] = [actual_task(data), actual_task(data, "native-task-2")]
        self.assertEqual(SCHEDULE.plan(data)["status"], "NeedsReconciliation")
        data["operation"] = "stop"
        self.assertEqual(SCHEDULE.plan(data)["schedule_ids"], ["native-task-1", "native-task-2"])

    def test_title_only_unrelated_schedule_is_never_a_stop_target(self):
        data = request("stop"); unrelated = actual_task(data, "unrelated")
        unrelated.update(name="EightDegrees scan", prompt="A completely different workflow.")
        data["tasks"] = [actual_task(data), unrelated]
        self.assertEqual(SCHEDULE.plan(data)["schedule_ids"], ["native-task-1"])

    def test_marker_drift_on_registered_id_is_not_already_stopped(self):
        data = request("stop"); item = actual_task(data); item["prompt"] = "Changed task"
        data.update(tasks=[item], scheduling={"schedule_ids": [item["id"]]})
        with self.assertRaises(ValueError): SCHEDULE.verify(data)

    def test_stop_requires_real_absence_not_a_paused_task_or_local_false(self):
        data = request("stop"); item = actual_task(data); item["enabled"] = False
        data.update(tasks=[item], scheduling={"enabled": False})
        self.assertEqual(SCHEDULE.verify(data)["status"], "NeedsCorrection")
        data["tasks"] = []
        self.assertEqual(SCHEDULE.verify(data)["status"], "StoppedVerified")
        self.assertEqual(SCHEDULE.plan(data)["status"], "AlreadyAbsent")

    def test_missing_delete_cannot_claim_native_deletion(self):
        data = request("stop"); data["tasks"] = [actual_task(data)]; data["capabilities"]["delete"] = False
        self.assertEqual(SCHEDULE.plan(data)["status"], "NativeDeletionUnavailable")

    def test_saved_different_executor_blocks_second_schedule_even_if_list_empty(self):
        data = request(); data["scheduling"] = {"enabled": True, "provider": "other", "owner_host": "other", "account_id": "other"}
        self.assertEqual(SCHEDULE.plan(data)["status"], "NeedsReconciliation")

    def test_owned_native_task_wrong_account_is_not_adopted_or_deleted(self):
        data = request("stop"); item = actual_task(data); item["account_id"] = "other"
        data["tasks"] = [item]
        with self.assertRaises(ValueError): SCHEDULE.plan(data)

    def test_scheduled_guard_rejects_stop_stale_wrong_task_and_changed_setup(self):
        data = scheduled_guard()
        self.assertEqual(SCHEDULE.guard(data)["status"], "EligibleForScheduledCycle")
        for field, value in [("enabled", False), ("desired_state", "Stopped"), ("state", "StopRequested"),
                             ("generation", 2), ("generation", True), ("owner_host", "other")]:
            changed = copy.deepcopy(data); changed["scheduling"][field] = value
            self.assertEqual(SCHEDULE.guard(changed)["status"], "Deferred")
        for field in ("operator_id", "gmail_account", "notion_root_id"):
            changed = copy.deepcopy(data); changed["setup"][field] = "changed"
            self.assertEqual(SCHEDULE.guard(changed)["status"], "Deferred")
        data["invocation"]["schedule_id"] = "unrelated"
        self.assertEqual(SCHEDULE.guard(data)["status"], "Deferred")

    def test_busy_tick_defers_but_manual_cycle_remains_available_when_stopped(self):
        data = scheduled_guard(); data["active_run"] = {"status": "InProgress", "invocation_id": "another-run"}
        self.assertEqual(SCHEDULE.guard(data)["status"], "Deferred")
        data["trigger"] = "manual"; data["scheduling"]["enabled"] = False
        self.assertEqual(SCHEDULE.guard(data), {"status": "EligibleForManualCycle", "customer_send_allowed": False})

    def test_work_and_cowork_guards_never_enable_legacy_no_send_jobs(self):
        for runtime in ('work-gpt-task', 'cowork-cron-task'):
            data = scheduled_guard(); data['context']['runtime'] = data['scheduling']['runtime'] = runtime
            result = SCHEDULE.guard(data)
            self.assertEqual(result['policy'], 'scheduled-approved-work'); self.assertTrue(result['customer_send_allowed'])
            del data['scheduling']['approved_work_enabled']
            self.assertEqual(SCHEDULE.guard(data)['status'], 'Deferred')

    def test_wrong_runtime_does_not_take_over_a_different_executor(self):
        data = scheduled_guard(); data['scheduling']['runtime'] = 'cowork-cron-task'
        self.assertEqual(SCHEDULE.guard(data)['status'], 'Deferred')
