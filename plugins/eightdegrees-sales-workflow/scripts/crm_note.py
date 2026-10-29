#!/usr/bin/env python3
"""Render/validate a complete plain-text CRM note offline; never call a connector."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


TEMPLATE_VERSION = "aimore-crm-note-v1"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets/crm-note-v1.txt"
FIELDS = {
    "template_version", "communication_id", "content_version", "communication_time",
    "timezone", "source_url", "location_id", "contact_id", "customer_name", "sections",
}
SECTIONS = ("context_background", "action", "recommendation", "next_schedule")
UNKNOWN = {"not provided", "to confirm", "unknown", "null", "none", "n/a"}
MARKUP = re.compile(
    r"`|\*\*|__|!?\[[^\]\n]*\]\([^\n)]*\)|"
    r"</?[A-Za-z][\w:-]*(?:\s[^>]*)?/?>|"
    r"^(?:#{1,6}\s|>\s|[-*+]\s|\d+[.)]\s|\|)|"
    r"(?<!\w)(?:\*[^*\s][^*]*\*|_[^_\s][^_]*_)(?!\w)"
)
EXECUTION_TERMS = re.compile(
    r"(?<![A-Za-z0-9_])(?:Manual\s+continue|RunSettings|Communications|PendingTasks|WorkflowRuns|"
    r"OperationLogs|OwnerSkill|ResumeStep|TaskId|AttemptId|InputSubmitted|MCP|TestHarness)(?![A-Za-z0-9_])|"
    r"add-communication|one-cycle-no-customer-send|\[TEST\]|\u6d4b\u8bd5\u8054\u7cfb\u4eba", re.I
)


def plain(value, label, allow_unknown=True, check_markup=True):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: required non-empty text")
    if value != value.strip() or any(ord(c) < 32 or ord(c) == 127 or c in "\u0085\u2028\u2029" for c in value):
        raise ValueError(f"{label}: use one plain-text line without surrounding whitespace")
    if (check_markup and MARKUP.search(value)) or "{{" in value or "}}" in value:
        raise ValueError(f"{label}: markup or unresolved placeholder is not allowed")
    if not allow_unknown and value.casefold() in UNKNOWN:
        raise ValueError(f"{label}: a verified value is required")
    return value


def render(payload):
    if not isinstance(payload, dict) or set(payload) != FIELDS:
        raise ValueError("payload: supply exactly the documented header fields and sections")
    if payload["template_version"] != TEMPLATE_VERSION:
        raise ValueError("template_version: unsupported template")
    values = {k: plain(v, k, k in {"communication_time", "customer_name"}, k == "customer_name")
              for k, v in payload.items() if k != "sections"}
    for key in FIELDS - {"sections", "source_url", "customer_name", "communication_time"}:
        if re.search(r"[\s`*#<>\[\]{}|\\]", values[key]):
            raise ValueError(f"{key}: use an unformatted identifier")
    url = urlsplit(values["source_url"])
    if url.scheme != "https" or not url.hostname or url.username or url.password or re.search(r"\s|[<>`{}]", values["source_url"]):
        raise ValueError("source_url: use the verified HTTPS original source/page URL")
    try:
        timezone = ZoneInfo(values["timezone"])
    except ZoneInfoNotFoundError as exc:
        raise ValueError("timezone: a known IANA timezone is required") from exc
    time_text = values["communication_time"]
    if time_text != "Not provided":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{2}:\d{2}", time_text):
            raise ValueError("communication_time: use ISO 8601 with seconds and numeric offset, or Not provided")
        instant = datetime.fromisoformat(time_text)
        if instant.utcoffset() != instant.astimezone(timezone).utcoffset():
            raise ValueError("communication_time: offset does not match the stated timezone at this instant")
    sections = payload["sections"]
    if not isinstance(sections, dict) or set(sections) != set(SECTIONS):
        raise ValueError("sections: all four standard sections are required")
    for key in SECTIONS:
        items = sections[key]
        if not isinstance(items, list) or not items:
            raise ValueError(f"{key}: at least one plain-text bullet is required")
        if key != "context_background" and any(isinstance(item, str) and EXECUTION_TERMS.search(item) for item in items):
            raise ValueError(f"{key}: use business actions and next steps; execution details belong in Notion logs")
        values[key] = "\n".join("- " + plain(item, key) for item in items)
    return TEMPLATE.read_text(encoding="utf-8").format(**values).encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    make = modes.add_parser("render")
    make.add_argument("--input", required=True)
    make.add_argument("--output", help="Optional plain-text note file; otherwise return note in JSON")
    check = modes.add_parser("validate")
    check.add_argument("--input", required=True)
    check.add_argument("--note", required=True)
    check.add_argument("--expected-sha256")
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        note = render(json.loads(source))
        digest = hashlib.sha256(note).hexdigest()
        if args.mode == "validate":
            if Path(args.note).read_bytes() != note:
                raise ValueError("note: bytes differ from the complete standard payload; revise and reapprove")
            if args.expected_sha256 is not None and args.expected_sha256 != digest:
                raise ValueError("note: approved digest mismatch; do not append")
        result = {"status": "Valid", "template_version": TEMPLATE_VERSION, "sha256": digest, "bytes": len(note)}
        if args.mode == "render":
            if args.output:
                # Preserve an existing file instead of overwriting any prior approved version.
                with Path(args.output).open("xb") as output:
                    output.write(note)
                result["output"] = args.output
            else:
                result["note"] = note.decode("utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({"status": "NeedsCorrection", "reason": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
