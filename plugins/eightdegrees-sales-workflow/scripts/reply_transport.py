#!/usr/bin/env python3
"""Offline Gmail stored-draft preparation/verification; no connector calls or sends."""

import argparse
import base64
import hashlib
import json
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
from pathlib import Path
import re
import sys

from notion_checks import object_result


def b64url(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]*={0,2}", value):
        raise ValueError("Expected exact base64url bytes")
    return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)


def manifest(data):
    m = data["manifest"]
    required = ("task_page_id", "content_version", "draft_id", "message_id", "thread_id",
                "reply_message_id", "parent_rfc_message_id", "from_address", "to", "subject", "html_base64url", "html_sha256")
    if isinstance(m, dict):
        for key in ("from_address", "to", "cc", "bcc", "reply_to", "subject", "parent_rfc_message_id"):
            if key in m and not isinstance(m[key], str):
                raise ValueError(key + " must be a header string, not a list or null; use the current connector contract")
    if not isinstance(m, dict) or any(not isinstance(m.get(k), str) or not m[k] for k in required):
        raise ValueError("Missing original draft/message/thread/version/target/HTML binding")
    if m.get("assets") or m.get("attachments"):
        raise ValueError("This adapter verifies one HTML part only; frozen multipart assets require a separately verified adapter, never drop them")
    for key in ("from_address", "to", "cc", "bcc", "reply_to", "subject", "parent_rfc_message_id"):
        if any(c in m.get(key, "") for c in "\r\n"):
            raise ValueError("Header injection or malformed header")
    if not re.fullmatch(r"<[^<>\s]+>", m["parent_rfc_message_id"]):
        raise ValueError("Expected the actual original RFC Message-ID")
    html = b64url(m["html_base64url"])
    html.decode("utf-8", errors="strict")
    if not html or hashlib.sha256(html).hexdigest() != m["html_sha256"]:
        raise ValueError("Frozen HTML digest mismatch; preserve exact bytes including trailing newline")
    return m, html


def prepare(data):
    m, html = manifest(data)
    return {"status": "DraftPatchPlanned", "args": {"draft_id": m["draft_id"],
            "from_address": m["from_address"], "to": m["to"], "cc": m.get("cc", ""), "bcc": m.get("bcc", ""),
            "reply_to": m.get("reply_to", ""),
            "subject": m["subject"], "payload": {"mime_type": "text/html", "charset": "UTF-8",
            "body": {"base64_url_content": base64.urlsafe_b64encode(html).decode().rstrip("=")}},
            "response_fields": ["id", "message"]},
            "scope": "Use current update_draft contract; reply_message_id is deliberately omitted to preserve existing reply context; not approval or sending"}


def addresses(message, header):
    values = message.get_all(header, [])
    parsed = getaddresses([str(v) for v in values])
    return sorted(address.casefold() for _, address in parsed if address)


def expected_addresses(value):
    return sorted(address.casefold() for _, address in getaddresses([value]) if address)


def verify(data):
    m, html = manifest(data)
    raw = object_result(data["message"])
    phase = data.get("phase", "draft")
    if phase not in {"draft", "sent"}:
        raise ValueError("Expected draft or sent verification phase")
    issues = []
    expected_id = m["message_id"] if phase == "draft" else data.get("sent_message_id")
    if not expected_id or raw.get("id") != expected_id or raw.get("thread_id", raw.get("threadId")) != m["thread_id"]:
        issues.append("Wrong or missing original message/thread identity")
    if not isinstance(raw.get("label_ids", raw.get("labelIds")), list):
        issues.append("Missing actual message labels")
    else:
        labels = raw.get("label_ids", raw.get("labelIds"))
        if phase == "draft" and "DRAFT" not in labels or phase == "sent" and "SENT" not in labels:
            issues.append("Message is not in the expected draft/sent state")
    if phase == "draft":
        draft = object_result(data["draft"])
        child = draft.get("message", {})
        if draft.get("id", draft.get("draft_id")) != m["draft_id"] or child.get("id", child.get("message_id")) != m["message_id"]:
            issues.append("Stored draft ID to current message ID mapping changed")
    encoded = raw.get("raw")
    if not isinstance(encoded, str):
        raise ValueError("Actual raw MIME readback required; normalized full text is not exact byte proof")
    msg = BytesParser(policy=policy.default).parsebytes(b64url(encoded))
    if msg.defects or msg.is_multipart() or msg.get_content_type() != "text/html":
        issues.append("Malformed or unexpected MIME tree; HTML-only adapter cannot omit additional parts")
    if msg.get_content_charset() not in {"utf-8", "UTF-8"}:
        issues.append("Unexpected HTML charset")
    for field, expected in (("From", m["from_address"]), ("To", m["to"]), ("Cc", m.get("cc", "")), ("Bcc", m.get("bcc", "")), ("Reply-To", m.get("reply_to", ""))):
        if addresses(msg, field) != expected_addresses(expected):
            issues.append("Changed " + field + " address set")
    if len(msg.get_all("Subject", [])) != 1 or str(msg.get("Subject", "")) != m["subject"]:
        issues.append("Changed or duplicated subject")
    if len(msg.get_all("In-Reply-To", [])) != 1 or str(msg.get("In-Reply-To", "")).strip() != m["parent_rfc_message_id"]:
        issues.append("Changed or missing In-Reply-To")
    refs = " ".join(str(x) for x in msg.get_all("References", []))
    if m["parent_rfc_message_id"] not in re.findall(r"<[^<>\s]+>", refs):
        issues.append("Missing parent References header")
    payload = msg.get_payload(decode=True)
    if payload != html or msg.defects:
        issues.append("Decoded HTML differs from frozen approved bytes, including any appended quote/newline")
    binding = {k: m.get(k, "") for k in ("task_page_id", "content_version", "draft_id", "message_id", "thread_id", "reply_message_id",
        "parent_rfc_message_id", "from_address", "to", "cc", "bcc", "reply_to", "subject", "html_sha256")}
    return {"status": "NeedsCorrection" if issues else "StoredReplyVerified", "issues": issues,
            "entity_id": m["task_page_id"], "draft_id": m["draft_id"], "message_id": raw.get("id"),
            "thread_id": m["thread_id"], "content_version": m["content_version"], "phase": phase,
            "html_sha256": m["html_sha256"],
            "draft_binding_sha256": hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "scope": "Raw stored message/headers/exact HTML only; separate pre-dispatch approval/latest-reply/window/attempt checks; no recipient verification is required"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = (prepare if args.command == "prepare" else verify)(json.loads(source))
        print(json.dumps(result, ensure_ascii=True))
        return 2 if result["status"] == "NeedsCorrection" else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"status": "NeedsCorrection", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
