#!/usr/bin/env python3
"""Run local checks using one original capture bundle; never call any connector."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

import execution_preflight
import fact_checks
import notion_checks
import operator_experience
import outcome_checks
import material_handoff
import sms_authority

OPERATIONS = {
    "notion.page-links": notion_checks.page_links,
    "notion.schema-values": notion_checks.schema_values,
    "notion.task-display": notion_checks.task_display,
    "notion.preview": notion_checks.check_preview,
    "notion.preview-image": notion_checks.check_image_preview,
    "notion.completion-gate": notion_checks.completion_gate,
    "execution.prepare": execution_preflight.prepare,
    "execution.ready": execution_preflight.ready,
    "facts.canonical": fact_checks.canonical_facts,
    "outcome.verify": outcome_checks.verify_projection,
    "outcome.display": outcome_checks.current_display,
    "operator.feedback": operator_experience.feedback,
    "operator.review": operator_experience.review_brief,
    "operator.results": operator_experience.result_summary,
    "material.plan": material_handoff.plan,
    "material.verify": material_handoff.verify,
    "sms.prepare": sms_authority.prepare,
    "sms.verify": sms_authority.verify,
}
PASSED = {"ClearForCheckedPatterns", "ValidSelectValues", "DisplayConsistentForCheckedPatterns",
          "SavedEmbedAndBytesMatch", "SavedImageAndBytesMatch", "EligibleForCompletion",
          "PreflightPrepared", "ExecutionPlanReady", "ValidFactSemantics", "OutcomeProjectionsVerified",
          "CurrentOutcomeDisplayVerified", "OperatorFeedbackReady", "ReviewBriefReady", "OperatorResultsReady",
          "MaterialHandoffPlanned", "MaterialHandoffVerified", "SMSNotificationPrepared", "SMSNotificationVerified"}


def run(plan, captures):
    checks = plan["checks"]
    if not isinstance(checks, list) or not checks or not isinstance(captures, dict):
        raise ValueError("Supply a nonempty local check plan and original named captures")
    names = [c.get("name") for c in checks]
    if any(not isinstance(n, str) or not n for n in names) or len(set(names)) != len(names):
        raise ValueError("Check names must be unique and nonempty")
    results, hashes, references = {}, {}, 0

    def expand(value):
        nonlocal references
        if isinstance(value, dict):
            if set(value) == {"$capture"}:
                name = value["$capture"]
                original = captures[name]
                if name not in hashes:
                    hashes[name] = hashlib.sha256(json.dumps(original, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
                references += 1
                return original  # Preserve all error/warning/completeness layers.
            if set(value) == {"$result"}:
                name = value["$result"]
                if name not in results or results[name]["exit_code"] != 0:
                    raise ValueError("Only an earlier successful check result may be referenced")
                return results[name]["result"]
            return {k: expand(v) for k, v in value.items()}
        if isinstance(value, list):
            return [expand(v) for v in value]
        return value

    for check in checks:
        try:
            operation = OPERATIONS[check["operation"]]
            # Helpers receive isolated inputs; one check cannot edit the bundle
            # or fabricate evidence for another check in this batch.
            result = operation(copy.deepcopy(expand(check["input"])))
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            result = {"status": "NeedsCorrection", "issues": [str(exc)]}
        code = 0 if result.get("status") in PASSED and not result.get("issues") else 2
        results[check["name"]] = {"name": check["name"], "operation": check["operation"], "exit_code": code, "result": result}
        if code:
            break
    return {"status": "LocalChecksPassed" if len(results) == len(checks) and all(c["exit_code"] == 0 for c in results.values()) else "NeedsCorrection",
            "checks": list(results.values()), "capture_hashes": hashes, "capture_references": references,
            "distinct_captures_used": len(hashes), "checks_requested": len(checks), "checks_run": len(results),
            "scope": "Local selected checks only; no connector I/O, cross-invocation cache, approval, mutation or historical order proof"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--captures", required=True)
    args = parser.parse_args()
    try:
        plan = json.loads(sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8"))
        captures = json.loads(Path(args.captures).read_text(encoding="utf-8"))
        result = run(plan, captures)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result["status"] == "LocalChecksPassed" else 2


if __name__ == "__main__":
    sys.exit(main())
