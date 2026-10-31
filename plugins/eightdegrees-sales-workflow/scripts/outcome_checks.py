#!/usr/bin/env python3
"""Check normalized observed task/send results offline; no tools, writes or approval."""

import argparse
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id

STATES = {"WaitingForOperator", "NeedsCorrection", "ReadyToValidate", "InProgress", "Completed", "Cancelled"}
PROVIDER_STATES = {"Sent", "SentToNetwork", "Delivered", "ProviderAccepted", "AwaitingPhone", "PendingApproval", "Failed", "Unknown"}


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing observed " + name)
    return value


def task_state(data):
    original, candidate = data["original"], data.get("candidate")
    identity = required_text(original.get("id"), "task id")
    if original.get("read_verified") is not True or original.get("state") not in STATES:
        raise ValueError("Read the registered original task before checking state")
    if candidate is not None and (candidate.get("id") != identity or candidate.get("state") != original["state"]):
        return {"status": "NeedsReconciliation", "entity_id": identity, "execute_allowed": False,
                "observed_original_state": original["state"], "reason": "Candidate and original task conflict; preserve both observations, do not reopen or dispatch"}
    terminal = original["state"] in {"Completed", "Cancelled"}
    return {"status": "Deferred" if terminal else "CurrentStateVerified", "entity_id": identity,
            "execute_allowed": not terminal, "observed_original_state": original["state"],
            "scope": "Observed state only; approval, versions, ownership and prior attempts remain separate checks"}


def projection(data):
    result = data["provider"]
    if result.get("read_verified") is not True or result.get("status") not in PROVIDER_STATES:
        raise ValueError("Actual provider result/status evidence is required")
    identity = required_text(data.get("task_id"), "task id")
    version = required_text(data.get("content_version"), "approved content version")
    message = required_text(result.get("message_id"), "provider message id")
    operation = result.get("operation")
    if operation not in {"email", "sms"} or operation == "sms" and result["status"] == "Sent":
        raise ValueError("Normalize actual email/SMS status without upgrading its evidence")
    network = result["status"] in {"Sent", "SentToNetwork", "Delivered"}
    receipt = data.get("human_receipt") or {}
    received = receipt.get("received") is True
    if received and (receipt.get("message_id") != message or not receipt.get("source")):
        raise ValueError("Human receipt must identify this exact provider message and its source")
    expected = {"message_id": message, "provider_status": result["status"], "sent": network,
                "reserved": result["status"] in {"Unknown", "AwaitingPhone", "ProviderAccepted", "PendingApproval"},
                "provider_delivered": result["status"] == "Delivered", "human_received": received,
                "sender_display": receipt.get("sender_display") if received else None}
    return {"status": "OutcomeDerived", "entity_id": identity, "content_version": version, "expected": expected,
            "scope": "Current result projection only; preserve approved payloads and historical pre-send snapshots"}


def verify_projection(data):
    derived = projection(data)
    expected = derived["expected"]
    surfaces = data.get("saved")
    if not isinstance(surfaces, dict) or not {"task", "index", "action_result"} <= surfaces.keys():
        raise ValueError("Read back current task, lightweight index and active action result")
    display = current_display(data)
    issues = list(display["issues"])
    for name, observed in surfaces.items():
        if not isinstance(observed, dict) or observed.get("read_verified") is not True:
            issues.append(name + ": current saved readback missing")
            continue
        if observed.get("task_id") != derived["entity_id"] or observed.get("content_version") != derived["content_version"]:
            issues.append(name + ": original task or approved version differs")
        for field, value in expected.items():
            if observed.get(field) != value:
                issues.append(name + ": " + field + " differs from verified outcome")
    return {"status": "NeedsCorrection" if issues else "OutcomeProjectionsVerified",
            "entity_id": derived["entity_id"], "content_version": derived["content_version"],
            "action_page_id": display["action_page_id"], "expected": expected, "issues": issues,
            "scope": "Offline readback comparison; repair projections only, never repeat the provider operation"}


