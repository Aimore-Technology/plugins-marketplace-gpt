#!/usr/bin/env python3
"""Batch local checks and private capture/project-cache I/O; never call a connector."""

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
import email_presentation
import notion_mutation
import sms_presentation
import contact_preferences
import scan_cycle
import sms_channel
import provider_handoff
import event_probe
import dispatch_admission
import review_release
import runtime_records
import connector_capture
import discovery_watch
import intake_handoff
import invocation_context
import scan_control
import backlog_recovery
import cycle_metrics
import current_rules
import configuration_audit
import queue_construction
import inquiry_intake
import communication_intake
import api_result
import email_flow
import project_cache
import capture_bundle
import consent_review
import exception_presentation
import task_submission

OPERATIONS = {
    "exception.presentation": exception_presentation.plan,
    "operator.system-view": exception_presentation.system_view,
    "email.review-repair": consent_review.repair_publication,
    "task.submission": task_submission.observe,
    "operator.today-views": operator_experience.today_views,
    "email.consent-read-plan": consent_review.read_plan,
    "email.consent-observe": consent_review.observe,
    "email.view-plan": consent_review.view_plan,
    "capture.commit": capture_bundle.commit,
    "notification.dispatch": sms_authority.dispatch,
    "project.cache-put": project_cache.put,
    "project.cache-get": project_cache.get,
    "project.cache-catalog": project_cache.catalog,
    "project.cache-match": project_cache.match,
    "project.cache-invalidate": project_cache.invalidate,
    "email.prepare": email_flow.prepare,
    "email.review": email_flow.render,
    "email.accept": email_flow.accept,
    "email.dispatch": email_flow.dispatch,
    "email.complete": email_flow.complete,
    "write.confirm": api_result.confirm,
    "communication.read-plan": communication_intake.plan,
    "communication.note": communication_intake.note,
    "inquiry.name": inquiry_intake.name,
    "inquiry.label": inquiry_intake.label,
    "scan.queue": queue_construction.build,
    "setup.audit": configuration_audit.audit,
    "scheduled.rules": current_rules.load,
    "backlog.recover": backlog_recovery.plan,
    "cycle.metrics": cycle_metrics.summarize,
    "scan.entry": scan_control.gate,
    "scan.control-plan": scan_control.plan,
    "scan.control-verify": scan_control.verify,
    "run.record": runtime_records.prepare,
    "run.legacy-projection": runtime_records.legacy_projection,
    "intake.handoff": intake_handoff.verify,
    "intake.plan": intake_handoff.plan,
    "invocation.prepare": invocation_context.prepare,
    "invocation.resume": invocation_context.resume,
    "checkpoint.reconcile": scan_cycle.reconcile,
    "connector.capture": connector_capture.normalize,
    "scan.watches": discovery_watch.plan,
    "notion.page-links": notion_checks.page_links,
    "notion.schema-values": notion_checks.schema_values,
    "notion.task-display": notion_checks.task_display,
    "notion.task-summary": notion_checks.task_summary,
    "notion.preview": notion_checks.check_preview,
    "notion.preview-image": notion_checks.check_image_preview,
    "notion.completion-gate": notion_checks.completion_gate,
    "execution.prepare": execution_preflight.prepare,
    "execution.ready": execution_preflight.ready,
    "facts.canonical": fact_checks.canonical_facts,
    "outcome.verify": outcome_checks.verify_projection,
    "outcome.display": outcome_checks.current_display,
    "sms.progress": outcome_checks.sms_progress,
    "send.progress": outcome_checks.send_progress,
    "provider.handoff": provider_handoff.verify,
    "operator.feedback": operator_experience.feedback,
    "operator.review": operator_experience.review_brief,
    "operator.results": operator_experience.result_summary,
    "operator.response": operator_experience.final_response,
    "material.plan": material_handoff.plan,
    "material.verify": material_handoff.verify,
    "material.dispatch-guard": material_handoff.dispatch_guard,
    "sms.prepare": sms_authority.prepare,
    "sms.verify": sms_authority.verify,
    "notion.mutation": notion_mutation.prepare,
    "notion.owner-write": notion_checks.owner_write,
    "notion.report-write": notion_checks.report_write,
    "email.presentation-plan": email_presentation.plan,
    "email.presentation-verify": email_presentation.verify,
    "sms.presentation-plan": sms_presentation.plan,
    "sms.presentation-verify": sms_presentation.verify,
    "contact.restriction-plan": contact_preferences.stop_overlay,
    "contact.restriction-verify": contact_preferences.verify,
    "contact.dispatch-gate": contact_preferences.dispatch_gate,
    "scan.cycle": scan_cycle.advance,
    "scan.probe": event_probe.probe,
    "dispatch.admit": dispatch_admission.prepare,
    "dispatch.prepare": dispatch_admission.release,
    "review.prepare": review_release.prepare,
    "sms.channel-check": sms_channel.gate,
}
PASSED = {"ExceptionPresentationPlanned", "ExceptionPresentationUnchanged", "SystemRecoveryViewPlanned", "EmailReviewPublicationPlanned", "EmailReviewPublicationUnchanged", "TaskSubmissionQueued", "TaskSubmissionUnchanged", "TaskSubmissionProjectionRepair", "TodayViewsPlanned", "ConsentReadPlanPrepared", "EmailConsentPending", "EmailConsentObserved", "ConsentViewPlanned", "CaptureBundleSaved", "CaptureBundleUnchanged", "SMSDispatchPrepared", "SMSDispatchDeferred", "ProjectCacheUnavailable", "ProjectCacheStored", "ProjectCacheHit", "ProjectCacheMiss", "ProjectCacheRefreshRequired",
          "ProjectCatalogLoaded", "ProjectMatched", "NeedsProjectSelection", "ProjectCacheInvalidated",
          "SingleEmailReviewPrepared", "SingleEmailReviewRendered", "EmailDecisionAccepted", "EmailRevisionRequired", "EmailDispatchDeferred", "EmailDispatchPrepared", "EmailRecordingPending", "EmailHandoffRecorded", "APIWriteConfirmed", "CommunicationReadPlanPrepared", "CommunicationNotePrepared","InquiryNameResolved", "InquiryLabelPlanned","ReadyQueueConstructed", "ConfigurationAuditPrepared", "CurrentScheduledRulesLoaded", "BacklogRecoveryPlanned", "CycleMetricsPrepared","ScanEnabled", "ScanStopped", "ScanControlPlanned", "ScanningEnabled", "ScanningStopped","RunRecordPrepared", "LegacyRunProjectionPrepared", "IntakeCheckpointPlanned", "IntakeHandoffVerified", "InvocationContextPrepared", "InvocationResumeChecked", "CheckpointReconciled", "ConnectorCaptureRecorded", "DiscoveryWatchesPrepared", "ClearForCheckedPatterns", "ValidSelectValues", "DisplayConsistentForCheckedPatterns",
          "SavedEmbedAndBytesMatch", "SavedImageAndBytesMatch", "EligibleForCompletion",
          "PreflightPrepared", "ExecutionPlanReady", "ValidFactSemantics", "OutcomeProjectionsVerified",
          "CurrentOutcomeDisplayVerified", "OperatorFeedbackReady", "ReviewBriefReady", "OperatorResultsReady",
          "MaterialHandoffPlanned", "MaterialHandoffVerified", "MaterialNotificationEligible", "SMSNotificationPrepared", "SMSNotificationVerified",
          "NotionMutationPrepared", "WithinOwnerScope", "WithinReportScope",
          "EmailPresentationPlanned", "EmailPresentationVerified", "OperatorResponseReady",
          "SMSPresentationPlanned", "SMSPresentationVerified", "ContactRestrictionPlanned", "ContactRestrictionVerified", "ContactDispatchChecked",
          "ScanCyclePlanned", "ScanDeferred", "ScanIdle", "ScanWorkReady", "ScanDiscoveryRequired", "DispatchAdmissionPrepared", "DispatchArgumentsPrepared", "EmailReviewReady", "ChannelCheckEligible", "ChannelCheckBlocked", "SMSProgressChecked", "DispatchProgressChecked", "ProviderHandoffVerified"}


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
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            result = {"status": "NeedsCorrection", "issues": [str(exc)]}
        code = 0 if result.get("status") in PASSED and not result.get("issues") else 2
        results[check["name"]] = {"name": check["name"], "operation": check["operation"], "exit_code": code, "result": result}
        if code:
            break
    passed = len(results) == len(checks) and all(c["exit_code"] == 0 for c in results.values())
    if not passed:
        for checked in results.values():
            checked['result'].pop('call', None)
            checked['result'].pop('writes', None)
    return {"status": "LocalChecksPassed" if passed else "NeedsCorrection",
            "checks": list(results.values()), "capture_hashes": hashes, "capture_references": references,
            "distinct_captures_used": len(hashes), "checks_requested": len(checks), "checks_run": len(results),
            "scope": "Local checks and private project material cache only; no connector I/O, inferred approval, provider mutation or historical order proof"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--captures", help="Existing capture dictionary/bundle; omit to use inline plan.captures")
    parser.add_argument("--output", help="Save full check results/exact calls and print only small summaries")
    args = parser.parse_args()
    try:
        plan = json.loads(sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8"))
        captures = capture_bundle.merge_originals(
            capture_bundle.unpack(json.loads(Path(args.captures).read_text(encoding='utf-8'))) if args.captures else {},
            plan.get('captures', {}))
        result = run(plan, captures)
        if args.output:
            output = Path(args.output)
            protected = [Path(args.captures).resolve()] if args.captures else []
            if args.input != "-":
                protected.append(Path(args.input).resolve())
            protected += [Path(c['result']['bundle_path']).resolve() for c in result.get('checks', [])
                          if c['operation'] == 'capture.commit' and c['result'].get('bundle_path')]
            if output.resolve() in protected:
                raise ValueError("Do not overwrite captures or the check plan")
            artifact = {**result, 'record_type': 'local-check-phase-v1',
                        'captures': captures, 'plan': {k:v for k,v in plan.items() if k != 'captures'}}
            written = capture_bundle.save_private(output, artifact)
            result = {**result, "checks": [{"name": c["name"], "operation": c["operation"],
                       "exit_code": c["exit_code"], "status": c["result"]["status"],
                       "issues": c["result"].get("issues", []),
                       "call_sha256": c["result"].get("call_sha256")} for c in result["checks"]],
                      "output_file": str(output), "output_written": written,
                      "original_inputs_saved": True, "separate_capture_save_required": False}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result["status"] == "LocalChecksPassed" else 2


if __name__ == "__main__":
    sys.exit(main())
