"""Realistic stored-draft adapter fixtures; no network or actual sends."""

import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("reply_transport", SCRIPTS / "reply_transport.py")
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)
HTML = b"<!doctype html>\n<html><body><p>Approved TEST reply.</p></body></html>\n"


def encoded(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def fixture(html=HTML):
    m = {"task_page_id": "a" * 32, "content_version": "reply-v2", "draft_id": "r-draft-1",
         "message_id": "message-2", "thread_id": "thread-1", "reply_message_id": "source-1",
         "parent_rfc_message_id": "<original@example.invalid>", "from_address": "sender@example.invalid",
         "to": "receiver@example.invalid", "subject": "Re: TEST inquiry", "html_base64url": encoded(HTML),
         "html_sha256": hashlib.sha256(HTML).hexdigest()}
    raw = ("From: sender@example.invalid\r\nTo: receiver@example.invalid\r\nSubject: Re: TEST inquiry\r\n"
           "In-Reply-To: <original@example.invalid>\r\nReferences: <original@example.invalid>\r\n"
           "Content-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n").encode() + base64.b64encode(html)
    return {"manifest": m, "draft": {"id": "r-draft-1", "message": {"id": "message-2"}},
            "message": {"id": "message-2", "thread_id": "thread-1", "label_ids": ["DRAFT"], "raw": encoded(raw)}}


class ReplyTransportTests(unittest.TestCase):
    def test_header_lists_null_and_nonstring_values_are_refused_before_payload(self):
        for key in ("from_address", "to", "cc", "bcc", "reply_to", "subject", "parent_rfc_message_id"):
            for value in (["receiver@example.invalid"], None, 42):
                with self.subTest(key=key, value=value):
                    data = fixture(); data["manifest"][key] = value
                    with self.assertRaisesRegex(ValueError, "header string"):
                        ADAPTER.prepare(data)

    def test_prepare_replaces_mime_without_resetting_reply_context(self):
        planned = ADAPTER.prepare(fixture())
        args = planned["args"]
        self.assertEqual(args["draft_id"], "r-draft-1")
        self.assertNotIn("reply_message_id", args)
        self.assertEqual(ADAPTER.b64url(args["payload"]["body"]["base64_url_content"]), HTML)
        self.assertEqual((args["cc"], args["bcc"], args["reply_to"]), ("", "", ""))

    def test_raw_stored_draft_matches_approved_body_and_thread(self):
        result = ADAPTER.verify(fixture())
        self.assertEqual(result["status"], "StoredReplyVerified")
        self.assertEqual(result["phase"], "draft")
        self.assertEqual(len(result["draft_binding_sha256"]), 64)

    def test_added_quote_is_not_accepted_as_an_exact_prefix_match(self):
        data = fixture(HTML + b'<div class="gmail_quote">Original inquiry</div>')
        result = ADAPTER.verify(data)
        self.assertEqual(result["status"], "NeedsCorrection")
        self.assertTrue(any("Decoded HTML" in x for x in result["issues"]))

    def test_fake_stored_draft_replacement_flow_removes_quote_before_review(self):
        data = fixture(HTML + b"quote automatically added by create_draft")
        self.assertEqual(ADAPTER.verify(data)["status"], "NeedsCorrection")
        patch = ADAPTER.prepare(data)["args"]
        exact = ADAPTER.b64url(patch["payload"]["body"]["base64_url_content"])
        saved = fixture(exact)
        self.assertEqual(ADAPTER.verify(saved)["status"], "StoredReplyVerified")
        # Same existing draft sent, with no body reconstruction: simulate only raw readback state.
        saved.update(phase="sent", sent_message_id="sent-1")
        saved["message"].update(id="sent-1", label_ids=["SENT"])
        self.assertEqual(ADAPTER.verify(saved)["status"], "StoredReplyVerified")

    def test_stale_draft_message_thread_and_state_bindings_are_rejected(self):
        for key, value in (("id", "other-message"), ("thread_id", "other-thread"), ("label_ids", ["SENT"])):
            data = fixture(); data["message"][key] = value
            self.assertEqual(ADAPTER.verify(data)["status"], "NeedsCorrection")
        data = fixture(); data["draft"]["id"] = "other-draft"
        self.assertEqual(ADAPTER.verify(data)["status"], "NeedsCorrection")

    def test_sender_recipient_subject_and_reply_headers_cannot_change(self):
        for old, new in ((b"sender@example.invalid", b"other@example.invalid"),
                         (b"receiver@example.invalid", b"other@example.invalid"),
                         (b"Subject: Re: TEST inquiry", b"Subject: Edited subject"),
                         (b"original@example.invalid", b"other-parent@example.invalid")):
            data = fixture(); raw = ADAPTER.b64url(data["message"]["raw"]).replace(old, new)
            data["message"]["raw"] = encoded(raw)
            self.assertEqual(ADAPTER.verify(data)["status"], "NeedsCorrection")

    def test_extra_recipient_headers_and_missing_raw_proof_are_rejected(self):
        data = fixture(); data["message"]["raw"] = encoded(b"Cc: extra@example.invalid\r\n" + ADAPTER.b64url(data["message"]["raw"]))
        self.assertEqual(ADAPTER.verify(data)["status"], "NeedsCorrection")
        data = fixture(); del data["message"]["raw"]
        with self.assertRaises(ValueError):
            ADAPTER.verify(data)

    def test_no_newline_normalization_or_unapproved_byte_changes(self):
        for html in (HTML.rstrip(b"\n"), HTML + b"\n", HTML.replace(b"\n", b"\r\n")):
            self.assertEqual(ADAPTER.verify(fixture(html))["status"], "NeedsCorrection")
        data = fixture(); data["manifest"]["html_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            ADAPTER.prepare(data)

    def test_frozen_assets_are_not_silently_dropped_by_html_only_adapter(self):
        data = fixture(); data["manifest"]["assets"] = [{"id": "image-1"}]
        with self.assertRaises(ValueError):
            ADAPTER.prepare(data)

    def test_failed_tool_envelope_and_header_injection_refuse(self):
        data = fixture(); data["message"] = {"isError": True, "structuredContent": data["message"]}
        with self.assertRaises(ValueError):
            ADAPTER.verify(data)
        data = fixture(); data["manifest"]["subject"] = "subject\r\nBcc: other@example.invalid"
        with self.assertRaises(ValueError):
            ADAPTER.prepare(data)

    def test_current_raw_mcp_envelope_is_supported(self):
        data = fixture()
        data["message"] = {"isError": False, "structuredContent": None,
                           "content": [{"type": "text", "text": json.dumps(data["message"])}]}
        self.assertEqual(ADAPTER.verify(data)["status"], "StoredReplyVerified")

    def test_cli_mismatch_has_nonzero_exit_without_sending(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "reply_transport.py"), "verify", "--input", "-"],
                                input=json.dumps(fixture(HTML + b"quote")), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "NeedsCorrection")


if __name__ == "__main__":
    unittest.main()