def current_display(data):
    """Check the actual action copy, not only caller-normalized result fields."""
    derived = projection(data)
    page = object_result(data["action_page"])
    action_id = data["action_page_id"]
    if page.get("metadata", {}).get("type") != "page" or page_id(page["id"]) != page_id(action_id):
        raise ValueError("Read the registered original action page")
    body = page_body(data["action_page"])
    sections = re.split(r"(?m)^##[ \t]+([^\n]+)\n", body)
    groups = {"status": [], "result": []}
    for heading, text in zip(sections[1::2], sections[2::2]):
        name = heading.strip().lower()
        if name in {"current status", "\u5f53\u524d\u72b6\u6001"}:
            groups["status"].append(text)
        elif name in {"processing result", "\u5904\u7406\u7ed3\u679c"}:
            groups["result"].append(text)
    issues = []
    if any(len(v) != 1 for v in groups.values()):
        issues.append("Missing/duplicate current status or processing result section")
    current = "\n".join(text for values in groups.values() for text in values)
    other = (r"\u77ed\u4fe1(?:\u5c1a?\u672a\u53d1\u9001|\u987b\u72ec\u7acb\u5ba1\u6279)|SMS\s+(?:not sent|pending approval)"
             if data["provider"]["operation"] == "email" else r"\u90ae\u4ef6(?:\u5c1a?\u672a\u53d1\u9001|\u987b\u72ec\u7acb\u5ba1\u6279)|email\s+not sent")
    if re.search(other, current, re.I):
        issues.append("Current copy must stay channel-local; other-channel claims become stale")
    unknown = r"(?:\u5b9e\u9645\u6536\u4ef6\u5c1a\u672a\u6838\u9a8c|\u6536\u4ef6\u4eba\u5c1a\u672a\u6536\u5230|recipient (?:receipt|delivery) (?:is )?(?:unverified|not verified))"
    for paragraph in re.split(r"\n\s*\n", current):
        if re.search(unknown, paragraph, re.I):
            if derived["expected"]["human_received"] or not re.search(
                    r"(?:as of|observed|\u622a\u81f3|\u8bb0\u5f55\u4e8e|\u53d1\u9001\u65f6).*?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", paragraph, re.I | re.S):
                issues.append("Undated or contradicted current non-receipt claim; use an evidence-time snapshot or source link")
    if derived["expected"]["message_id"] not in current or derived["expected"]["provider_status"] not in current:
        issues.append("Current result must identify this verified provider message and status")
    return {"status": "NeedsCorrection" if issues else "CurrentOutcomeDisplayVerified",
            "entity_id": derived["entity_id"], "action_page_id": action_id, "issues": issues,
            "scope": "Current owned sections only; historical snapshots/approved content unchanged; limited text patterns"}


def counts(data):
    """Count current verified outcomes, not duplicate logs or history snapshots."""
    if not isinstance(data.get("events"), list) or type(data.get("coverage_complete")) is not bool:
        raise ValueError("Supply current outcome observations and explicit coverage completeness")
    unique = {}
    for event in data["events"]:
        fields = projection(event)["expected"]
        account = required_text(event.get("account"), "source account")
        key = (event["provider"]["operation"], account, fields["message_id"])
        if key in unique and unique[key] != fields:
            return {"status": "NeedsReconciliation", "reason": "Conflicting current results for one provider message; do not publish invented totals"}
        unique[key] = fields
    return {"status": "OutcomeCountsDerived", "email_sent": sum(v["sent"] for k, v in unique.items() if k[0] == "email"),
            "sms_sent": sum(v["sent"] for k, v in unique.items() if k[0] == "sms"),
            "reserved": sum(v["reserved"] for v in unique.values()),
            "unknown": sum(v["provider_status"] == "Unknown" for v in unique.values()),
            "coverage_complete": data["coverage_complete"],
            "scope": "Complete supplied scope" if data["coverage_complete"] else "Known supplied outcomes only; global counts/absence unverified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("task", "project", "verify", "display", "counts"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = {"task": task_state, "project": projection, "verify": verify_projection,
                  "display": current_display, "counts": counts}[args.command](json.loads(source))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        result = {"status": "NeedsCorrection", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"CurrentStateVerified", "OutcomeDerived", "OutcomeProjectionsVerified",
                                    "CurrentOutcomeDisplayVerified", "OutcomeCountsDerived"} else 2


if __name__ == "__main__":
    sys.exit(main())
