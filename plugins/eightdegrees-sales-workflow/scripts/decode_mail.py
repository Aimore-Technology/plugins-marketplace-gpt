#!/usr/bin/env python3
"""Decode an already-authorized MIME message offline; never fetch, render or send."""
import argparse
import base64
import binascii
import codecs
import hashlib
import json
from email import policy
from email.header import decode_header
from email.parser import BytesParser
from pathlib import Path
import re
import sys


class MailDecodeError(ValueError):
    """The original bytes cannot be interpreted without guessing or data loss."""


def decode_bytes(data, declared):
    warnings = []
    charset = declared or ("ascii" if data.isascii() else "utf-8")
    if not declared and not data.isascii():
        warnings.append("Undeclared charset; strict UTF-8 used, not a detected charset.")
    try:
        codec = codecs.lookup(charset).name
        try:
            text = data.decode(codec, errors="strict")
        except UnicodeDecodeError:
            if codec not in {"gb2312", "gbk"}:
                raise
            codec = "gb18030"
            text = data.decode(codec, errors="strict")
            warnings.append("Declared GB2312/GBK failed; compatible GB18030 extension used.")
    except (LookupError, UnicodeError) as exc:
        raise MailDecodeError(f"Cannot strictly decode charset {charset!r}.") from exc
    if "\ufffd" in text or any(0xD800 <= ord(c) <= 0xDFFF for c in text):
        raise MailDecodeError("Decoded content contains replacement characters or surrogates.")
    return text, codec, warnings


def decode_header_value(value):
    result = []
    for part, charset in decode_header(str(value or "")):
        if isinstance(part, bytes):
            part = decode_bytes(part, charset)[0]
        if "\ufffd" in part or any(0xD800 <= ord(c) <= 0xDFFF for c in part):
            raise MailDecodeError("Header contains undecodable characters.")
        result.append(part)
    return "".join(result)


def decode_message(raw):
    if not raw or len(raw) > 10 * 1024 * 1024:
        raise MailDecodeError("Expected a nonempty MIME message of at most 10 MiB.")
    message = BytesParser(policy=policy.compat32).parsebytes(raw)
    if not message.keys():
        raise MailDecodeError("Missing MIME message headers.")
    bodies, skipped = [], []

    def visit(part, path):
        content_type = part.get_content_type()
        # Do not descend into attached emails or decode attachment payloads.
        if part.get_content_disposition() == "attachment" or part.get_filename():
            skipped.append({"path": path, "content_type": content_type})
            return
        if part.defects:
            raise MailDecodeError(f"Malformed MIME structure at {path}.")
        if content_type.startswith("multipart/") and part.is_multipart():
            for index, child in enumerate(part.get_payload()):
                visit(child, f"{path}.{index}")
            return
        if content_type not in {"text/plain", "text/html"}:
            skipped.append({"path": path, "content_type": content_type})
            return
        transfer = (part.get("Content-Transfer-Encoding") or "7bit").strip().lower()
        if transfer not in {"7bit", "8bit", "binary", "base64", "quoted-printable"}:
            raise MailDecodeError(f"Unsupported transfer encoding at {path}.")
        if transfer == "quoted-printable" and re.search(
            r"=(?![0-9A-Fa-f]{2}|\r?\n)", part.get_payload()
        ):
            raise MailDecodeError(f"Malformed quoted-printable body at {path}.")
        payload = part.get_payload(decode=True)
        if payload is None or part.defects:
            raise MailDecodeError(f"Malformed transfer encoding at {path}.")
        if transfer == "7bit" and not payload.isascii():
            raise MailDecodeError(f"Non-ASCII bytes declared as 7bit at {path}.")
        declared = part.get_content_charset()
        text, used, warnings = decode_bytes(payload, declared)
        bodies.append({"path": path, "content_type": content_type,
                       "declared_charset": declared, "used_charset": used,
                       "transfer_encoding": transfer, "text": text,
                       "warnings": warnings})

    visit(message, "0")
    if not bodies:
        raise MailDecodeError("No supported, readable inline text body.")
    return {"status": "Decoded", "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "headers": {name: decode_header_value(message.get(name)) for name in
                        ("Subject", "From", "To", "Date", "Message-ID")},
            "bodies": bodies, "skipped_parts": skipped}


def decode_gmail(data, expected_id=None):
    if not isinstance(data, dict) or not isinstance(data.get("raw"), str):
        raise MailDecodeError("Expected a Gmail object with a raw base64url string.")
    if expected_id is not None and data.get("id") != expected_id:
        raise MailDecodeError("Gmail immutable message ID does not match the requested source.")
    encoded = re.sub(r"\s+", "", data["raw"])
    if not re.fullmatch(r"[A-Za-z0-9_-]*={0,2}", encoded):
        raise MailDecodeError("Invalid Gmail base64url alphabet.")
    try:
        raw = base64.b64decode(encoded + "=" * (-len(encoded) % 4),
                               altchars=b"-_", validate=True)
    except (ValueError, binascii.Error) as exc:
        raise MailDecodeError("Invalid Gmail base64url payload.") from exc
    result = decode_message(raw)
    result["gmail_message_id"] = data.get("id")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="Authorized input file, or - for stdin")
    parser.add_argument("--input-format", choices=("gmail-json", "eml"), default="gmail-json")
    parser.add_argument("--expected-id", help="Verify the immutable Gmail ID in gmail-json input")
    args = parser.parse_args()
    try:
        data = sys.stdin.buffer.read(10 * 1024 * 1024 + 1) if args.input == "-" else Path(args.input).read_bytes()
        if len(data) > 10 * 1024 * 1024:
            raise MailDecodeError("Input exceeds 10 MiB.")
        if args.input_format == "gmail-json":
            result = decode_gmail(json.loads(data), args.expected_id)
        else:
            if args.expected_id:
                raise MailDecodeError("Use gmail-json input to verify a Gmail immutable ID.")
            result = decode_message(data)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, LookupError, UnicodeError) as exc:
        print(json.dumps({"status": "NeedsManualReview", "error": str(exc)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
