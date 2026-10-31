"""Persisted handoff, resend and failure regressions without external effects."""

import copy
import json
import unittest

from test_notion_checks import page, REPORT
import material_handoff as HANDOFF


def inputs():
    return {"root_id": "a" * 32, "email_task_id": REPORT, "content_version": "test-v1",
            "event": {"status": "Sent", "material": True, "provider": "gmail",
                      "account": "operator@example.com", "message_id": "sent-one",
                      "location_id": "location-one", "contact_id": "contact-one",
                      "context_key": "thread-one", "sent_at": "2026-11-02T00:00:00Z"},
            "cycle_query_complete": True, "cycles": [], "stop": False,
            "manual_pause": False, "recipient": "+61400000000",
            "channel_verified": True, "automatic_sms_enabled": True}


def cycle(data):
    r = HANDOFF.plan(data)["record"]
    return {k: r[k] for k in ("cycle_key", "location_id", "contact_id", "context_key")} | {
        "page_id": "d" * 32, "material_events": [r["event_key"]],
        "active": True, "total_count": 1, "unknown_attempt": False}


def saved(data, field="saved_cycle"):
    record = HANDOFF.plan(data)["record"]
    result = page("```json\n" + json.dumps(record) + "\n```")
    if field == "saved_cycle":
        result["id"] = "d" * 32
    return result


class MaterialHandoffTests(unittest.TestCase):
    def test_nonmaterial_reply_records_not_applicable_without_a_cycle_or_sms(self):
        data = inputs(); data['event']['material'] = False
        r = HANDOFF.plan(data)['record']
        self.assertEqual(r['state'], 'NotApplicable'); self.assertNotIn('cycle_key', r)
        result = HANDOFF.verify({'input': data, 'saved_email_task': saved(data, 'email')})
        self.assertEqual(result['status'], 'MaterialHandoffVerified'); self.assertIsNone(result['cycle_page_id'])
        data['event']['material'] = None
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_closed_unrelated_cycle_requires_manual_new_context_authorization(self):
        data = inputs(); c = cycle(data); c.update(active=False, context_key='old-thread', material_events=[])
        data['cycles'] = [c]
        self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Stopped')

    def test_actual_send_plans_one_registration_and_never_a_dispatch_or_cron(self):
        data = inputs(); before = copy.deepcopy(data)
        r = HANDOFF.plan(data)["record"]
        self.assertEqual(r["state"], "AwaitingSmsApproval")
        self.assertEqual(r["first_due_not_before"], "2026-11-02T00:30:00+00:00")
        self.assertFalse(r["create_native_task"]); self.assertFalse(r["customer_send_allowed"])
        self.assertEqual(data, before)

    def test_disabled_channel_or_missing_number_still_produces_observable_blocked_handoff(self):
        for field, value in (("recipient", None), ("channel_verified", False), ("automatic_sms_enabled", False)):
            data = inputs(); data[field] = value
            r = HANDOFF.plan(data)["record"]
            self.assertEqual(r["state"], "Blocked"); self.assertTrue(r["reasons"])

    def test_unknown_email_and_incomplete_discovery_do_not_enroll(self):
        for status in ("Unknown", "Draft", "Accepted"):
            data = inputs(); data["event"]["status"] = status
            with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); data["cycle_query_complete"] = False
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_same_event_and_resend_preserve_original_cycle_and_manual_ai_count(self):
        data = inputs(); existing = cycle(data); data["cycles"] = [existing]
        for message in ("sent-one", "sent-again"):
            data["event"]["message_id"] = message
            r = HANDOFF.plan(data)["record"]
            self.assertEqual(r["operation"], "reuse")
            self.assertEqual(r["cycle_key"], existing["cycle_key"]); self.assertEqual(r["total_count"], 1)

    def test_stop_pause_and_closed_or_capped_cycle_never_reopen(self):
        for field in ("stop", "manual_pause"):
            data = inputs(); data[field] = True
            self.assertEqual(HANDOFF.plan(data)["record"]["state"], "Stopped")
        for change in ({"active": False}, {"total_count": 2}):
            data = inputs(); c = cycle(data); c.update(change); data["cycles"] = [c]
            r = HANDOFF.plan(data)["record"]
            self.assertEqual(r["state"], "Stopped"); self.assertEqual(r["operation"], "reuse")

    def test_unknown_count_attempt_and_competing_cycles_require_reconciliation(self):
        for change in ({"total_count": None}, {"total_count": True}, {"unknown_attempt": True}):
            data = inputs(); c = cycle(data); c.update(change); data["cycles"] = [c]
            with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); data["cycles"] = [cycle(data), cycle(data)]
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_changed_context_or_version_does_not_change_provider_event_identity(self):
        data = inputs(); original = HANDOFF.plan(data)["record"]["event_key"]
        data["event"]["context_key"] = "new-context"
        self.assertEqual(HANDOFF.plan(data)["record"]["event_key"], original)

    def test_original_email_and_distinct_cycle_readback_are_required(self):
        data = inputs(); payload = {"input": data, "saved_email_task": saved(data, "email"), "saved_cycle": saved(data)}
        self.assertEqual(HANDOFF.verify(payload)["status"], "MaterialHandoffVerified")
        for field in ("saved_email_task", "saved_cycle"):
            changed = copy.deepcopy(payload); changed[field]["truncated"] = True
            with self.assertRaises(ValueError): HANDOFF.verify(changed)
            changed = copy.deepcopy(payload); changed[field]["text"] = changed[field]["text"].replace('AwaitingSmsApproval', 'Sent')
            with self.assertRaises(ValueError): HANDOFF.verify(changed)
        payload["saved_cycle"]["id"] = REPORT
        with self.assertRaises(ValueError): HANDOFF.verify(payload)

    def test_reuse_cannot_persist_to_a_duplicate_cycle_page(self):
        data = inputs(); data["cycles"] = [cycle(data)]
        payload = {"input": data, "saved_email_task": saved(data, "email"), "saved_cycle": saved(data)}
        self.assertEqual(HANDOFF.verify(payload)["status"], "MaterialHandoffVerified")
        payload["saved_cycle"]["id"] = "e" * 32
        with self.assertRaises(ValueError): HANDOFF.verify(payload)

    def test_display_markdown_and_naive_time_cannot_supply_source_identity(self):
        data = inputs(); data["event"]["contact_id"] = "[Customer](https://example.com)"
        with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); data["event"]["sent_at"] = "2026-11-02T00:00:00"
        with self.assertRaises(ValueError): HANDOFF.plan(data)
