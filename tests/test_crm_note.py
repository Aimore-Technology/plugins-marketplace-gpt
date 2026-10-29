"""Behavioral regressions for missing/markup Notes and approved-byte integrity."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts/crm_note.py"
SPEC = importlib.util.spec_from_file_location("crm_note", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def payload():
    return {
        "template_version": "aimore-crm-note-v1",
        "communication_id": "test@example.com:inbound:message__1",
        "content_version": "notes-v1",
        "communication_time": "2026-10-28T22:33:11+10:30",
        "timezone": "Australia/Adelaide",
        "source_url": "https://www.notion.so/test__source",
        "location_id": "test-location",
        "contact_id": "test-contact",
        "customer_name": "Test Customer",
        "sections": {
            "context_background": ["Source-backed preference: three bedrooms."],
            "action": ["Customer matched; no message sent."],
            "recommendation": ["AI suggestion, pending: verify source."],
            "next_schedule": ["Owner: configured operator; time: Not provided."],
        },
    }


class CRMNoteTests(unittest.TestCase):
    def test_execution_terms_in_business_sections_are_rejected_before_review(self):
        for section in ("action", "recommendation", "next_schedule"):
            for value in ("Saved RunSettings after Manual continue.", "Use the Communications archive.",
                          "Resume PendingTasks using the MCP result.",
                          "\u539f\u6765\u6e90\u53caRunSettings\u5df2\u5e94\u7528\u5e76\u56de\u8bfb\u3002",
                          "Matched a CRM \u6d4b\u8bd5\u8054\u7cfb\u4eba."):
                data = payload(); data["sections"][section] = [value]
                with self.subTest(section=section, value=value), self.assertRaises(ValueError):
                    MODULE.render(data)

    def test_genuine_source_quote_and_business_follow_up_remain_plain_text(self):
        data = payload()
        data["sections"]["context_background"] = ["Customer quoted a document named RunSettings in the original inquiry."]
        data["sections"]["action"] = ["Clarified that the purchase-price cap excludes acquisition costs."]
        data["sections"]["recommendation"] = ["AI suggestion, pending: ask the sales desk to verify current availability."]
        data["sections"]["next_schedule"] = ["Operator to request a Tuesday viewing slot; time unconfirmed; no appointment booked."]
        self.assertIn(b"time unconfirmed", MODULE.render(data))

    def test_complete_plain_text_preserves_literal_ids_and_unicode(self):
        data = payload()
        data["sections"]["context_background"].append("\u5ba2\u6237\u504f\u597d\uff1a\u4e09\u5367\u3002")
        note = MODULE.render(data).decode("utf-8")
        for key in ("CommunicationTime:", "Timezone:", "LocationId:", "ContactId:", "Customer:"):
            self.assertIn(key, note)
        self.assertIn(data["communication_id"], note)
        self.assertIn(data["source_url"], note)
        self.assertIn(data["sections"]["context_background"][-1], note)
        self.assertNotIn("```", note)

    def test_every_header_is_required(self):
        for key in payload().keys() - {"sections"}:
            with self.subTest(key=key):
                data = payload()
                del data[key]
                with self.assertRaises(ValueError):
                    MODULE.render(data)

    def test_missing_empty_or_extra_section_rejected(self):
        for key in MODULE.SECTIONS:
            for value in ([], "unstructured prose", [""]):
                data = payload()
                data["sections"][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    MODULE.render(data)
        data = payload()
        data["sections"]["persona"] = ["Unreviewed extra section"]
        with self.assertRaises(ValueError):
            MODULE.render(data)

    def test_prose_markup_is_not_written_to_notes(self):
        examples = ["**bold**", "*italic*", "_italic_", "`code`", "## Heading", "[source](https://example.com)",
                    "<b>rich</b>", "| a | b |", "- nested bullet", "> quote", "1. nested list", "{{missing}}"]
        for value in examples:
            with self.subTest(value=value):
                data = payload()
                data["sections"]["action"] = [value]
                with self.assertRaises(ValueError):
                    MODULE.render(data)

    def test_header_and_bullet_line_injection_rejected(self):
        for key in ("customer_name", "contact_id", "source_url"):
            data = payload()
            data[key] = "value\nContactId: other"
            with self.subTest(key=key), self.assertRaises(ValueError):
                MODULE.render(data)
        data = payload()
        data["sections"]["action"] = ["First\u2028Second"]
        with self.assertRaises(ValueError):
            MODULE.render(data)

    def test_unknown_time_is_explicit_but_identity_is_required(self):
        data = payload()
        data["communication_time"] = "Not provided"
        data["customer_name"] = "Not provided"
        self.assertIn(b"CommunicationTime: Not provided", MODULE.render(data))
        for key in ("contact_id", "location_id", "source_url", "communication_id"):
            bad = copy.deepcopy(data)
            bad[key] = "Not provided"
            with self.subTest(key=key), self.assertRaises(ValueError):
                MODULE.render(bad)

    def test_original_instant_needs_numeric_offset_matching_dst(self):
        for text in ("2026-10-28T12:03:11Z", "2026-10-28T12:03:11", "2026-10-28T22:33:11+09:30"):
            data = payload()
            data["communication_time"] = text
            with self.subTest(text=text), self.assertRaises(ValueError):
                MODULE.render(data)
        data = payload()
        data["communication_time"] = "2026-06-28T21:33:11+09:30"
        MODULE.render(data)

    def test_unknown_timezone_and_non_source_url_rejected(self):
        for key, value in (("timezone", "Not/AZone"), ("source_url", "http://project-v1.md"),
                           ("source_url", "https://user:password@example.com")):
            data = payload()
            data[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                MODULE.render(data)

    def run_cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_render_then_validate_approved_bytes_and_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, note = root / "input.json", root / "note.txt"
            source.write_text(json.dumps(payload()), encoding="utf-8")
            code, result = self.run_cli("render", "--input", source, "--output", note)
            self.assertEqual(code, 0)
            digest = result["sha256"]
            self.assertEqual(digest, hashlib.sha256(note.read_bytes()).hexdigest())
            code, _ = self.run_cli("validate", "--input", source, "--note", note, "--expected-sha256", digest)
            self.assertEqual(code, 0)
            code, _ = self.run_cli("validate", "--input", source, "--note", note, "--expected-sha256", "0" * 64)
            self.assertEqual(code, 2)
            note.write_bytes(note.read_bytes() + b"\nUnapproved change")
            code, result = self.run_cli("validate", "--input", source, "--note", note)
            self.assertEqual((code, result["status"]), (2, "NeedsCorrection"))

    def test_invalid_input_creates_no_note_and_existing_version_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, note = root / "input.json", root / "note.txt"
            source.write_text("{}", encoding="utf-8")
            code, _ = self.run_cli("render", "--input", source, "--output", note)
            self.assertEqual(code, 2)
            self.assertFalse(note.exists())
            source.write_text(json.dumps(payload()), encoding="utf-8")
            note.write_bytes(b"Existing approved bytes")
            code, _ = self.run_cli("render", "--input", source, "--output", note)
            self.assertEqual(code, 2)
            self.assertEqual(note.read_bytes(), b"Existing approved bytes")


if __name__ == "__main__":
    unittest.main()
