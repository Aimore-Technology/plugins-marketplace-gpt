#!/usr/bin/env python3
"""Render operator guidance and native view plans offline; no execution or approval."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id, schema_values
from outcome_checks import counts, projection, sms_progress
from workflow_checks import submitted_manual_route

ROOT = Path(__file__).resolve().parents[1]
COPY = json.loads((ROOT / "assets/operator-copy.json").read_text())
ROUTES = json.loads((ROOT / "references/task-routes.json").read_text())


def words(data):
    language = data.get("language", "en")
    if language not in COPY:
        raise ValueError("Use the saved en or zh-CN workspace language")
    return COPY[language]


def line(value):
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise ValueError("Operator summaries need nonempty single-line text")
    for char in ("\\", "`", "*", "[", "]", "<", ">", "#"):
        value = value.replace(char, "\\" + char)
    return value


def _schema(capture):
    source = object_result(capture)
    if source.get("metadata", {}).get("type") != "data_source":
        raise ValueError("Read the original PendingTasks schema")
    if source.get("truncated") or source.get("unknown_block_count") or source.get("unknown_block_ids"):
        raise ValueError("Use the complete original schema capture")
    matches = re.findall(r"<data-source-state>\s*(.*?)\s*</data-source-state>", source["text"], re.S)
    if len(matches) != 1:
        raise ValueError("Missing or ambiguous original schema")
    state = json.loads(matches[0])
    if page_id(source["id"]) != page_id(state["url"]):
        raise ValueError("Schema identity differs")
    return source, state


def today_views(data):
    """Plan linked views over existing canonical tasks; never clone task rows."""
    copy = words(data)
    page = object_result(data["page"])
    if page.get("metadata", {}).get("type") != "page":
        raise ValueError("Read the actual Today page before planning placement")
    page_body(data["page"])
    source, state = _schema(data["pending_source"])
    required = {"Name", "Category", "State", "Decision", "ActionPageURL"}
    if not required <= state["schema"].keys():
        raise ValueError("Today setup needs the original task properties; no guessed schema")
    for key, values in {"Category": ["ClientMatching", "DataCompletion", "ContentReview", "SendApproval", "ExecutionExceptions"],
                        "State": ["WaitingForOperator", "NeedsCorrection", "ReadyToValidate", "InProgress", "Completed", "Cancelled"],
                        "Decision": ["Pause", "Postpone", "Confirm", "Approve", "Return", "Cancel"]}.items():
        for value in values:
            checked = schema_values({"data_source": data["pending_source"], "data_source_id": source["id"], "properties": {key: value}})
            if checked["status"] != "ValidSelectValues":
                raise ValueError("Current task options differ; explicit setup repair required")
    opened = '"State" != "Completed" AND "State" != "Cancelled"'
    needs_input = '("Decision" IS EMPTY OR "Decision" = "Return") AND "State" IN ("WaitingForOperator", "NeedsCorrection")'
    specs = [
        ("review", opened + ' AND "Category" IN ("ContentReview", "SendApproval") AND ' + needs_input),
        ("information", opened + ' AND "Category" IN ("ClientMatching", "DataCompletion") AND ' + needs_input),
        ("attention", opened + ' AND "Category" = "ExecutionExceptions" AND ' + needs_input),
        ("waiting", opened + ' AND ("State" IN ("InProgress", "ReadyToValidate") OR "Decision" IN ("Pause", "Postpone", "Confirm", "Approve", "Cancel"))')]
    sort = '"ObservedAt" DESC' if "ObservedAt" in state["schema"] else '"Name" ASC'
    views = [{"key": key, "args": {
        "parent_page_id": page["id"], "data_source_id": source["id"], "type": "list",
        "name": copy[key], "show_data_source_title": False,
        "configure": 'FILTER ' + predicate + '; SORT BY ' + sort + '; SHOW "Name", "ActionPageURL"'}} for key, predicate in specs]
    for name, required, predicate, sorting, columns in [
            ("runs_source", {"Name", "RecordType", "State", "Summary", "LastActiveAt"},
             '\"RecordType\" = \"Business\" AND \"State\" IN (\"Completed\", \"Error\", \"Unknown\")',
             '\"LastActiveAt\" DESC', '\"Name\", \"Summary\", \"LastActiveAt\"'),
            ("brief_source", {"Name", "State", "BusinessDate", "DataCutoff"},
             '\"State\" = \"Completed\"', '\"BusinessDate\" DESC', '\"Name\", \"DataCutoff\"')]:
        if name not in data:
            continue
        extra_source, extra_state = _schema(data[name])
        if not required <= extra_state["schema"].keys():
            raise ValueError("Results view needs its actual original schema")
        values = [{"RecordType": "Business", "State": x} for x in ("Completed", "Error", "Unknown")] if name == "runs_source" else [{"State": "Completed"}]
        for properties in values:
            checked = schema_values({"data_source": data[name], "data_source_id": extra_source["id"], "properties": properties})
            if checked["status"] != "ValidSelectValues":
                raise ValueError("Results view options differ from the original schema")
        key = "results" if name == "runs_source" else "briefs"
        views.append({"key": key, "args": {"parent_page_id": page["id"], "data_source_id": extra_source["id"],
            "type": "list", "name": copy[key], "show_data_source_title": False,
            "configure": 'FILTER ' + predicate + '; SORT BY ' + sorting + '; SHOW ' + columns}})
    task_layout = {"data_source_id": source["id"], "page_layout": {
        "main": [{"type": "title", "pinnedProperties": [], "propertyLabels": "hide"}, {"type": "editor"}, {"type": "discussions"}],
        "sidebar": [{"type": "properties", "properties": [{"property": name, "visibility": "hide"}
                     for name in sorted(state["schema"]) if name != "Name"]}]}}
    if "<page-layout" in source["text"]:
        task_layout = None  # Preserve customized/host-only layouts for explicit adaptation.
    return {"status": "TodayViewsPlanned", "views": views, "task_page_layout": task_layout,
        "scope": "Native display views only; reconcile existing IDs first; never replace execution-discovery views or authorize work"}


def feedback(data):
    copy, task = words(data), data["task"]
    state, mode = task["State"], task["Mode"]
    page_id(task["PageId"])
    if not task.get("ContentVersion"):
        raise ValueError("Use the original task's content version")
    if state not in {"WaitingForOperator", "NeedsCorrection", "ReadyToValidate", "InProgress", "Completed", "Cancelled"} or mode not in {"Manual", "Automatic"}:
        raise ValueError("Use actual canonical task state and mode")
    phase = data.get("submission", "not_observed")
    if phase not in {"not_observed", "requested", "accepted"}:
        raise ValueError("Unknown submission observation")
    accepted = data.get("accepted_snapshot")
    bound = bool(accepted and accepted.get("read_verified") is True
                 and accepted.get("task_id") == task.get("PageId")
                 and accepted.get("content_version") == task.get("ContentVersion")
                 and re.fullmatch(r"[0-9a-f]{64}", accepted.get("input_sha256", "")))
    if phase == "accepted" and not bound:
        raise ValueError("Accepted feedback needs the actual saved, version-bound input snapshot")
    decision = task.get("Decision") if task.get("DecisionVersion") == task.get("ContentVersion") else None
    stage, command = "input", None
    pending = data.get('reserved_outcome')
    if pending is not None:
        if pending.get('task_id') != task['PageId'] or pending.get('content_version') != task['ContentVersion']:
            raise ValueError('Pending feedback must use this original task/version')
        if projection(pending)['expected']['reserved'] is not True:
            raise ValueError('Pending feedback needs an actually observed reserved outcome')
    if data.get("result_unknown") is True:
        stage = "unknown"
    elif pending is not None:
        stage = 'stopped_pending' if data.get('future_sms_stopped') is True else 'external_pending'
    elif state in {"Completed", "Cancelled"}:
        stage = "completed" if state == "Completed" else "cancelled"
    elif decision in {"Pause", "Postpone"}:
        stage = "paused" if decision == "Pause" else "postponed"
    elif state == "InProgress" and task.get("ResumeStep") == "SendNotificationSms":
        stage = "queued"
    elif state == "InProgress":
        stage = "processing" if bound else "checking"
    else:
        stage = "accepted" if bound else "requested" if phase == "requested" else "input"
        if state == "NeedsCorrection" and phase == "not_observed" and not bound:
            stage = "correction"
        route = ROUTES.get(task.get("ResumeStep"))
        if (not route or route["owner"] != task.get("OwnerSkill")
                or task.get("Category") not in route["categories"] or task.get("ResumeContractVersion") != "resume-v1"):
            raise ValueError("Missing actual owner/step binding; no guessed continuation")
        action = task["ActionPageURL"]
        page_id(action)
        schedule = data.get("schedule") or {}
        queue_eligible = mode == "Automatic" or submitted_manual_route(task) or task.get("ResumeStep") == "SendNotificationSms"
        native = (queue_eligible and route["effect"] != "setup" and schedule.get("enabled") is True
                  and schedule.get("state") == "Running" and schedule.get("approved_work_enabled") is True
                  and schedule.get("read_verified") is True
                  and bool(schedule.get("schedule_id")))
        if native:
            stage = "scheduled" if phase != "not_observed" or bound else "input"
        else:
            if queue_eligible:
                command = "@eightdegrees-sales-workflow run-auto" if route["effect"] != "setup" else "@eightdegrees-sales-workflow init"
            # Legacy Manual sends remain Manual. Do not fabricate a private
            # command or suggest a public scanner that cannot adopt this work.
    window = data.get("approved_window") or {}
    if window and stage not in {"completed", "cancelled", "paused", "postponed", "unknown", "external_pending", "stopped_pending"}:
        if (window.get("read_verified") is not True or window.get("content_version") != task.get("ContentVersion")
                or window.get("task_id") != task["PageId"]):
            raise ValueError("Display only the actual current approved window")
        end, now = (datetime.fromisoformat(x.replace("Z", "+00:00")) for x in (window["send_not_after"], data["now"]))
        if end.tzinfo is None or now.tzinfo is None:
            raise ValueError("Window feedback requires timezone-aware observations")
        if now > end:
            stage, command = "expired", None
    return {"status": "OperatorFeedbackReady", "stage": stage, "message": copy[stage],
            "continue_command": command, "last_checked_at": data.get("observed_at"),
            "scope": "Presentation only; saved edits/submission requests are not acceptance, approval, execution or a schedule"}


def review_brief(data):
    copy = words(data)
    rows = [(copy["request"], data["customer_request"]), (copy["response"], data["proposed_response"]),
            (copy["decision"], data["decision_needed"])]
    markdown = "\n\n".join("**" + label + "** " + line(value) for label, value in rows)
    changes = data.get("changes", [])
    if changes:
        markdown += "\n\n### " + copy["changes"]
        for change in changes:
            markdown += "\n\n- " + line(change["field"]) + ": " + line(change["before"]) + " → " + line(change["after"])
    confirmed, inputs = [], []
    for field in data.get("fields", []):
        value = field.get("value")
        if value not in (None, "") and field.get("verified") is True and field.get("applicable") is True and field.get("source") and not field.get("error"):
            confirmed.append({"label": field["label"], "value": value, "source": field["source"]})
        else:
            inputs.append({**field, "required": field.get("required", True)})
    return {"status": "ReviewBriefReady", "summary_markdown": markdown, "reused_fields": confirmed,
            "editable_fields": inputs, "scope": "Brief only; retain full exact-version material and preview before separate content/send decisions"}


def result_summary(data):
    copy = words(data)
    totals = counts(data)
    if totals["status"] != "OutcomeCountsDerived":
        return totals
    rows, seen = [], set()
    for event in data["events"]:
        derived = projection(event)
        expected = derived["expected"]
        operation = event["provider"]["operation"]
        key = (operation, event["account"], expected["message_id"])
        if key in seen:
            continue
        seen.add(key)
        receipt = copy["receipt_yes"] if expected["human_received"] else copy["receipt_no"]
        if operation == 'sms' and expected['sent'] and not expected['human_received']:
            receipt = copy['sms_confirmation_not_required']
        row = {"channel": copy[operation], "result": copy[expected["provider_status"]],
            "receipt": receipt,
            "observed_at": event.get("observed_at"), "source_url": event.get("source_url"),
            "task_id": derived["entity_id"], "message_id": expected["message_id"]}
        if operation == 'sms':
            progress = sms_progress(event)
            row.update({key: progress[key] for key in ('send_complete', 'query_original_request',
                                                       'requires_handset_confirmation')})
        rows.append(row)
    return {"status": "OperatorResultsReady", "rows": rows, "counts": totals,
            "scope": "Original outcome observations only; UI IDs support links and are not primary labels; no global absence or delivery inference"}


def final_response(data):
    """Produce clickable next-step/result links from existing original captures."""
    words(data)
    chinese = data.get('language') == 'zh-CN'
    links, seen = [], set()
    for key, label in [('action_page', '\u53bb\u5904\u7406' if chinese else 'Take action'),
                       ('result_page', '\u67e5\u770b\u7ed3\u679c' if chinese else 'View result'),
                       ('today_page', '\u4eca\u65e5\u5165\u53e3' if chinese else 'Today')]:
        if key not in data:
            continue
        capture = data[key]
        original = object_result(capture)
        page_body(capture)
        if original.get('metadata', {}).get('type') != 'page':
            raise ValueError('A response link needs its original page capture')
        identity = page_id(original['id'])
        if identity not in seen:
            seen.add(identity)
            links.append({'label': label, 'url': 'https://app.notion.com/p/' + identity})
    if not links:
        raise ValueError('Return at least one actual result/action link; do not name an unlinked page')
    markdown = line(data['result']) + '\n\n' + line(data['next_action']) + '\n\n'
    markdown += ' · '.join('[' + x['label'] + '](' + x['url'] + ')' for x in links)
    return {'status': 'OperatorResponseReady', 'markdown': markdown, 'links': links,
            'scope': 'Presentation only; reuse current captures, no additional business action or Notion write'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("today-views", "feedback", "review", "results", "response"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = {"today-views": today_views, "feedback": feedback, "review": review_brief,
                  "results": result_summary, "response": final_response}[args.command](json.loads(raw))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"TodayViewsPlanned", "OperatorFeedbackReady", "ReviewBriefReady", "OperatorResultsReady", "OperatorResponseReady"} else 2


if __name__ == "__main__":
    sys.exit(main())
