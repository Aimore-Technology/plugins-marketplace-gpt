"""Synthetic MIME regressions; no connectors, credentials or live account writes."""
import base64
from email.header import Header
import importlib.util
import json
from pathlib import Path
import quopri
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts/decode_mail.py"
SPEC = importlib.util.spec_from_file_location("decode_mail", SCRIPT)
decoder = importlib.util.module_from_spec(SPEC)
sys.dont_write_bytecode = True
SPEC.loader.exec_module(decoder)
TEXT = "\u6d4b\u8bd5\u8be2\u76d8\uff1a\u9700\u8981\u4e09\u95f4\u5367\u5ba4\uff0c\u9884\u7b97 800,000 AUD\u3002"


def message(text=TEXT, charset="gb2312", transfer="base64", encoded_charset=None):
    payload = text.encode(encoded_charset or charset)
    if transfer == "base64":
        payload = base64.b64encode(payload)
    elif transfer == "quoted-printable":
        payload = quopri.encodestring(payload)
    return (f"From: test@example.com\r\nTo: recipient@example.com\r\n"
            f"Subject: {Header(TEXT, 'utf-8').encode()}\r\nMIME-Version: 1.0\r\n"
            f"Content-Type: text/plain; charset={charset}\r\n"
            f"Content-Transfer-Encoding: {transfer}\r\n\r\n").encode("ascii") + payload


def gmail(raw):
    return {"id": "synthetic-message-1", "raw": base64.urlsafe_b64encode(raw).decode().rstrip("=")}


class MimeRecoveryTests(unittest.TestCase):
    def test_chinese_gb2312_base64_is_lossless(self):
        result = decoder.decode_gmail(gmail(message()), "synthetic-message-1")
        self.assertEqual(result["status"], "Decoded")
        self.assertEqual(result["bodies"][0]["text"], TEXT)
        self.assertEqual(result["headers"]["Subject"], TEXT)
        self.assertEqual(result["bodies"][0]["used_charset"], "gb2312")
        self.assertEqual(len(result["raw_sha256"]), 64)

    def test_gb18030_extension_is_recorded(self):
        text = TEXT + "\U00020000"
        part = decoder.decode_message(message(text, encoded_charset="gb18030"))["bodies"][0]
        self.assertEqual(part["text"], text)
        self.assertEqual(part["declared_charset"], "gb2312")
        self.assertEqual(part["used_charset"], "gb18030")
        self.assertTrue(part["warnings"])

    def test_utf8_and_gbk_quoted_printable(self):
        for charset in ("utf-8", "gbk"):
            with self.subTest(charset=charset):
                result = decoder.decode_message(message(charset=charset, transfer="quoted-printable"))
                self.assertEqual(result["bodies"][0]["text"], TEXT)

    def test_alternative_plain_and_html_bodies_are_kept_separate(self):
        plain = message(charset="utf-8").split(b"\r\n\r\n", 1)[1]
        raw = (b'MIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary="b"\r\n\r\n'
               b'--b\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n'
               + plain + b'\r\n--b\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<p>Test</p>\r\n--b--\r\n')
        result = decoder.decode_message(raw)
        self.assertEqual([p["content_type"] for p in result["bodies"]], ["text/plain", "text/html"])
        self.assertEqual(result["bodies"][0]["text"], TEXT)
        self.assertIn("<p>Test</p>", result["bodies"][1]["text"])

    def test_attached_email_is_not_traversed_or_decoded(self):
        raw = (b'MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary="b"\r\n\r\n'
               b'--b\r\nContent-Type: text/plain\r\n\r\nVisible body\r\n'
               b'--b\r\nContent-Type: message/rfc822\r\nContent-Disposition: attachment; filename="secret.eml"\r\n\r\n'
               b'Subject: private attachment\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n\xff\xfe\r\n--b--\r\n')
        result = decoder.decode_message(raw)
        self.assertEqual(len(result["bodies"]), 1)
        self.assertEqual(result["bodies"][0]["text"], "Visible body")
        self.assertEqual(len(result["skipped_parts"]), 1)
        self.assertNotIn("private attachment", json.dumps(result))

    def test_bad_inputs_are_rejected_instead_of_repaired(self):
        cases = [
            message(charset="utf-8").replace(b"charset=utf-8", b"charset=unknown-test-charset"),
            message(charset="utf-8").replace(b"Content-Transfer-Encoding: base64", b"Content-Transfer-Encoding: unsupported"),
            message().split(b"\r\n\r\n", 1)[0] + b"\r\n\r\n%%%%",
            message(transfer="quoted-printable") + b"=ZZ",
            message("\ufffd", charset="utf-8"),
            message(charset="utf-8", transfer="8bit").replace(b"charset=utf-8", b"charset=ascii"),
            b"not an email",
            b'MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary="missing"\r\n\r\nTest',
        ]
        for index, raw in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(decoder.MailDecodeError):
                decoder.decode_message(raw)

    def test_source_id_and_outer_base64_are_checked(self):
        with self.assertRaises(decoder.MailDecodeError):
            decoder.decode_gmail(gmail(message()), "different-message")
        for raw in ("%%%", "A", "QQ=Q", "QQ==="):
            with self.subTest(raw=raw), self.assertRaises(decoder.MailDecodeError):
                decoder.decode_gmail({"raw": raw})

    def test_declared_charset_does_not_fall_back_to_arbitrary_encoding(self):
        with self.assertRaises(decoder.MailDecodeError):
            decoder.decode_bytes(b"\xff", "utf-8")

    def test_ascii_undeclared_body(self):
        result = decoder.decode_message(b"Subject: Test\r\n\r\nASCII body")
        self.assertEqual(result["bodies"][0]["text"], "ASCII body")

    def test_cli_outputs_readable_body_and_failure_has_no_partial_body(self):
        good = subprocess.run([sys.executable, str(SCRIPT), "--expected-id", "synthetic-message-1"],
                              input=json.dumps(gmail(message())).encode(), capture_output=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["bodies"][0]["text"], TEXT)
        bad = subprocess.run([sys.executable, str(SCRIPT)], input=b'{"raw":"%%%"}', capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(json.loads(bad.stdout)["status"], "NeedsManualReview")
        self.assertNotIn("bodies", json.loads(bad.stdout))


if __name__ == "__main__":
    unittest.main()
