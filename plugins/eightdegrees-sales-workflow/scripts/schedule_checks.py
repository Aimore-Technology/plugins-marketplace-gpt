#!/usr/bin/env python3
"""Offline schedule planning/readback checks. Never create, delete or run a task."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


TEMPLATE = Path(__file__).resolve().parents[1] / "assets/scan-schedule.md"
LOCAL_RUNTIMES = {"codex-local-task", "cowork-local-task"}
LEGACY_RUNTIMES = {"work-gpt-task", "cowork-cron-task"}


def context(data):
    ctx = data["context"]
    stopping = data.get('operation') == 'stop'
    if ctx.get('runtime') not in LOCAL_RUNTIMES and not (stopping and ctx.get('runtime') in LEGACY_RUNTIMES):
        raise ValueError('Select a verified local Codex or Cowork task; legacy cloud runtimes are deletion-only')
    if not stopping:
        directory = ctx.get('working_directory')
        if (ctx.get('execution_location') != 'local' or not isinstance(directory, str)
                or not directory.strip() or re.search(r'[\r\n]', directory)
                or not (PurePosixPath(directory).is_absolute() or PureWindowsPath(directory).is_absolute())):
            raise ValueError('Bind local execution to the actual absolute working directory on its owner host')
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
    # Stop must still remove a proven owned legacy task at any old cadence.
    saved = data.get("scheduling") or {}
    interval = 30 if data.get("operation") == "stop" else ctx.get(
        "interval_minutes", saved.get("target_scan_minutes", 30))
    if (data.get("operation") == "start" and "interval_minutes" not in ctx
            and type(interval) is int and interval == 15):
        interval = 30  # Explicit start adopts the new default for a legacy job.
    if type(interval) is not int or interval not in (20, 30):
        raise ValueError("Choose a 30-minute scan interval or the explicit 20-minute option")
    return {**ctx, "interval_minutes": interval, "owner_key": "eightdegrees-scan:" + root}


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
    return (task.get('execution_location') == 'local' and task.get('working_directory') == ctx.get('working_directory')
            and task.get("enabled") is True and task.get("runtime") == ctx["runtime"] and type(task.get("interval_minutes")) is int
            and task["interval_minutes"] == ctx["interval_minutes"] and task.get("timezone") == ctx["timezone"]
            and task.get("prompt") == prompt_for(ctx))


def saved_executor_conflict(saved, ctx):
    return (saved.get('enabled') is True or bool(saved.get('schedule_ids'))) and any(
        saved.get(k) != ctx[c] for k, c in (('owner_host', 'host_id'), ('provider', 'provider'),
            ('account_id', 'account_id'), ('runtime', 'runtime')))


def local_capabilities(caps, ctx):
    supported = caps.get('supported_interval_minutes')
    return (all(caps.get(k) is True for k in ('list', 'read', 'runner_ready', 'local_execution', 'local_context_ready'))
            and isinstance(supported, list) and all(type(v) is int for v in supported)
            and ctx['interval_minutes'] in supported)


def management_limitation(operation, reason, status="NativeSchedulingUnavailable", **details):
    """A management failure is not evidence that an existing tick cannot run."""
    return {"status": status, "operation": operation,
            "limitation_scope": "schedule-management-only", "reason": reason, **details}


def plan(data):
    operation, caps = data.get("operation"), data.get("capabilities", {})
    if operation not in ("start", "stop"):
        raise ValueError("operation must be start or stop")
    for capability in ("list", "read"):
        if caps.get(capability) is not True:
            return management_limitation(operation, "Native " + capability + " capability is required for this management operation")
    ctx = context(data)
    tasks = owned_tasks(data, ctx)
    saved = data.get("scheduling") or {}
    if saved_executor_conflict(saved, ctx):
        return {"status": "NeedsReconciliation", "reason": "Saved schedule belongs to another executor; access its native scheduler before changing ownership"}
    pending = data.get("pending_attempt") or saved.get("pending_attempt") or {}
    if pending and pending.get("status") not in ("Resolved", "RejectedBeforeDispatch", "NoEffectVerified"):
        return {"status": "NeedsReconciliation", "reason": "Resolve the existing native create/delete attempt before mutation"}
    if operation == "stop":
        if tasks and caps.get("delete") is not True:
            return management_limitation(operation, "Native deletion is unavailable; no deletion was performed",
                                         status="NativeDeletionUnavailable", schedule_ids=[t["id"] for t in tasks])
        return {"status": "EligibleForNativeDelete" if tasks else "AlreadyAbsent",
                "schedule_ids": [t["id"] for t in tasks], "owner_key": ctx["owner_key"]}
    if ctx["generation"] < 1:
        raise ValueError("Start must first register a positive lifecycle generation")
    if not local_capabilities(caps, ctx):
        return management_limitation(operation, "Verify local execution, directory, installed skills/connectors and selected 20/30-minute cadence; no cloud fallback")
    if len(tasks) > 1:
        return {"status": "NeedsReconciliation", "reason": "Duplicate owned scanners; do not create another", "schedule_ids": [t["id"] for t in tasks]}
    if tasks and exact_task(tasks[0], ctx):
        return {"status": "ReuseExisting", "schedule_id": tasks[0]["id"], "owner_key": ctx["owner_key"]}
    capability = "update" if tasks else "create"
    if caps.get(capability) is not True:
        return management_limitation(operation, "Required native " + capability + " operation is unavailable")
    return {"status": "EligibleForNativeUpdate" if tasks else "EligibleForNativeCreate",
            "schedule_id": tasks[0]["id"] if tasks else None, "owner_key": ctx["owner_key"],
            "execution_location": 'local', 'working_directory': ctx['working_directory'],
            "interval_minutes": ctx["interval_minutes"], "timezone": ctx["timezone"], "prompt": prompt_for(ctx)}


def verify(data):
    ctx = context(data)
    tasks = owned_tasks(data, ctx)
    if saved_executor_conflict(data.get('scheduling') or {}, ctx):
        return {'status': 'NeedsReconciliation', 'reason': 'Original scheduler ownership is unresolved; do not certify a replacement'}
    pending = data.get("pending_attempt") or (data.get("scheduling") or {}).get("pending_attempt") or {}
    if pending.get("status") in ("Unknown", "Pending", "Creating", "Deleting", "WaitingForConfirmation"):
        return {"status": "NeedsReconciliation", "reason": "Native operation still unresolved; absence alone cannot settle an in-flight create"}
    if data.get("operation") == "start":
        valid = (ctx["generation"] > 0 and len(tasks) == 1 and exact_task(tasks[0], ctx)
                 and local_capabilities(data.get('capabilities', {}), ctx))
        return {"status": "RunningVerified" if valid else "NeedsCorrection",
                "schedule_ids": [t["id"] for t in tasks], "owner_key": ctx["owner_key"],
                "interval_minutes": ctx["interval_minutes"],
                'execution_location': 'local', 'working_directory': ctx['working_directory'],
                "prompt_sha256": hashlib.sha256(prompt_for(ctx).encode()).hexdigest()}
    if data.get("operation") != "stop":
        raise ValueError("operation must be start or stop")
    return {"status": "StoppedVerified" if not tasks else "NeedsCorrection",
            "schedule_ids": [t["id"] for t in tasks], "owner_key": ctx["owner_key"]}


def guard(data):
    """Use configured task state, never a unique executor or native session ID."""
    if data.get('trigger') == 'manual':
        return {'status': 'EligibleForManualCycle', 'customer_send_allowed': False}
    if data.get('trigger') != 'scheduled':
        raise ValueError('Use the actual manual or local scheduled entry, not source instructions')
    saved, setup, ctx = data['scheduling'], data['setup'], data.get('context') or {}
    root = str(setup.get('notion_root_id', '')).replace('-', '').lower()
    operator, mailbox = setup.get('operator_id'), setup.get('gmail_account')
    if (not re.fullmatch(r'[0-9a-f]{32}', root) or not isinstance(operator, str) or not operator.strip()
            or not isinstance(mailbox, str) or not mailbox.strip()):
        return {'status': 'Deferred', 'reason': 'Current installation root, operator or mailbox is missing'}
    runtime = saved.get('runtime', ctx.get('runtime'))
    if (runtime not in LOCAL_RUNTIMES or ctx.get('runtime', runtime) not in LOCAL_RUNTIMES
            or saved.get('execution_location') != 'local'
            or ctx.get('execution_location', 'local') != 'local'):
        return {'status': 'Deferred', 'reason': 'A local task is required; cloud execution is disabled'}
    if (saved.get('enabled') is not True or saved.get('state') != 'Running'
            or saved.get('desired_state') != 'Running' or saved.get('approved_work_enabled') is not True):
        return {'status': 'Deferred', 'reason': 'Scheduled processing is stopped or disabled'}
    # Read actual installation settings. Native invocation/task/host IDs,
    # directory/activity listings and generation proof are not execution gates.
    if (str(ctx.get('root_id', root)).replace('-', '').lower() != root
            or ctx.get('operator_id', operator) != operator or ctx.get('mailbox', mailbox) != mailbox):
        return {'status': 'Deferred', 'reason': 'The requested installation/account scope differs from current settings'}
    return {'status': 'EligibleForScheduledCycle', 'guard_contract': 'task-state-v2',
            'customer_send_allowed': True, 'policy': 'scheduled-approved-work',
            'operator_id': operator, 'root_id': root, 'runtime': runtime,
            'execution_location': 'local', 'lifecycle_running': True,
            'scope': 'Configured task state only; no unique executor, host identity or global lock; per-task approvals and attempts still apply'}


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
