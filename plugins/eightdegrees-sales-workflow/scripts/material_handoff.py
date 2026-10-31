#!/usr/bin/env python3
"""Plan and verify persisted email-to-SMS handoff; no connectors or sends."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id

SCOPE = "Offline normalized-evidence checks only; not provider verification, approval, a scheduler or an execution lock"


def token(value):
    if not isinstance(value, str) or not value or re.search(r'\s|[<>`\[\]()]', value):
        raise ValueError("Use an exact machine identity, not display Markdown")
    return value


def stamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Actual send time must include a timezone")
    return result.astimezone(timezone.utc)


def key(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def plan(data):
    event = data["event"]
    if event.get("status") != "Sent" or type(event.get("material")) is not bool:
        raise ValueError("Require actual Sent and an explicit material classification; reconcile unknown outcomes first")
    identity = {k: token(event[k]) for k in ("account", "provider", "message_id", "location_id", "contact_id", "context_key")}
    root, email = page_id(data["root_id"]), page_id(data["email_task_id"])
    if not all(re.fullmatch(r"[0-9a-f]{32}", x or "") for x in (root, email)):
        raise ValueError("Use the actual installation root and original email task IDs")
    sent_at = stamp(event["sent_at"])
    # Context/version updates do not change the actual provider-event identity.
    event_key = "material:" + key({"root": root, **{k: identity[k] for k in identity if k != "context_key"}})
    if event["material"] is False:
        return {"status": "MaterialHandoffPlanned", "record": {
            "contract": "material-handoff-v1", "event_key": event_key, "email_task_id": email,
            "content_version": token(data["content_version"]), "root_id": root, **identity,
            "sent_at": sent_at.isoformat(), "state": "NotApplicable", "material": False,
            "reason": "This verified reply did not deliver project materials; no SMS enrollment",
            "create_native_task": False, "customer_send_allowed": False}, "scope": SCOPE}
    if data.get("cycle_query_complete") is not True or not isinstance(data.get("cycles"), list):
        raise ValueError("Complete scoped cycle discovery is required before create/reuse")
    candidates = []
    for cycle in data["cycles"]:
        if cycle.get("location_id") != identity["location_id"] or cycle.get("contact_id") != identity["contact_id"]:
            raise ValueError("Cycle discovery must belong to this exact CRM customer")
        token(cycle["cycle_key"])
        if not re.fullmatch(r"[0-9a-f]{32}", page_id(cycle.get("page_id", "")) or ""):
            raise ValueError("Reuse requires the actual original cycle page identity before any write")
        if (type(cycle.get("total_count")) is not int or not 0 <= cycle["total_count"] <= 2
                or type(cycle.get("active")) is not bool or not isinstance(cycle.get("material_events"), list)
                or cycle.get("unknown_attempt") is not False):
            raise ValueError("Unknown attempt/count or malformed cycle requires reconciliation, never a new cycle")
        if (event_key in cycle["material_events"] or cycle.get("context_key") == identity["context_key"] or cycle["active"]):
            candidates.append(cycle)
    if len(candidates) > 1:
        raise ValueError("Ambiguous related/active cycles; do not reset or create another")
    existing = candidates[0] if candidates else None
    for field in ("stop", "manual_pause", "channel_verified", "automatic_sms_enabled"):
        if type(data.get(field)) is not bool:
            raise ValueError("Use an observed boolean for " + field)
    reasons = []
    stopped = data["stop"] or data["manual_pause"] or bool(existing and (not existing["active"] or existing["total_count"] >= 2))
    if data["cycles"] and existing is None:
        stopped = True
        reasons.append("Previous cycles exist; a different context requires explicit manual new-cycle authorization")
    if stopped:
        reasons.append("Customer stop, operator pause or closed/capped cycle; never reopen automatically")
    if not data.get("recipient"):
        reasons.append("Customer SMS number required")
    elif not re.fullmatch(r"\+[1-9][0-9]{7,14}", data["recipient"]):
        raise ValueError("Use a verified E.164 recipient or leave it missing")
    if not data["channel_verified"]:
        reasons.append("Own-number display, stable send and ordinary-inbox replies not verified")
    if not data["automatic_sms_enabled"]:
        reasons.append("Automatic SMS disabled; prepare only, do not silently enable")
    record = {"contract": "material-handoff-v1", "event_key": event_key,
              "material": True,
              "email_task_id": email, "content_version": token(data["content_version"]), "root_id": root, **identity,
              "sent_at": sent_at.isoformat(),
              "first_due_not_before": (sent_at + timedelta(minutes=30)).isoformat(),
              "cycle_key": existing["cycle_key"] if existing else "sms-cycle:" + key(event_key),
              "operation": "reuse" if existing else "create",
              "state": "Stopped" if stopped else "Blocked" if reasons else "AwaitingSmsApproval",
              "total_count": existing["total_count"] if existing else 0,
              "reasons": reasons, "recipient": data.get("recipient"),
              "executor": "shared-approved-work", "create_native_task": False,
              "customer_send_allowed": False}
    return {"status": "MaterialHandoffPlanned", "record": record, "scope": SCOPE}


def saved_record(capture, expected):
    payload = object_result(capture)
    if payload.get("metadata", {}).get("type") != "page":
        raise ValueError("Use the original saved page fetch")
    body = page_body(capture)
    matches = []
    for block in re.findall(r"```json\s*\n(.*?)\n```", body, re.S):
        value = json.loads(block)
        if isinstance(value, dict) and value.get("contract") == "material-handoff-v1" and value.get("event_key") == expected["event_key"]:
            matches.append(value)
    if matches != [expected]:
        raise ValueError("Missing, duplicated or changed saved handoff record")
    return page_id(payload["id"])


def verify(data):
    expected = plan(data["input"])["record"]
    email_id = saved_record(data["saved_email_task"], expected)
    cycle_id = saved_record(data["saved_cycle"], expected) if expected["material"] else None
    if email_id != expected["email_task_id"] or email_id == cycle_id:
        raise ValueError("Handoff must persist on the original email task and its distinct cycle page")
    if expected.get("operation") == "reuse":
        cycles = [c for c in data["input"]["cycles"] if c["cycle_key"] == expected["cycle_key"]]
        if len(cycles) != 1 or page_id(cycles[0].get("page_id", "")) != cycle_id:
            raise ValueError("Reuse must keep the original cycle page, not a duplicate")
    return {"status": "MaterialHandoffVerified", "entity_id": email_id, "cycle_page_id": cycle_id,
            "event_key": expected["event_key"], "state": expected["state"],
            "message_id": expected["message_id"], "content_version": expected["content_version"], "scope": SCOPE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "verify"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text()
        result = {"plan": plan, "verify": verify}[args.command](json.loads(raw))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)], "scope": SCOPE}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"MaterialHandoffPlanned", "MaterialHandoffVerified"} else 2


if __name__ == "__main__":
    sys.exit(main())
