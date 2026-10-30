#!/usr/bin/env python3
"""Offline schedule planning/readback checks. Never create, delete or run a task."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


TEMPLATE = Path(__file__).resolve().parents[1] / "assets/scan-schedule.md"


def context(data):
    ctx = data["context"]
    if ctx.get("runtime") not in {"work-gpt-task", "cowork-cron-task"}:
        raise ValueError("Select the verified Work GPT task or Cowork native cron runtime")
    for key in ("root_id", "root_url", "operator_id", "mailbox", "provider", "account_id", "host_id", "timezone"):
        if not isinstance(ctx.get(key), str) or not ctx[key].strip() or re.search(r"[\r\n]", ctx[key]):
            raise ValueError("Missing or invalid context: " + key)
    root = ctx["root_id"].replace("-", "").lower()
    if not re.fullmatch(r"[0-9a-f]{32}", root):
        raise ValueError("root_id must be the actual Notion root UUID")
    url = urlsplit(ctx["root_url"])
    if url.scheme != "https" or url.hostname not in ("app.notion.com", "www.notion.so", "notion.so") or root not in url.path.replace("-", "").lower():
        raise ValueError("root_url must identify that actual Notion root")
    ZoneInfo(ctx["timezone"])
    if type(ctx.get("generation")) is not int or ctx["generation"] < 0:
        raise ValueError("generation must be a nonnegative integer from saved lifecycle state")
    return {**ctx, "owner_key": "eightdegrees-scan:" + root}


def prompt_for(ctx):
    return TEMPLATE.read_text(encoding="utf-8").format(**ctx)


def owned_tasks(data, ctx):
    if data.get("list_complete") is not True or data.get("list_includes_inactive") is not True:
        raise ValueError("Need a complete native task listing including paused tasks")
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks must contain actual normalized native task observations")
    owned, ids = [], set()
    marker = "EightDegreesOwnerKey: " + ctx["owner_key"]
    registered = (data.get("scheduling") or {}).get("schedule_ids", [])
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"].strip() or task["id"] in ids:
            raise ValueError("Native task IDs must be present and unique")
        ids.add(task["id"])
        if not isinstance(task.get("prompt"), str):
            raise ValueError("Read native task prompts before claiming owned-task absence")
        if marker not in task["prompt"].splitlines():
            if task["id"] in registered:
                raise ValueError("Registered native task still exists but its ownership marker changed; reconcile")
            continue
        if any(task.get(k) != ctx[k] for k in ("provider", "account_id", "host_id", "runtime")):
            raise ValueError("Matching installation has a different executor; reconcile on its owner host")
        if task.get("read_verified") is not True:
            raise ValueError("Read the owned native task; a title/list summary is insufficient")
        owned.append(task)
    return owned


def exact_task(task, ctx):
    return (task.get("enabled") is True and task.get("runtime") == ctx["runtime"] and type(task.get("interval_minutes")) is int
            and task["interval_minutes"] == 15 and task.get("timezone") == ctx["timezone"]
            and task.get("prompt") == prompt_for(ctx))


def plan(data):
    ctx = context(data)
    tasks = owned_tasks(data, ctx)
    operation, caps = data.get("operation"), data.get("capabilities", {})
    if operation not in ("start", "stop"):
        raise ValueError("operation must be start or stop")
    if caps.get("list") is not True:
        return {"status": "NativeSchedulingUnavailable", "reason": "Native listing capability is required"}
    saved = data.get("scheduling") or {}
    if (saved.get("enabled") is True or saved.get("schedule_ids")) and any(
            saved.get(k) != ctx[c] for k, c in (("owner_host", "host_id"), ("provider", "provider"), ("account_id", "account_id"), ("runtime", "runtime"))):
        return {"status": "NeedsReconciliation", "reason": "Saved schedule belongs to another executor; access its native scheduler before changing ownership"}
    pending = data.get("pending_attempt") or saved.get("pending_attempt") or {}
    if pending and pending.get("status") not in ("Resolved", "RejectedBeforeDispatch", "NoEffectVerified"):
        return {"status": "NeedsReconciliation", "reason": "Resolve the existing native create/delete attempt before mutation"}
    if operation == "stop":
        if tasks and caps.get("delete") is not True:
            return {"status": "NativeDeletionUnavailable", "schedule_ids": [t["id"] for t in tasks]}
        return {"status": "EligibleForNativeDelete" if tasks else "AlreadyAbsent",
                "schedule_ids": [t["id"] for t in tasks], "owner_key": ctx["owner_key"]}
    if ctx["generation"] < 1:
        raise ValueError("Start must first register a positive lifecycle generation")
    if caps.get("read") is not True or caps.get("runner_ready") is not True or caps.get("exact_15_minutes") is not True:
        return {"status": "NativeSchedulingUnavailable", "reason": "Verify exact 15-minute cadence and skill/connector access; no alternate cadence or backend"}
    if len(tasks) > 1:
        return {"status": "NeedsReconciliation", "reason": "Duplicate owned scanners; do not create another", "schedule_ids": [t["id"] for t in tasks]}
    if tasks and exact_task(tasks[0], ctx):
        return {"status": "ReuseExisting", "schedule_id": tasks[0]["id"], "owner_key": ctx["owner_key"]}
    capability = "update" if tasks else "create"
    if caps.get(capability) is not True:
        return {"status": "NativeSchedulingUnavailable", "reason": "Required native " + capability + " operation is unavailable"}
    return {"status": "EligibleForNativeUpdate" if tasks else "EligibleForNativeCreate",
            "schedule_id": tasks[0]["id"] if tasks else None, "owner_key": ctx["owner_key"],
            "interval_minutes": 15, "timezone": ctx["timezone"], "prompt": prompt_for(ctx)}


def verify(data):
    ctx = context(data)
    tasks = owned_tasks(data, ctx)
    pending = data.get("pending_attempt") or (data.get("scheduling") or {}).get("pending_attempt") or {}
    if pending.get("status") in ("Unknown", "Pending", "Creating", "Deleting", "WaitingForConfirmation"):
        return {"status": "NeedsReconciliation", "reason": "Native operation still unresolved; absence alone cannot settle an in-flight create"}
    if data.get("operation") == "start":
        valid = ctx["generation"] > 0 and len(tasks) == 1 and exact_task(tasks[0], ctx)
        return {"status": "RunningVerified" if valid else "NeedsCorrection",
                "schedule_ids": [t["id"] for t in tasks], "owner_key": ctx["owner_key"],
                "prompt_sha256": hashlib.sha256(prompt_for(ctx).encode()).hexdigest()}
    if data.get("operation") != "stop":
        raise ValueError("operation must be start or stop")
    return {"status": "StoppedVerified" if not tasks else "NeedsCorrection",
            "schedule_ids": [t["id"] for t in tasks], "owner_key": ctx["owner_key"]}


def guard(data):
    if data.get("trigger") == "manual":
        return {"status": "EligibleForManualCycle", "customer_send_allowed": False}
    if data.get("trigger") != "scheduled":
        raise ValueError("Use the actual manual or native scheduled invocation context")
    ctx, saved, invocation = context(data), data["scheduling"], data["invocation"]
    setup = data["setup"]
    if (ctx["generation"] < 1 or saved.get("enabled") is not True or saved.get("state") != "Running"
            or saved.get("approved_work_enabled") is not True
            or saved.get("desired_state") != "Running" or type(saved.get("generation")) is not int
            or saved.get("generation") != ctx["generation"]
            or saved.get("owner_key") != ctx["owner_key"]
            or saved.get("owner_host") != ctx["host_id"] or saved.get("provider") != ctx["provider"]
            or saved.get("account_id") != ctx["account_id"]
            or saved.get("runtime") != ctx["runtime"]
            or setup.get("operator_id") != ctx["operator_id"] or setup.get("gmail_account") != ctx["mailbox"]
            or str(setup.get("notion_root_id", "")).replace("-", "").lower() != ctx["root_id"].replace("-", "").lower()
            or not isinstance(invocation.get("invocation_id"), str) or not invocation["invocation_id"].strip()
            or invocation.get("schedule_id") not in saved.get("schedule_ids", [])):
        return {"status": "Deferred", "reason": "Stopped, stale, wrong native task or executor"}
    active = data.get("active_run") or {}
    if active.get("status") == "InProgress" and active.get("invocation_id") != invocation.get("invocation_id"):
        return {"status": "Deferred", "reason": "Another scan is in progress; reconcile uncertain ownership, never overlap"}
    return {"status": "EligibleForScheduledCycle", "customer_send_allowed": True,
            "policy": "scheduled-approved-work", "operator_id": ctx["operator_id"],
            "schedule_id": invocation["schedule_id"], "invocation_id": invocation["invocation_id"],
            "owner_key": ctx["owner_key"], "generation": ctx["generation"], "runtime": ctx["runtime"],
            "scope": "Observed state only; Notion is not an atomic lock or native execution interceptor"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "verify", "guard"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = {"plan": plan, "verify": verify, "guard": guard}[args.command](json.loads(source))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        result = {"status": "NeedsCorrection", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"ReuseExisting", "AlreadyAbsent", "EligibleForNativeCreate", "EligibleForNativeUpdate", "EligibleForNativeDelete", "RunningVerified", "StoppedVerified", "EligibleForManualCycle", "EligibleForScheduledCycle"} else 2


if __name__ == "__main__":
    sys.exit(main())
