#!/usr/bin/env python3
"""Offline Notion publication checks and exact patch plans; no writes or approvals."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from workflow_checks import check_links, inspect_result, notion_text, visible_markdown


def object_result(value):
    """Extract an actual successful JSON tool payload without losing error layers."""
    if not isinstance(value, dict) or inspect_result(value)["status"] == "Error":
        raise ValueError("Missing or failed original tool result")
    if isinstance(value.get("structuredContent"), dict):
        return value["structuredContent"]
    for block in value.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            try:
                item = json.loads(block["text"])
            except (ValueError, TypeError):
                continue
            if isinstance(item, dict):
                return item
    return value


def page_body(value):
    payload = object_result(value)
    if any(x.get("truncated") is True or x.get("unknown_block_count", 0) or x.get("unknown_block_ids")
           for x in (payload, payload.get("metadata", {}))):
        raise ValueError("Incomplete page capture; reconcile omitted blocks first")
    text = notion_text(value)
    # Fetch wrappers/properties are not editable page content.
    match = re.search(r"<content>\s*\n(.*?)\n</content>", text, re.S)
    return match.group(1) if match else text


def section_patch(data):
    """Plan one workflow-owned H2 section replacement from a current fetch."""
    text = page_body(data["page"])
    heading, replacement = data["heading"], data["replacement"].rstrip()
    if not isinstance(heading, str) or not heading.strip() or "\n" in heading:
        raise ValueError("Expected one exact workflow-owned H2 heading")
    header = "## " + heading
    if replacement.splitlines()[0] != header:
        raise ValueError("Replacement must begin with the same actual heading")
    if len(re.findall(r"^## ", replacement, re.M)) != 1:
        raise ValueError("Replacement must contain exactly one H2 section")
    # This helper owns status/queue text, not operator input or child records.
    if re.search(r"<(?:page|folder|database|synced-block)\b|^\s*- \[[ xX]\]|<todo\b", replacement, re.M):
        raise ValueError("A status patch must not introduce child records or input controls")
    masked = visible_markdown(text)
    headings = list(re.finditer(r"^## [^\n]+", masked, re.M))
    matches = [m for m in headings if m.group().rstrip() == header]
    if len(matches) != 1:
        return {"status": "NeedsCorrection", "reason": "Heading missing or repeated; fetch/repair ownership, never guess", "matches": len(matches)}
    start = matches[0].start()
    end = next((m.start() for m in headings if m.start() > start), len(text))
    old = text[start:end].rstrip()
    if re.search(r"<(?:page|folder|database|synced-block)\b|^\s*- \[[ xX]\]|<todo\b", old, re.M):
        return {"status": "NeedsCorrection", "reason": "Section contains native children or operator controls; use supported smaller block edits"}
    if old == replacement:
        return {"status": "NoChange", "reason": "Current saved section already matches; no write needed"}
    native = r'<(?:mention|date|link-preview|embed|image|file|pdf|audio|video|bookmark|custom-block|synced-block-reference)\b'
    if re.search(native, visible_markdown(old)) or re.search(native, visible_markdown(replacement)):
        return {"status": "NeedsCorrection", "reason": "Native references are unsafe whole-section match anchors; use a separate plain-text status section or supported smaller block edit"}
    if text.count(old) != 1:
        return {"status": "NeedsCorrection", "reason": "Exact saved section is not unique"}
    return {"status": "PatchPlanned", "old_str": old, "new_str": replacement,
            "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "scope": "Exact fetched workflow-owned section only; caller must preserve inputs/children and current invocation limits"}


def check_preview(data):
    """Verify a saved native embed and the exact downloaded HTML bytes."""
    file_id, digest = data["html_file_id"], data["html_sha256"]
    if not re.fullmatch(r"[0-9a-fA-F-]{32,36}", file_id) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Expected original HTML upload ID and SHA-256")
    text = visible_markdown(page_body(data["page"]))
    sources = re.findall(r'<embed\b[^>]*\bsource="([^"]+)"', text)
    expected = "file-upload://" + file_id
    saved_source = expected
    if expected not in sources:
        asset = data.get("embedded_asset", {})
        saved_source = asset.get("source", "")
        payload = object_result(data["page"])
        refs = payload.get("references") or payload.get("metadata", {}).get("references", {})
        if (not saved_source.startswith("notion-file-block://") or saved_source not in sources
                or not asset.get("resolved_url") or refs.get(saved_source) != asset["resolved_url"]):
            return {"status": "NeedsCorrection", "reason": "No matching saved native HTML embed or actual stable-reference download mapping",
                    "sources": sources, "scope": "Raw URI/file/code is not a preview; stable references require original fetched mapping and downloaded bytes"}
        if urlsplit(asset["resolved_url"]).scheme != "https":
            raise ValueError("Expected actual HTTPS URL resolved by the current Notion fetch")
        try:
            embedded_bytes = base64.b64decode(asset.get("content_base64", ""), validate=True)
        except (ValueError, TypeError) as exc:
            raise ValueError("Expected exact base64 bytes downloaded from the resolved saved embed") from exc
        if hashlib.sha256(embedded_bytes).hexdigest() != digest:
            return {"status": "NeedsCorrection", "reason": "Saved embedded asset differs from frozen HTML"}
    downloaded = object_result(data["download"])
    content = downloaded.get("content")
    if (downloaded.get("file_upload_id") != file_id or not isinstance(content, str)
            or downloaded.get("content_type", "").split(";")[0].strip().lower() != "text/html"):
        return {"status": "NeedsCorrection", "reason": "Original HTML download identity/type/UTF-8 content missing or mismatched"}
    actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if actual != digest:
        return {"status": "NeedsCorrection", "reason": "Downloaded HTML differs from frozen version", "actual_sha256": actual}
    return {"status": "SavedEmbedAndBytesMatch", "source": saved_source, "sha256": actual,
            "entity_id": object_result(data["page"]).get("id"),
            "scope": "Saved block and exact HTML bytes only; editable-copy agreement, review, host visual and send checks remain separate"}


def page_id(value):
    if not isinstance(value, str):
        raise ValueError("Expected a registered Notion page/data-source ID")
    if value.startswith("collection://"):
        value = value[len("collection://"):]
    elif value.startswith("https://app.notion.com/p/"):
        value = urlsplit(value).path[len("/p/"):].rstrip("/")
    compact = value.replace("-", "").lower()
    if not re.fullmatch(r"[0-9a-f]{32}", compact):
        raise ValueError("Use actual registered Notion IDs, not titles or guessed URLs")
    return compact


def page_links(data):
    """Check page content, excluding database/view documentation and fetch wrappers."""
    payload = object_result(data["page"])
    entity_type = payload.get("metadata", {}).get("type", payload.get("object"))
    if entity_type in {"database", "data_source", "view", "saved_view"}:
        return {"status": "ExcludedNonPage", "entity_type": entity_type, "entity_id": payload.get("id"),
                "reason": "Database/view schemas and tool descriptions are not page content"}
    if entity_type != "page":
        return {"status": "NeedsCorrection", "reason": "Page entity type is missing or unknown; no clean-page claim"}
    result = check_links(page_body(data["page"]), data.get("allowed_urls", []))
    result.update(entity_type="page", entity_id=payload.get("id"),
                  scope="Actual returned page content only; no fetch wrapper, schema docs, recursive children or host-visual guarantee")
    return result


def schema_values(data):
    """Validate proposed enum values against the original data-source state JSON."""
    payload = object_result(data["data_source"])
    if payload.get("metadata", {}).get("type") != "data_source":
        raise ValueError("Expected the actual data-source fetch, not a remembered enum list")
    states = re.findall(r'<data-source-state>\s*(.*?)\s*</data-source-state>', payload.get("text", ""), re.S)
    if len(states) != 1:
        raise ValueError("Missing or ambiguous actual data-source state")
    state = json.loads(states[0])
    target = page_id(data["data_source_id"])
    if page_id(payload["id"]) != target or page_id(state["url"]) != target:
        raise ValueError("Schema belongs to another target data source")
    properties, issues = data["properties"], []
    if not isinstance(properties, dict):
        raise ValueError("Expected the exact proposed properties")
    for key, value in properties.items():
        name = key.split(":")[1] if key.startswith("date:") and len(key.split(":")) > 2 else key
        prop = state["schema"].get(name)
        if prop is None or prop.get("readOnly") is True:
            issues.append({"property": key, "reason": "Unknown or read-only property"})
            continue
        kind = prop.get("type")
        if kind not in {"select", "multi_select", "status"} or value is None:
            continue
        options = prop.get("options", prop.get(kind, {}).get("options", []))
        names = [o["name"] for o in options]
        values = value if kind == "multi_select" and isinstance(value, list) else [value]
        if (kind == "multi_select" and not isinstance(value, list)) or any(v not in names for v in values):
            issues.append({"property": key, "reason": "Invalid enum value; do not add an option automatically", "allowed": names})
    return {"status": "NeedsCorrection" if issues else "ValidSelectValues", "issues": issues,
            "entity_id": payload["id"], "scope": "Current enum/property preflight only; other types and permissions still require the actual tool schema"}


def task_display(data):
    """Find stale current instructions across status, result and input sections."""
    body, task = page_body(data["page"]), data["task"]
    version = task.get("ContentVersion")
    if not isinstance(version, str) or not version or not task.get("State"):
        raise ValueError("Expected canonical State and ContentVersion")
    aliases = {"status": {"Current status", "\u5f53\u524d\u72b6\u6001"},
               "result": {"Processing result", "\u5904\u7406\u7ed3\u679c"},
               "input": {"Your input", "\u60a8\u7684\u8f93\u5165"}}
    headings = list(re.finditer(r"^## ([^\n]+)", visible_markdown(body), re.M))
    sections = {k: [] for k in aliases}
    for i, match in enumerate(headings):
        for role, names in aliases.items():
            if match.group(1).strip() in names:
                end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
                sections[role].append(body[match.end():end])
    issues = []
    for role in ("status", "result"):
        if len(sections[role]) != 1:
            issues.append({"section": role, "reason": "Missing or repeated current section"})
    if len(sections["input"]) > 1:
        issues.append({"section": "input", "reason": "Repeated current input section"})
    if sections["status"] and not re.search(r"(?<![\w-])" + re.escape(version) + r"(?![\w-])", sections["status"][0]):
        issues.append({"section": "status", "reason": "Current version is absent or stale"})
    terminal = task["State"] in {"Completed", "Cancelled"}
    recorded = bool(task.get("Decision")) and task.get("DecisionVersion") == version
    paused = recorded and task["Decision"] in {"Pause", "Postpone", "Cancel"}
    not_submitted = r"\b(?:not (?:yet )?submitted|awaiting submission)\b|\u5c1a\u672a\u63d0\u4ea4|\u672a\u63d0\u4ea4|\u7b49\u5f85\u63d0\u4ea4"
    request = r"\b(?:choose (?:exactly )?one|please select|submit (?:your|this))\b|\u8bf7\u9009\u62e9|\u8bf7\u63d0\u4ea4"
    for role, texts in sections.items():
        for text in texts:
            visible = visible_markdown(text)
            if (terminal or recorded) and re.search(not_submitted, visible, re.I):
                issues.append({"section": role, "reason": "Unsubmitted instruction conflicts with recorded decision/result"})
            if (terminal or paused) and (re.search(request, visible, re.I) or re.search(r"^\s*- \[[ xX]\]|<todo\b", visible, re.M)):
                issues.append({"section": role, "reason": "Inactive step still requests input or has live controls"})
    payload = object_result(data["page"])
    return {"status": "NeedsCorrection" if issues else "DisplayConsistentForCheckedPatterns", "issues": issues,
            "entity_id": payload.get("id"), "scope": "Current owned status/result/input sections only; original answers, review material and labeled history are excluded; prose still needs owner review"}


def completion_gate(data):
    """Require current, successful results before a workflow records completion."""
    invocation, version = data.get("invocation_id"), data.get("publication_version")
    required, checks = data.get("required_checks"), data.get("checks")
    if not invocation or not version or not isinstance(required, dict) or not required or not isinstance(checks, list):
        raise ValueError("Expected frozen invocation/version, nonempty required checks and their actual results")
    passed_status = {"page-links": "ClearForCheckedPatterns", "task-display": "DisplayConsistentForCheckedPatterns",
                     "preview": "SavedEmbedAndBytesMatch", "schema-values": "ValidSelectValues"}
    by_name, issues = {}, []
    for item in checks:
        if not isinstance(item, dict) or item.get("name") not in required or item.get("name") in by_name:
            issues.append("Unknown, duplicate or malformed check result")
            continue
        by_name[item["name"]] = item
    for name, spec in required.items():
        item = by_name.get(name)
        if not isinstance(spec, dict) or spec.get("kind") not in passed_status:
            issues.append(name + ": unsupported check contract")
            continue
        if item is None:
            issues.append(name + ": missing check")
            continue
        result = item.get("result")
        if (item.get("invocation_id") != invocation or item.get("publication_version") != version
                or type(item.get("exit_code")) is not int or item["exit_code"] != 0
                or not isinstance(result, dict) or result.get("status") != passed_status[spec["kind"]]):
            issues.append(name + ": failed, stale or malformed result")
            continue
        if spec["kind"] == "page-links" and (result.get("entity_type") != "page" or result.get("issue_count") != 0):
            issues.append(name + ": page coverage or link check incomplete")
        if result.get("issues"):
            issues.append(name + ": unresolved findings")
        if spec.get("entity_id") is None or result.get("entity_id") is None or page_id(spec["entity_id"]) != page_id(result["entity_id"]):
            issues.append(name + ": missing or mismatched evidence target")
    return {"status": "NeedsCorrection" if issues else "EligibleForCompletion", "issues": issues,
            "invocation_id": invocation, "publication_version": version,
            "scope": "Offline current-result gate only; required checks must be frozen from actual workflow dependencies; no host enforcement, approval or business execution"}


def report_write(data):
    """Check a planned or captured mutation against this report invocation's registry."""
    registry, call = data["registry"], data["call"]
    reports = {page_id(x) for x in registry.get("report_page_ids", [])}
    runs = {page_id(x) for x in registry.get("report_run_page_ids", [])}
    logs = {page_id(x) for x in registry.get("operation_log_source_ids", [])}
    run_sources = {page_id(x) for x in registry.get("workflow_run_source_ids", [])}
    args, tool = call["args"], call["tool"]
    reason = "Unsupported report mutation; no fallback to a business owner inside report"
    allowed = False
    if tool.endswith("__notion_notion_update_page"):
        target = page_id(args.get("page_id"))
        command = args.get("command")
        if target in reports and command in {"update_content", "insert_content", "update_properties"}:
            # Report metadata uses actual schema; templates/verification/whole-page replacement are excluded.
            allowed = not any(k in args for k in ("template_id", "allow_deleting_content"))
        elif target in runs and command == "update_properties":
            keys = set(args.get("properties", {}))
            allowed = bool(keys) and keys <= {"State", "Status", "Result", "Summary", "CurrentStep",
                "date:FinishedAt:start", "date:FinishedAt:is_datetime", "date:EndedAt:start", "date:EndedAt:is_datetime",
                "date:LastActiveAt:start", "date:LastActiveAt:is_datetime"}
    elif tool.endswith("__notion_notion_create_pages"):
        parent = args.get("parent", {})
        if parent.get("data_source_id"):
            source = page_id(parent["data_source_id"])
            allowed = source in logs and bool(args.get("pages"))
            if source in run_sources:
                run_id = registry.get("report_run_id")
                allowed = isinstance(run_id, str) and bool(run_id.strip()) and bool(args.get("pages")) and all(
                    p.get("properties", {}).get("RunId") == run_id
                    and p.get("properties", {}).get("Skill") == "eightdegrees-daily-brief-and-handover"
                    for p in args["pages"])
            if not allowed:
                allowed = bool(args.get("pages")) and all(any(
                    s.get("parent_data_source_id") and page_id(s["parent_data_source_id"]) == source
                    and s.get("title_property") in {"Name", "title"}
                    and s["title"] == p.get("properties", {}).get(s["title_property"])
                    for s in registry.get("report_creations", [])) for p in args["pages"])
        else:
            # First report creation must be registered by exact parent/title after complete discovery.
            specs = registry.get("report_creations", [])
            parent_id = page_id(parent.get("page_id"))
            allowed = bool(args.get("pages")) and all(
                any(s.get("parent_page_id") and page_id(s["parent_page_id"]) == parent_id and s["title"] == p.get("properties", {}).get("title")
                    for s in specs) for p in args["pages"])
    final_result = False
    if tool.endswith("__notion_notion_update_page") and args.get("command") == "update_properties":
        props = args.get("properties", {})
        final_result = props.get("State", props.get("Status")) == "Completed" or props.get("Result") == "Success"
    elif tool.endswith("__notion_notion_create_pages"):
        final_result = any(p.get("properties", {}).get("State", p.get("properties", {}).get("Status")) == "Completed"
                           or p.get("properties", {}).get("Result") == "Success"
                           and p.get("properties", {}).get("Phase", "Result") == "Result" for p in args.get("pages", []))
    if allowed and final_result:
        evidence = data.get("completion")
        if not isinstance(evidence, dict):
            allowed, reason = False, "Final completion/success requires current completion-gate evidence"
        else:
            gate = completion_gate(evidence)
            covered = {page_id(s["entity_id"]) for s in evidence["required_checks"].values()
                       if s.get("kind") == "page-links" and s.get("entity_id")}
            if (gate["status"] != "EligibleForCompletion" or not reports <= covered
                    or evidence["invocation_id"] != registry.get("invocation_id")
                    or evidence["publication_version"] != registry.get("publication_version")):
                allowed, reason = False, "Failed/stale/incomplete publication checks block final completion/success"
    if allowed:
        reason = "Target and mutation kind match the supplied report-only registry"
    return {"status": "WithinReportScope" if allowed else "Deferred", "reason": reason,
            "scope": "Offline preflight/audit only, not host enforcement or authorization; registry must come from actual report/settings records"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    operations = {"section-patch": section_patch, "preview": check_preview, "report-write": report_write,
                  "page-links": page_links, "schema-values": schema_values, "task-display": task_display,
                  "completion-gate": completion_gate}
    parser.add_argument("command", choices=tuple(operations))
    parser.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        outcome = operations[args.command](json.loads(source))
        print(json.dumps(outcome, ensure_ascii=False))
        return 2 if outcome["status"] in {"NeedsCorrection", "Deferred"} else 0
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        print(json.dumps({"status": "NeedsCorrection", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
