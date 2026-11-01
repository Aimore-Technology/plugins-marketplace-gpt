#!/usr/bin/env python3
"""Prepare and read back an owner plan offline; never call a connector or send."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

from fact_checks import canonical_facts
from notion_checks import object_result, page_body, page_id, schema_values
from reply_transport import prepare as prepare_reply


PROFILES = json.loads((Path(__file__).resolve().parents[1] / "references/owner-completion-profiles.json").read_text())
POLICIES = {"setup-only", "scheduling-only", "manual-review", "one-cycle-no-customer-send", "one-cycle-approved-work",
            "draft-only", "owner-workflow", "scheduled-approved-work", "report-only"}
TYPES = {"run": ("page-links",), "task": ("page-links", "route"),
         "action": ("page-links", "task-display"), "publication": ("page-links",),
         "html-preview": ("page-links", "preview"), "image-preview": ("page-links", "preview-image")}
TASK_EVIDENCE = {"reply-draft", "reply-sent", "outcome", "crm-receipt", "material-handoff", "sms-authority", "email-presentation", "sms-presentation", "contact-restriction"}
OPERATIONS = {"content", "review", "scan", "setup", "schedule", "report", "recovery", "reply-patch"}
SCOPE = "Offline preparation/readback only; no host interception, approval, lock or proof of past tool order"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                                     allow_nan=False).encode()).hexdigest()


def identity(value):
    normalized = page_id(value)
    if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{32}", normalized):
        raise ValueError("Expected an actual Notion page ID/URL, not a role or invented placeholder")
    return normalized


def compile_checks(resources):
    """Derive required coverage from affected roles, including uncreated slots."""
    if not isinstance(resources, list) or not resources:
        raise ValueError("Affected resources must be a nonempty list")
    roles, required = {}, {}
    for resource in resources:
        role, kind = resource.get("role"), resource.get("type")
        if not isinstance(role, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", role) or role in roles or kind not in TYPES:
            raise ValueError("Each affected resource needs a unique role and supported type")
        roles[role] = resource
        if resource.get("entity_id") is not None:
            identity(resource["entity_id"])
        if kind == "task" and (not isinstance(resource.get("content_version"), str) or not resource["content_version"].strip()):
            raise ValueError("Each task needs its actual/planned content_version")
        extra = resource.get("evidence", [])
        if not isinstance(extra, list) or len(set(extra)) != len(extra) or not set(extra) <= TASK_EVIDENCE or extra and kind != "task":
            raise ValueError("Extra transport/outcome evidence must belong to a task")
        for check in (*TYPES[kind], *extra):
            spec = {"kind": check, "entity_role": role}
            if check == "preview-image":
                if (not resource.get("content_version") or not isinstance(resource.get("html_sha256"), str)
                        or not re.fullmatch(r"[a-f0-9]{64}", resource["html_sha256"])):
                    raise ValueError("Image role needs the frozen HTML digest and content version")
                spec.update(content_version=resource["content_version"], html_sha256=resource["html_sha256"])
            required[role + ":" + check] = spec
    if sum(r["type"] == "run" for r in resources) != 1:
        raise ValueError("Plan exactly one owning run; downstream owners prepare separate plans")
    for resource in resources:
        if resource["type"] == "action" and roles.get(resource.get("task_role"), {}).get("type") != "task":
            raise ValueError("Action must bind to a task role in this same owner plan")
    return required


def prepare(data):
    owner, policy, operation = data.get("owner_skill"), data.get("policy"), data.get("operation")
    if owner not in PROFILES or policy not in POLICIES or operation not in OPERATIONS:
        raise ValueError("Unknown owner, invocation policy or operation")
    if (policy == "report-only" and owner != "eightdegrees-daily-brief-and-handover"
            or owner == "eightdegrees-automation-control" and policy != "scheduling-only"
            or policy == "scheduling-only" and owner != "eightdegrees-automation-control"
            or policy == "setup-only" and owner != "eightdegrees-initialization"
            or policy in {"one-cycle-approved-work", "scheduled-approved-work"} and owner == "eightdegrees-initialization"
            or policy == "draft-only" and owner != "eightdegrees-sales-reply"
            or policy == "manual-review" and owner not in {"eightdegrees-communication-context-process", "eightdegrees-client-persona-update"}):
        raise ValueError("Owner conflicts with invocation policy")
    for key in ("invocation_id", "publication_version"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError("Missing invocation/publication version")
    resources = copy.deepcopy(data["resources"])
    required = compile_checks(resources)
    if not set(PROFILES[owner]) <= {s["kind"] for s in required.values()}:
        raise ValueError("Affected roles omit the owner's minimum check coverage")
    if operation == "content" and "facts" not in data:
        raise ValueError("Content projection requires the actual proposed customer facts")
    if operation == "reply-patch" and "reply" not in data:
        raise ValueError("Stored reply patch requires the actual transport manifest")
    checks, outputs = [], {}

    def checked(name, kind, source, function, expected):
        try:
            result = function(source)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            result = {"status": "NeedsCorrection", "issues": [str(exc)]}
        exit_code = 0 if result.get("status") == expected else 2
        checks.append({"name": name, "kind": kind, "input_sha256": digest(source),
                       "result_sha256": digest(result), "exit_code": exit_code, "result": result})
        return result, exit_code

    if "facts" in data:
        result, code = checked("facts", "facts", data["facts"], canonical_facts, "ValidFactSemantics")
        if code:
            return {"status": "NeedsCorrection", "checks": checks, "scope": SCOPE}
        outputs["facts"] = copy.deepcopy(result["facts"])
    rows = data.get("notion_rows", [])
    if not isinstance(rows, list):
        raise ValueError("notion_rows must list the exact proposed property writes")
    roles = {r["role"] for r in resources}
    for index, row in enumerate(rows):
        if row.get("role") not in roles:
            raise ValueError("Property write is outside the planned affected roles")
        _, code = checked("row-" + str(index), "schema-values", row, schema_values, "ValidSelectValues")
        if code:
            return {"status": "NeedsCorrection", "checks": checks, "scope": SCOPE}
    if "reply" in data:
        result, code = checked("reply-patch", "reply-prepare", data["reply"], prepare_reply, "DraftPatchPlanned")
        if code:
            return {"status": "NeedsCorrection", "checks": checks, "scope": SCOPE}
        outputs["reply_args"] = copy.deepcopy(result["args"])
    plan = {k: data[k] for k in ("owner_skill", "policy", "operation", "invocation_id", "publication_version")}
    plan.update(contract_version="execution-v1", resources=resources, required_checks=required,
                prechecks=[{k: c[k] for k in ("name", "kind", "input_sha256", "result_sha256", "exit_code")} for c in checks])
    return {"status": "PreflightPrepared", "execution_plan": plan, "plan_sha256": digest(plan),
            "checks": checks, "outputs": outputs, "scope": SCOPE}


def ready(data):
    """Verify the exact persisted plan and resolve its predeclared entity slots."""
    prepared = data["prepared"]
    plan = prepared["execution_plan"]
    if (prepared.get("status") != "PreflightPrepared" or prepared.get("plan_sha256") != digest(plan)
            or plan.get("contract_version") != "execution-v1"
            or plan["required_checks"] != compile_checks(plan["resources"])):
        raise ValueError("Missing or changed original generated plan")
    # Recheck results as well as hashes; a zero exit without a successful result is not evidence.
    expected = {"facts": "ValidFactSemantics", "schema-values": "ValidSelectValues", "reply-prepare": "DraftPatchPlanned"}
    observed = prepared.get("checks", [])
    if len(observed) != len(plan["prechecks"]):
        raise ValueError("Missing original preflight results")
    for source, result in zip(plan["prechecks"], observed):
        if (source.get("kind") not in expected
                or type(source.get("exit_code")) is not int
                or any(source.get(k) != result.get(k) for k in ("name", "kind", "input_sha256", "result_sha256", "exit_code"))
                or type(result.get("exit_code")) is not int or result["exit_code"] != 0
                or result.get("result_sha256") != digest(result.get("result"))
                or result.get("result", {}).get("status") != expected.get(source["kind"])
                or result.get("result", {}).get("issues")):
            raise ValueError("Preflight is failed, missing or malformed")
    outputs = {}
    for check in observed:
        if check["kind"] == "facts":
            outputs["facts"] = check["result"]["facts"]
        if check["kind"] == "reply-prepare":
            outputs["reply_args"] = check["result"]["args"]
    if prepared.get("outputs") != outputs:
        raise ValueError("Prepared outputs changed after validation")
    bindings = data.get("bindings", {})
    roles = {r["role"]: r for r in plan["resources"]}
    if not isinstance(bindings, dict) or not set(bindings) <= roles.keys():
        raise ValueError("Cannot add a resource role after freezing the plan")
    resolved = {}
    for role, resource in roles.items():
        original, actual = resource.get("entity_id"), bindings.get(role, resource.get("entity_id"))
        if original is not None and identity(original) != identity(actual):
            raise ValueError("Cannot rebind an existing target")
        resolved[role] = identity(actual)
    if len(set(resolved.values())) != len(resolved):
        raise ValueError("Distinct resource roles cannot alias the same entity")
    saved = object_result(data["saved_plan"])
    run_role = next(r["role"] for r in plan["resources"] if r["type"] == "run")
    if saved.get("metadata", {}).get("type") != "page" or identity(saved.get("id")) != resolved[run_role]:
        raise ValueError("Plan evidence must be the actual owning run page")
    matches = []
    for text in re.findall(r"```json\s*\n(.*?)\n```", page_body(data["saved_plan"]), re.S):
        try:
            candidate = json.loads(text)
        except ValueError:
            continue
        if isinstance(candidate, dict) and candidate.get("execution_plan", {}).get("invocation_id") == plan["invocation_id"]:
            matches.append(candidate)
    if len(matches) != 1 or matches[0].get("execution_plan") != plan or matches[0].get("plan_sha256") != digest(plan):
        raise ValueError("Original saved plan is absent, ambiguous or different; no retrospective pass")
    required = {name: {**{k: v for k, v in spec.items() if k != "entity_role"},
                       "entity_id": resolved[spec["entity_role"]]} for name, spec in plan["required_checks"].items()}
    required["execution-plan"] = {"kind": "execution-plan", "entity_id": resolved[run_role],
                                  "plan_sha256": digest(plan)}
    registry = {k: plan[k] for k in ("owner_skill", "policy", "invocation_id", "publication_version")}
    for key, kinds in {"run_page_ids": {"run"}, "task_page_ids": {"task"}, "action_page_ids": {"action"},
                       "publication_page_ids": {"publication", "html-preview", "image-preview"}}.items():
        registry[key] = [resolved[r["role"]] for r in plan["resources"] if r["type"] in kinds]
    registry.update(required_checks=required, task_versions={resolved[r["role"]]: r["content_version"] for r in plan["resources"] if r["type"] == "task"},
                    action_bindings={resolved[r["role"]]: resolved[r["task_role"]] for r in plan["resources"] if r["type"] == "action"},
                    execution_plan_sha256=digest(plan))
    return {"status": "ExecutionPlanReady", "registry": registry, "plan_page_id": saved["id"],
            "entity_id": saved["id"], "execution_plan_sha256": digest(plan),
            "invocation_id": plan["invocation_id"], "publication_version": plan["publication_version"], "scope": SCOPE}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "ready"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = (prepare if args.command == "prepare" else ready)(json.loads(raw))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)], "scope": SCOPE}
    print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    return 0 if result["status"] in {"PreflightPrepared", "ExecutionPlanReady"} else 2


if __name__ == "__main__":
    sys.exit(main())
