"""Offline phase boundaries shared by preparation and final-write checks."""

import json
from pathlib import Path


ROUTES = json.loads((Path(__file__).resolve().parents[1] / "references/task-routes.json").read_text())
MINIMUM_EVIDENCE = {
    "ReviewReplyDraft": ("reply-draft",),
    "SendApprovedReply": ("reply-draft", "reply-sent", "outcome", "crm-receipt", "material-handoff", "email-presentation"),
    "SendGeneralReply": ("reply-draft", "reply-sent", "outcome", "crm-receipt"),
    "RecordSendReceipt": ("outcome", "crm-receipt"),
    "RecordGeneralSendReceipt": ("outcome", "crm-receipt"),
    "RecordMaterialHandoff": ("material-handoff",),
    "RefreshEmailOutcome": ("email-presentation",),
    "SendApprovedSms": ("outcome",),
    "SendNotificationSms": ("sms-authority", "outcome"),
    "RefreshSmsOutcome": ("sms-presentation",),
    "RefreshContactRestrictions": ("contact-restriction",),
}


def task_evidence(resource):
    """Generate only this step's obligations, never a successor's outcomes."""
    step = resource.get("resume_step")
    if step not in ROUTES:
        raise ValueError("Every task needs its canonical resume_step before preparation")
    minimum = MINIMUM_EVIDENCE.get(step, ())
    allowed = set(minimum)
    if ROUTES[step]["effect"] == "draft":
        allowed.add("reply-draft")
    extra = resource.get("evidence", [])
    if not isinstance(extra, list) or any(not isinstance(x, str) for x in extra) or len(extra) != len(set(extra)):
        raise ValueError("Task evidence must be a unique list of check kinds")
    if not set(extra) <= allowed:
        raise ValueError("Evidence belongs to another phase; future results cannot gate " + step)
    return (*minimum, *(kind for kind in extra if kind not in minimum))


def validate_phase(resources, owner, policy):
    """One current resume step per plan; successors get separate persisted plans."""
    steps = set()
    for resource in resources:
        if resource.get("type") != "task":
            continue
        task_evidence(resource)
        step = resource["resume_step"]
        route = ROUTES[step]
        if route["owner"] != owner:
            raise ValueError("Task resume_step belongs to another owner")
        if route["effect"] == "customer-send" and policy in {
                "setup-only", "scheduling-only", "manual-review", "one-cycle-no-customer-send", "draft-only", "report-only"}:
            raise ValueError("Invocation policy does not allow this sending phase")
        steps.add(step)
    if len(steps) > 1:
        raise ValueError("Mixed completion phases; prepare a separate plan for each resume_step")
    return next(iter(steps), None)
