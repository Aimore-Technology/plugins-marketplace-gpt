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

from workflow_checks import inspect_result, notion_text, visible_markdown


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
    if payload.get("truncated") is True or payload.get("unknown_block_count", 0):
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
    if allowed:
        reason = "Target and mutation kind match the supplied report-only registry"
    return {"status": "WithinReportScope" if allowed else "Deferred", "reason": reason,
            "scope": "Offline preflight/audit only, not host enforcement or authorization; registry must come from actual report/settings records"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("section-patch", "preview", "report-write"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        outcome = {"section-patch": section_patch, "preview": check_preview, "report-write": report_write}[args.command](json.loads(source))
        print(json.dumps(outcome, ensure_ascii=False))
        return 2 if outcome["status"] in {"NeedsCorrection", "Deferred"} else 0
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        print(json.dumps({"status": "NeedsCorrection", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
