#!/usr/bin/env python3
"""Prepare exact Notion write arguments offline; never execute a connector."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id, schema_values
from workflow_checks import check_links
from review_release import gate_mutation
from runtime_records import validate as validate_run

SCOPE = "Exact proposed call only; no host interception, scope permission or retrospective order proof"
IDENTITY_FIELDS = {"TaskId", "RunId", "ParentRunId", "StepId", "SourceKey", "ClientId", "ContactId", "LocationId", "OperatorId", "ApproverId", "ContentVersion", "DecisionVersion", "OwnerSkill", "ResumeStep", "ResumeContractVersion", "CycleId", "AttemptId"}


def prepare(data):
    call = data["call"]
    args, tool = call["args"], call["tool"]
    texts, properties, source, checks = [], [], None, []
    if not isinstance(args, dict):
        raise ValueError("Supply the exact tool arguments")
    if tool.endswith("__notion_notion_create_pages"):
        parent, pages = args.get("parent") or {}, args["pages"]
        if not isinstance(pages, list) or not pages:
            raise ValueError("A page batch must contain actual proposed pages")
        if args.get("creation_mode") == "draft" and not parent:
            pass  # Host-supported durable private root; no fabricated parent.
        elif args.get("creation_mode") == "draft":
            raise ValueError("Draft creation cannot also name a parent")
        elif parent.get("data_source_id"):
            source = parent["data_source_id"]
        elif parent.get("page_id"):
            _page(data["target"], parent["page_id"])
        else:
            raise ValueError("Root creation needs separate host/setup handling")
        for page in pages:
            properties.append(page["properties"])
            if not source and not page["properties"].get("title"):
                raise ValueError("An ordinary new page needs its actual title")
            if "content" in page:
                texts.append(page["content"])
    elif tool.endswith("__notion_notion_update_page"):
        target = _page(data["target"], args["page_id"])
        command = args["command"]
        if command == "update_properties":
            properties.append(args.get("properties", {}))
            # A schema appendix is documentation, not another parent. A word
            # boundary also matches the hyphen in parent-data-source-schema.
            parents = re.findall(r'<parent-data-source(?=\s|>)[^>]*\burl="([^"\n]+)"', target.get("text", ""))
            if len(parents) > 1:
                raise ValueError("Ambiguous original parent data source")
            source = parents[0] if parents else None
        elif command in {"insert_content", "replace_content"}:
            texts.append(args["content"] if command == "insert_content" else args["new_str"])
        elif command == "update_content":
            edits = args["content_updates"]
            if not isinstance(edits, list) or not edits:
                raise ValueError("Supply actual targeted edits")
            for edit in edits:
                if not isinstance(edit["old_str"], str) or not edit["old_str"]:
                    raise ValueError("An edit needs its actual nonempty anchor")
                texts.append(edit["new_str"])
        else:
            raise ValueError("Unsupported mutation; no guessed fallback")
        if args.get("allow_deleting_content"):
            raise ValueError("Destructive replacement is outside this helper")
    else:
        raise ValueError("Not a supported Notion page write")

    # Run both kinds before emitting ANY executable arguments, including initial
    # inert run/task/action creation and metadata-only result/log updates.
    for index, text in enumerate(texts):
        result = check_links(text, data.get("allowed_urls", []))
        checks.append({"kind": "notion-links", "index": index, "result": result})
    for index, props in enumerate(properties):
        if not isinstance(props, dict):
            raise ValueError("Properties must be the exact proposed object")
        run_props = props
        creating = tool.endswith('__notion_notion_create_pages')
        if not creating and 'target' in data:
            from email_presentation import properties as saved_properties
            run_props = {**saved_properties(data['target']), **props}
        if source:
            payload = object_result(data['data_source'])
            schemas = re.findall(r'<data-source-state>\s*(.*?)\s*</data-source-state>', payload.get('text', ''), re.S)
            if len(schemas) == 1 and {'RecordType', 'RunId', 'SkillVersion'} <= json.loads(schemas[0])['schema'].keys():
                if run_props.get('RecordType') not in {'Scan', 'Business', 'Initialization'}:
                    raise ValueError('WorkflowRun must declare its actual RecordType and identity')
        validate_run(run_props, creating=creating)
        for field in IDENTITY_FIELDS & props.keys():
            value = props[field]
            if isinstance(value, str) and re.search(r'\[[^\]]*\]\(|<\/?(?:mention|page|a)\b|[`*\n\r]', value):
                raise ValueError("Canonical " + field + " contains display markup; recover exact source identity before the first write")
        if source:
            result = schema_values({"data_source": data["data_source"],
                                    "data_source_id": source, "properties": props})
        else:
            if set(props) - {"title"} or any(not isinstance(v, str) for v in props.values()):
                raise ValueError("Ordinary-page writes only accept the title property")
            result = {"status": "ValidOrdinaryPageProperties"}
        checks.append({"kind": "properties", "index": index, "result": result})
    if any(c["result"]["status"] == "NeedsCorrection" for c in checks):
        return {"status": "NeedsCorrection", "checks": checks, "scope": SCOPE}
    review = gate_mutation(data, texts)
    if review is not None:
        checks.append({"kind": "email-review-release", "result": review})
    encoded = json.dumps(call, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return {"status": "NotionMutationPrepared", "call": copy.deepcopy(call),
            "call_sha256": hashlib.sha256(encoded.encode()).hexdigest(), "checks": checks, "scope": SCOPE}


def _page(capture, expected):
    page = object_result(capture)
    if page.get("metadata", {}).get("type") != "page" or page_id(page["id"]) != page_id(expected):
        raise ValueError("Use the original target/parent page fetch")
    page_body(capture)  # Reject truncated/omitted captures before mutation.
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", help="Save the exact checked call locally and print a small summary")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = prepare(json.loads(raw))
        if args.output:
            output = Path(args.output)
            if args.input != "-" and output.resolve() == Path(args.input).resolve():
                raise ValueError("Do not overwrite the original input capture")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False), encoding="utf-8")
            result = {k: v for k, v in result.items() if k != "call"}
            result["output_file"] = str(output)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)], "scope": SCOPE}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result["status"] == "NotionMutationPrepared" else 2


if __name__ == "__main__":
    sys.exit(main())
