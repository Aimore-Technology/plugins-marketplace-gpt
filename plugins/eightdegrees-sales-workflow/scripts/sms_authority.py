#!/usr/bin/env python3
"""Check standing notification authority and exact saved SMS; never send."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id

INTENTS = {"material_receipt", "follow_up_notice", "appointment_reminder", "operator_alert"}
SCOPE = "Offline standing-policy/payload check only; not provider access, timing, stop coverage or permission to ignore invocation limits"


def prepare(data):
    authority, payload = data["authority"], data["payload"]
    if (authority.get("policy") != "notification-sms-v1" or authority.get("enabled") is not True
            or authority.get("revoked_at") is not None or authority.get("per_message_review_required") is not False):
        raise ValueError("Current standing notification authority is disabled, revoked or missing")
    for field in ("root_id", "operator_id"):
        if not authority.get(field) or authority[field] != payload.get(field):
            raise ValueError("SMS authority belongs to another installation/operator")
    if data.get("invocation_policy") not in {"one-cycle-approved-work", "scheduled-approved-work", "owner-workflow"}:
        raise ValueError("This invocation cannot send SMS, including through a helper")
    intent = payload.get("intent")
    if intent not in INTENTS or intent not in authority.get("allowed_intents", []):
        raise ValueError("Standing authority covers factual notifications only")
    role = "operator" if intent == "operator_alert" else "customer"
    if payload.get("recipient_role") != role:
        raise ValueError("Notification intent and recipient role differ")
    for field in ("recipient", "sender_number"):
        if not isinstance(payload.get(field), str) or not re.fullmatch(r"\+[1-9][0-9]{7,14}", payload[field]):
            raise ValueError("Use actual E.164 sender and recipient numbers")
    if role == "operator" and payload["recipient"] != authority.get("operator_sms_number"):
        raise ValueError("Internal alerts may use only the configured operator destination")
    if payload["sender_number"] != authority.get("sender_number") or payload.get("device_id") != authority.get("device_id") or not payload.get("device_id"):
        raise ValueError("Use the configured actual sending number/device")
    if (not payload.get("content_version") or not payload.get("source_refs") or not isinstance(payload["source_refs"], list)
            or any(not isinstance(x, str) or not x.strip() for x in payload["source_refs"])):
        raise ValueError("Freeze an exact version and original factual source references")
    body = payload.get("body")
    if not isinstance(body, str) or not body.strip() or body != body.strip():
        raise ValueError("Freeze the exact nonempty notification text before dispatch")
    if payload.get("facts_verified") is not True:
        raise ValueError("Notification claims require current factual source verification")
    identity = page_id(payload.get("task_id", ""))
    if not re.fullmatch(r"[a-f0-9]{32}", identity or ""):
        raise ValueError("Use the original notification task page")
    # Body generation/edits are permitted under standing authority. This binds
    # exactly what will be sent, without pretending to approve its business facts.
    record = {"contract": "sms-notification-v1", **{k: payload[k] for k in (
        "root_id", "operator_id", "task_id", "content_version", "intent", "recipient_role",
        "recipient", "sender_number", "device_id", "body", "source_refs", "facts_verified")},
        "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "authority_policy": authority["policy"], "requires_human_review": False}
    return {"status": "SMSNotificationPrepared", "record": record, "scope": SCOPE}


def verify(data):
    record = prepare(data)["record"]
    payload = object_result(data["saved_task"])
    if payload.get("metadata", {}).get("type") != "page" or page_id(payload["id"]) != page_id(record["task_id"]):
        raise ValueError("Read the actual original notification task")
    found = []
    for block in re.findall(r"```json\s*\n(.*?)\n```", page_body(data["saved_task"]), re.S):
        value = json.loads(block)
        if isinstance(value, dict) and value.get("contract") == "sms-notification-v1":
            found.append(value)
    if found != [record]:
        raise ValueError("Current saved notification differs, is duplicated or is missing")
    dispatch = data.get("dispatch")
    if dispatch is not None and dispatch != {k: record[k] for k in ("recipient", "device_id", "body")}:
        raise ValueError("Actual proposed provider payload differs from the frozen notification")
    return {"status": "SMSNotificationVerified", "entity_id": payload["id"],
            "content_version": record["content_version"], "body_sha256": record["body_sha256"],
            "authority_policy": record["authority_policy"], "scope": SCOPE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text()
        result = {"prepare": prepare, "verify": verify}[args.command](json.loads(raw))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)], "scope": SCOPE}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"SMSNotificationPrepared", "SMSNotificationVerified"} else 2


if __name__ == "__main__":
    sys.exit(main())
