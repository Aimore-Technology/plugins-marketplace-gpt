#!/usr/bin/env python3
"""Offline evidence checks; no connectors, dispatch, approval or write capability."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROUTES_PATH = Path(__file__).resolve().parents[1] / "references/task-routes.json"
POLICIES = ("setup-only", "scheduling-only", "manual-review", "one-cycle-no-customer-send", "one-cycle-approved-work", "draft-only", "report-only", "scheduled-approved-work", "owner-workflow")
SUBMITTED_MANUAL_STEPS = {"VerifyCustomer", "CompleteCommunicationData", "ReviewCommunication", "SyncApprovedPersona"}


def local_schedule_guard(guard):
    return (guard.get('guard_contract') == 'scan-control-v1'
            and guard.get('scan_enabled') is True
            and bool(re.fullmatch(r'[0-9a-f]{32}', str(guard.get('root_id', '')))))


def submitted_manual_route(task):
    return (task.get("Mode") == "Manual" and task.get("ResumeStep") in SUBMITTED_MANUAL_STEPS
            and task.get("OwnerSkill") in {"eightdegrees-communication-context-process", "eightdegrees-client-persona-update"})


def current_submission(task):
    """Normalized persisted snapshot binding, not a substitute for original form checks."""
    snapshot = task.get("AcceptedSubmission") or {}
    normalize = lambda x: str(x or "").replace("-", "").lower().rsplit("/", 1)[-1]
    return (snapshot.get("read_verified") is True and bool(task.get("OperatorId"))
            and bool(task.get("PageId")) and bool(task.get("ActionPageURL"))
            and normalize(snapshot.get("task_id")) == normalize(task["PageId"])
            and normalize(snapshot.get("action_page_id")) == normalize(task["ActionPageURL"])
            and snapshot.get("operator_id") == task["OperatorId"]
            and snapshot.get("content_version") == task["ContentVersion"]
            and bool(re.fullmatch(r"[a-f0-9]{64}", snapshot.get("input_sha256", ""))))


def inspect_result(result):
    """Inspect all MCP layers, including text even when structuredContent exists."""
    found, codes, failures, successes = [], [], [], []

    def visit(value, origin="root", depth=0, error_context=False):
        if depth > 12 or not isinstance(value, dict):
            return
        if value.get("isError") is True:
            failures.append(origin)
        if value.get("success") is True:
            successes.append(origin)
        status = value.get("status", value.get("statusCode", value.get("code") if isinstance(value.get("code"), int) else None))
        failed = (value.get("isError") is True or value.get("success") is False or bool(value.get("error_code"))
                  or bool(value.get("error")) or isinstance(status, int) and status >= 400 or error_context)
        if failed:
            failures.append(origin)
            data = value.get("data") if isinstance(value.get("data"), dict) else {}
            for item, suffix in ((value, ""), (data, ".data")):
                code = item.get("code") or item.get("error_code") or item.get("reason")
                http = item.get("statusCode", status)
                message = item.get("message") or item.get("error")
                if isinstance(code, str):
                    codes.append(code)
                if code or isinstance(http, int) and http >= 400 or message:
                    found.append({"origin": origin + suffix, "code": code,
                                  "http_status": http if isinstance(http, int) else None,
                                  "message": message if isinstance(message, str) else None})
        for key in ("structuredContent", "result"):
            visit(value.get(key), origin + "." + key, depth + 1, failed)
        if failed:
            # Only documented error containers; ordinary successful data/Notes bodies are not errors.
            for key in ("error_data", "error", "response"):
                visit(value.get(key), origin + "." + key, depth + 1, True)
            for detail in value.get("details", []) if isinstance(value.get("details"), list) else []:
                visit(detail, origin + ".details", depth + 1, True)
            if isinstance(value.get("payload"), str):
                try:
                    visit(json.loads(value["payload"]), origin + ".payload", depth + 1, True)
                except ValueError:
                    pass
        for index, block in enumerate(value.get("content", []) or []):
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            text = block.get("text", "")
            if text.strip() == "Action completed.":
                successes.append(origin + f".content[{index}].text")
            try:
                decoded = json.loads(text)
            except (ValueError, TypeError):
                continue
            visit(decoded, origin + f".content[{index}].text", depth + 1)

    visit(result)
    if not failures:
        return {"status": "Accepted" if successes else "Unclassified", "diagnostics": [],
                "scope": "Tool evidence only; not delivery, approval or permission to retry a write"}
    priority = ("WORKFLOW_API_NOT_ENABLED_FOR_LOCATION", "RATE_LIMIT_EXCEEDED", "usage_limit_reached")
    primary = next((code for code in priority if code in codes), None)
    upstream = next((x for x in found if isinstance(x["http_status"], int) and x["http_status"] >= 400), None)
    if primary is None:
        primary = upstream.get("code") if upstream else (codes[0] if codes else None)
    selected = next((x for x in found if x["code"] == primary), upstream or (found[0] if found else {}))
    http = selected.get("http_status") or (upstream.get("http_status") if upstream else None)
    category = {"WORKFLOW_API_NOT_ENABLED_FOR_LOCATION": "CapabilityUnavailable",
                "RATE_LIMIT_EXCEEDED": "RateLimited", "usage_limit_reached": "EntitlementLimit",
                "UNAUTHENTICATED": "AccessDenied", "FORBIDDEN": "AccessDenied",
                "INVALID_ARGUMENT": "InvalidArgument"}.get(primary, "UnknownFailure")
    # An explicit upstream access refusal is not made retryable by a generic wrapper.
    if category in ("UnknownFailure", "InvalidArgument") and http in (401, 403):
        category = "AccessDenied"
    return {"status": "Error", "category": category, "primary_code": primary,
            "http_status": http, "message": selected.get("message"),
            "all_codes": list(dict.fromkeys(codes)), "diagnostics": found,
            "automatic_retry": False, "scope": "Inspect all layers; reconcile side effects separately"}


def notion_text(value):
    """Extract actual fetched Markdown, without treating a failed read as an empty page."""
    if not isinstance(value, dict):
        raise ValueError("notion-json: expected the actual fetch object or MCP result")
    if inspect_result(value)["status"] == "Error":
        raise ValueError("notion-json: read failed; cannot establish link coverage")
    if isinstance(value.get("text"), str):
        return value["text"]
    if isinstance(value.get("structuredContent"), dict):
        try:
            return notion_text(value["structuredContent"])
        except ValueError:
            pass
    for block in value.get("content", []):
        if block.get("type") == "text":
            try:
                return notion_text(json.loads(block["text"]))
            except (ValueError, TypeError):
                continue
    raise ValueError("notion-json: no fetched page text; do not substitute an empty string")


def visible_markdown(text):
    """Mask fenced/inline literal code, retaining line positions for diagnostics."""
    lines, fence = [], None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        in_code = fence is not None
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence = marker
                in_code = True
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip():
                fence = None
        lines.append(re.sub(r"[^\n]", " ", line) if in_code else line)
    text = "".join(lines)
    mask = lambda match: re.sub(r"[^\n]", " ", match.group())
    text = re.sub(r"<code\b[^>]*>.*?</code>", mask, text, flags=re.S)
    return re.sub(r"(`+)([^`\n]*?)\1", mask, text)


def check_links(text, allowed=()):
    if not isinstance(text, str) or not isinstance(allowed, (list, tuple, set)) or not all(isinstance(x, str) for x in allowed):
        raise ValueError("links: expected fetched Markdown and an optional list of verified exact URLs")
    visible, targets = visible_markdown(text), []
    pattern = r'!?\[(?:\\.|[^\]\\])*\]\((?:<([^>\n]+)>|([^\s)\n]+))(?:\s+"[^"\n]*")?\)'
    covered = []
    for match in re.finditer(pattern, visible):
        targets.append((match.start(), match.group(1) or match.group(2)))
        covered.append(match.span())
    for match in re.finditer(r'<(?:mention|embed|image|file)\b[^>]*?\b(?:url|source)="([^"]+)"', visible):
        targets.append((match.start(), match.group(1)))
        covered.append(match.span())
    # Pre-publication checks must also catch bare URLs that Notion will auto-link.
    for match in re.finditer(r'''https?://[^\s<>"'`()]+''', visible):
        if not any(start <= match.start() < end for start, end in covered):
            targets.append((match.start(), match.group().rstrip(".,;:!?")))
    issues = []
    for position, target in targets:
        if target in allowed:
            continue
        try:
            url = urlsplit(target)
            if target.startswith(("/home/", "/Users/", "/tmp/", "file://")) or re.match(r"^[A-Za-z]:[\\/]", target):
                issues.append({"line": visible.count("\n", 0, position) + 1, "target": target, "reasons": ["LocalFileLinkInNotion"]})
                continue
            if url.scheme not in ("http", "https"):
                continue
            host = unquote(url.hostname or "").lower()
            decoded = unquote(target)
            reasons = []
            if re.search(r"\.(?:md|py|json|ya?ml|txt|html?|csv|pdf|png|docx)$", host):
                reasons.append("UnverifiedFileNameHost")
            if any(ord(c) > 127 for c in host):
                reasons.append("UnverifiedNonASCIIHost")
            if any(c in decoded for c in "\u3002\uff1b\uff0c\uff1a\u2014\u201c\u201d"):
                reasons.append("PunctuationInTarget")
            if host == "app.notion.com" and not re.fullmatch(r"/p/[0-9a-fA-F]{32}/?", url.path):
                reasons.append("MalformedNotionPageTarget")
        except ValueError:
            reasons = ["MalformedURL"]
        if reasons:
            issues.append({"line": visible.count("\n", 0, position) + 1, "target": target, "reasons": reasons})
    return {"status": "NeedsCorrection" if issues else "ClearForCheckedPatterns",
            "links_examined": len(targets), "issue_count": len(issues), "issues": issues,
            "scope": "All supplied visible Markdown; static patterns only, no network/visual or permission verification"}


def check_resume(task, policy, explicit_continue=False, phase="execute", schedule_guard=None):
    required = ("TaskId", "RunId", "StepId", "SourceKey", "ContentVersion", "Mode", "State", "Category", "OwnerSkill", "ResumeStep", "ResumeContractVersion")
    if not isinstance(task, dict) or policy not in POLICIES or phase not in ("register", "observe", "execute"):
        raise ValueError("resume-task: expected canonical fields and a supported invocation policy")
    if task.get("State") in ("Completed", "Cancelled"):
        return {"status": "Deferred", "reason": "Terminal task; no migration or action required"}
    missing = [key for key in required if not isinstance(task.get(key), str) or not task[key].strip()]
    if missing:
        return {"status": "NeedsCorrection", "reason": "Missing canonical route fields", "missing": missing}
    routes = json.loads(ROUTES_PATH.read_text(encoding="utf-8"))
    route = routes.get(task["ResumeStep"])
    if (task["ResumeContractVersion"] != "resume-v1" or route is None or route["owner"] != task["OwnerSkill"]
            or task["Category"] not in route["categories"] or task["Mode"] not in ("Manual", "Automatic")
            or task["State"] not in ("WaitingForOperator", "NeedsCorrection", "ReadyToValidate", "InProgress", "Completed", "Cancelled")):
        return {"status": "NeedsCorrection", "reason": "Owner, step, category, mode or contract mismatch; no fallback to communication"}
    reason = None
    effect = route["effect"]
    queue_manual = submitted_manual_route(task) and policy in {"one-cycle-approved-work", "scheduled-approved-work"}
    notification_manual = (task["Mode"] == "Manual" and task["ResumeStep"] == "SendNotificationSms"
                           and policy in {"one-cycle-approved-work", "scheduled-approved-work"})
    if policy == "one-cycle-approved-work" and (task["Mode"] != "Automatic" and not queue_manual and not notification_manual or effect == "setup"):
        return {"status": "Deferred", "reason": "Queue work excludes unrelated Manual tasks and installation setup"}
    if policy == "scheduled-approved-work":
        guard = schedule_guard or {}
        if (not local_schedule_guard(guard) or guard.get("status") != "EligibleForScheduledCycle" or guard.get("policy") != policy
                or guard.get("customer_send_allowed") is not True or not task.get("OperatorId")
                or guard.get("operator_id") != task["OperatorId"]):
            return {"status": "Deferred", "reason": "Current scheduled task-state/operator binding missing; a policy name is not approval"}
        if task["Mode"] != "Automatic" and not queue_manual and not notification_manual:
            return {"status": "Deferred", "reason": "Scheduled work excludes unrelated Manual tasks"}
        if effect == "setup":
            return {"status": "Deferred", "reason": "Installation setup requires explicit initialization, not a scheduled task"}
    if phase == "register":
        entity = task.get("PageId", task.get("url", task.get("id")))
        if not entity:
            return {"status": "NeedsCorrection", "reason": "Register the canonical task first; check its actual PageId before enabling a form"}
        permitted = (policy == "owner-workflow" or queue_manual or notification_manual or policy in {"one-cycle-no-customer-send", "one-cycle-approved-work", "scheduled-approved-work"} and task["Mode"] == "Automatic"
                     or policy == "manual-review" and task["Mode"] == "Manual" and task["OwnerSkill"] in ("eightdegrees-communication-context-process", "eightdegrees-client-persona-update")
                     or policy == "setup-only" and effect == "setup"
                     or policy == "draft-only" and task["OwnerSkill"] == "eightdegrees-sales-reply")
        return {"status": "ValidResumeRoute" if permitted else "Deferred", "entity_id": entity,
                "policy": policy, "phase": "register", "mode": task["Mode"],
                "owner": task["OwnerSkill"], "resume_step": task["ResumeStep"],
                "content_version": task["ContentVersion"],
                "scope": "Metadata registration only; no input consumption, approval, dispatch or completion eligibility"}
    if task["State"] in ("Completed", "Cancelled"):
        reason = "Terminal task; no action"
    elif policy == "report-only":
        reason = "Report-only cannot resume tasks"
    elif policy == "scheduling-only":
        reason = "Scheduling-only cannot resume business tasks"
    elif queue_manual and phase == "execute" and not current_submission(task):
        reason = "Observe and persist the actual current Manual submission before automatic continuation"
    elif task["Mode"] == "Manual" and not queue_manual and not notification_manual and (policy == "one-cycle-no-customer-send" or not explicit_continue):
        reason = "Manual task requires an explicit owner continuation; scanner cannot take over"
    elif policy == "manual-review" and task["Mode"] != "Manual":
        reason = "Manual communication command cannot adopt an Automatic task"
    elif policy == "setup-only" and effect != "setup":
        reason = "Setup-only excludes business continuation"
    elif policy == "manual-review" and task["OwnerSkill"] not in ("eightdegrees-communication-context-process", "eightdegrees-client-persona-update"):
        reason = "Communication continuation cannot dispatch a sales-send or another unrelated owner"
    elif policy in ("one-cycle-no-customer-send", "manual-review", "draft-only", "setup-only") and effect == "customer-send" and not (policy == "one-cycle-no-customer-send" and phase == "observe"):
        reason = "Customer send remains deferred by invocation policy"
    elif policy == "draft-only" and task["ResumeStep"] not in ("VerifyCustomer", "ResolveProjectSources", "ReviewReplyDraft"):
        reason = "Draft-only excludes unrelated business work"
    return {"status": "Deferred" if reason else ("EligibleForInputCheck" if phase == "observe" else "EligibleForOwnerCheck"), "reason": reason,
            "entity_id": task.get("PageId", task.get("url", task.get("id"))),
            "policy": policy, "mode": task["Mode"], "content_version": task["ContentVersion"],
            "owner": task["OwnerSkill"], "resume_step": task["ResumeStep"], "effect": effect,
            "phase": phase,
            "scope": "Route validation only; original action/approval/attempt/ownership checks remain mandatory"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    result = sub.add_parser("tool-result")
    result.add_argument("--input", required=True)
    links = sub.add_parser("notion-links")
    links.add_argument("--input", required=True)
    links.add_argument("--input-format", choices=("notion-json", "markdown"), default="notion-json")
    links.add_argument("--allowed-urls")
    resume = sub.add_parser("resume-task")
    resume.add_argument("--input", required=True)
    resume.add_argument("--policy", choices=POLICIES, required=True)
    resume.add_argument("--schedule-guard", help="Current actual schedule_checks guard result; required for scheduled-approved-work")
    resume.add_argument("--explicit-continue", action="store_true")
    resume.add_argument("--phase", choices=("register", "observe", "execute"), default="execute")
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        if args.command == "notion-links":
            text = source if args.input_format == "markdown" else notion_text(json.loads(source))
            allowed = json.loads(Path(args.allowed_urls).read_text(encoding="utf-8")) if args.allowed_urls else []
            outcome = check_links(text, allowed)
        elif args.command == "tool-result":
            data = json.loads(source)
            if not isinstance(data, dict):
                raise ValueError("tool-result: expected original MCP object")
            outcome = inspect_result(data)
        else:
            schedule_guard = json.loads(Path(args.schedule_guard).read_text(encoding="utf-8")) if args.schedule_guard else None
            outcome = check_resume(json.loads(source), args.policy, args.explicit_continue, args.phase, schedule_guard)
        print(json.dumps(outcome, ensure_ascii=False))
        return 2 if outcome["status"] in ("Error", "NeedsCorrection") else 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "NeedsCorrection", "reason": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
