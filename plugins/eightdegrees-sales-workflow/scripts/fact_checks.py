#!/usr/bin/env python3
"""Check customer fact semantics offline, before saving proposals or snapshots."""

import argparse
import json
from pathlib import Path
import sys


STATES = {"ConfirmedYes": True, "ConfirmedNo": False, "Unknown": None}
FINANCE_STATES = {
    "approved": "ConfirmedYes", "confirmedyes": "ConfirmedYes",
    "rejected": "ConfirmedNo", "declined": "ConfirmedNo", "confirmedno": "ConfirmedNo",
    "unknown": "Unknown", "not confirmed": "Unknown", "unconfirmed": "Unknown",
}


def check_facts(data):
    if not isinstance(data, dict):
        raise ValueError("Expected a proposed customer-fact object")
    issues, checked = [], 0
    if "facts" in data:
        if not isinstance(data["facts"], list) or not data["facts"]:
            raise ValueError("facts must be a nonempty list")
        names = set()
        for fact in data["facts"]:
            if not isinstance(fact, dict) or not isinstance(fact.get("name"), str) or not fact["name"].strip():
                raise ValueError("Each fact needs a name, status, value and evidence")
            name, state = fact["name"], fact.get("status")
            if name in names:
                issues.append(name + ": duplicate fact")
            names.add(name)
            checked += 1
            if state not in STATES or "value" not in fact or fact["value"] is not STATES.get(state):
                issues.append(name + ": status/value disagree; unknown must be null")
            if state in ("ConfirmedYes", "ConfirmedNo") and not str(fact.get("evidence") or "").strip():
                issues.append(name + ": a confirmed fact needs source evidence")
    # Check the actual flat representation observed in communication snapshots too.
    if "finance_approved" in data or "finance_status" in data:
        checked += 1
        status = data.get("finance_status")
        state = FINANCE_STATES.get(status.strip().casefold()) if isinstance(status, str) else None
        if (state is None or "finance_approved" not in data
                or data["finance_approved"] is not STATES.get(state)):
            issues.append("finance_approved/finance_status: use explicit yes, explicit no, or unknown/null")
    if not checked:
        raise ValueError("No documented customer facts supplied; do not pass an unrelated control object")
    return {"status": "NeedsCorrection" if issues else "ValidFactSemantics", "issues": issues,
            "facts_checked": checked,
            "scope": "Representation check only; source accuracy, approval and execution remain separate"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = check_facts(json.loads(text))
    except (ValueError, OSError, TypeError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "ValidFactSemantics" else 2


if __name__ == "__main__":
    sys.exit(main())
