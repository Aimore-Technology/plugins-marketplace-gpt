#!/usr/bin/env python3
"""Plan and verify persisted email-to-SMS handoff; no connectors or sends."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from notion_checks import object_result, page_body, page_id
from email_presentation import blocks

SCOPE = "Offline normalized-evidence checks only; not provider verification, approval, a scheduler or an execution lock"


def token(value):
    if not isinstance(value, str) or not value or re.search(r'\s|[<>`\[\]()]', value):
        raise ValueError("Use an exact machine identity, not display Markdown")
    return value


def stamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Actual send time must include a timezone")
    return result.astimezone(timezone.utc)


def key(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def context_authorization(data, identity, root, sent_at):
    """Read explicit initiation from the original settings, never a loose flag."""
    capture = data.get('saved_settings')
    if capture is None:
        return None, False
    payload = object_result(capture)
    if payload.get('metadata', {}).get('type') != 'page':
        raise ValueError('Read the original saved settings page for new-context authorization')
    settings = []
    for raw in re.findall(r'```json\s*\n(.*?)\n```', page_body(capture), re.S):
        value = json.loads(raw)
        if isinstance(value, dict) and 'settings_schema_version' in value:
            settings.append(value)
    if len(settings) != 1:
        raise ValueError('Require one original saved settings record')
    settings = settings[0]
    setup = settings['customer_setup']
    settings_id = page_id(payload['id'])
    if (page_id(setup['notion_root_id']) != root
            or page_id(setup['notion_ids']['settings']) != settings_id
            or setup['crm_location_id'] != identity['location_id']
            or setup['gmail_account'] != identity['account']):
        raise ValueError('Settings belong to another installation, account or CRM location')
    # A context stop is not a customer-global stop; uncertain/global scope stays
    # restrictive. CRM DND and fresh persona restrictions remain owner guards.
    restricted = False
    for scope, stop in settings.get('sms_stops', {}).items():
        if (stop.get('location_id') == identity['location_id']
                and stop.get('contact_id') == identity['contact_id']
                and stop.get('channel', 'sms') in ('sms', '*')
                and stop.get('stopped') is True):
            context = stop.get('context_key', scope)
            if context in ('*', identity['context_key'], None, ''):
                restricted = True
    override = settings['sms_follow_up'].get('context_overrides', {}).get(identity['context_key'])
    if override is None:
        return None, restricted
    enquiry = settings.get('enquiries', {}).get(identity['context_key'], {})
    source = data['event'].get('source_message_id')
    authority = settings['sms_notifications']
    if (override.get('explicitly_initiated') is not True
            or override.get('revoked_at') is not None
            or override.get('context_key', identity['context_key']) != identity['context_key']
            or not source or source != override.get('source_message_id')
            or source != enquiry.get('source_message_id')
            or enquiry.get('location_id') != identity['location_id']
            or enquiry.get('contact_id') != identity['contact_id']
            or override.get('recipient') != data.get('recipient')
            or enquiry.get('phone') != data.get('recipient')
            or not re.fullmatch(r'[0-9a-f]{32}', page_id(override.get('authorization_ref', '')) or '')
            or authority.get('policy') != 'notification-sms-v1'
            or authority.get('enabled') is not True or authority.get('revoked_at') is not None
            or authority.get('per_message_review_required') is not False
            or page_id(authority.get('root_id', '')) != root
            or authority.get('operator_id') != setup.get('operator_id')
            or not setup.get('operator_id')
            or settings['sms_follow_up'].get('automatic_sending_enabled') is not True):
        raise ValueError('Saved new-context initiation must match the current source, customer, recipient and standing policy')
    now = stamp(data['observed_at'])
    if now < sent_at:
        raise ValueError('Authorization observation cannot precede the Gmail handoff')
    expires = override.get('expires_at')
    if expires is not None and now >= stamp(expires):
        raise ValueError('Saved new-context authorization has expired; preserve it without dispatch')
    if override.get('starts_at') is not None and now < stamp(override['starts_at']):
        raise ValueError('New-context authorization is not yet effective')
    delay = override.get('first_delay_minutes', settings['sms_follow_up']['first_delay_minutes'])
    cap = override.get('max_messages_per_cycle_including_manual', 2)
    second = override.get('second_sms_allowed', cap == 2)
    if (type(delay) is not int or delay < 0 or type(cap) is not int or cap not in (1, 2)
            or type(second) is not bool or second != (cap == 2)):
        raise ValueError('Use an exact nonnegative delay and coherent one/two-message authorization limit')
    return {'settings_page_id': settings_id, 'authorization_ref': override['authorization_ref'],
            'root_id': root, 'location_id': identity['location_id'], 'contact_id': identity['contact_id'],
            'context_key': identity['context_key'], 'source_message_id': source,
            'recipient': data['recipient'], 'first_delay_minutes': delay,
            'maximum_count': cap, 'second_sms_allowed': second, 'expires_at': expires,
            'authorization_sha256': key(override)}, restricted


def blocked_registration(data, cycle, event_key, identity, root, email, authorization):
    """Recover only the original zero-attempt implementation-blocked stub."""
    if cycle.get('state') != 'BlockedImplementation' or authorization is None:
        return False
    capture = data.get('recovery_cycle_page')
    if capture is None:
        raise ValueError('Recover blocked registration from its original cycle-page readback')
    payload = object_result(capture)
    current = blocks(capture, 'sms-cycle-current-state')[1]
    original = blocks(capture, 'material-handoff-v1')[1]
    if (payload.get('metadata', {}).get('type') != 'page'
            or page_id(payload['id']) != page_id(cycle['page_id'])
            or original.get('event_key') != event_key or original.get('root_id') != root
            or page_id(original.get('email_task_id', '')) != email
            or any(original.get(k) != v for k, v in identity.items())
            or original.get('cycle_key') != cycle['cycle_key']
            or current.get('cycle_id') != cycle['cycle_key']
            or current.get('blocked_reason') != 'ClosedPriorContextBlocksExplicitNewContext'
            or current.get('state') != 'BlockedImplementation'
            or any(current.get(k) != identity[k] for k in ('location_id', 'contact_id', 'context_key'))
            or current.get('source_message_id') != authorization['source_message_id']
            or not isinstance(current.get('authorization'), dict)
            or key(current['authorization']) != authorization['authorization_sha256']
            or current.get('maximum_count') != authorization['maximum_count']
            or current.get('second_sms_allowed') is not authorization['second_sms_allowed']
            or current.get('active') is not False or current.get('stop') is not False
            or current.get('manual_pause') is not False
            or type(current.get('total_count')) is not int or current['total_count'] != 0
            or type(current.get('reserved_slots')) is not int or current['reserved_slots'] != 0
            or type(current.get('reserved_count', 0)) is not int or current.get('reserved_count', 0) != 0
            or cycle['total_count'] != 0 or cycle['active'] is not False
            or event_key not in cycle['material_events']
            or any(current.get(k) is not None for k in ('current_outcome', 'last_request_id', 'last_attempt_id'))
            or current.get('attempts', []) != []
            or current.get('unknown_attempt', False) is not False):
        raise ValueError('Only the same unsent zero-reservation implementation block can resume; never reopen stopped/used/unknown work')
    return True


def plan(data):
    event = data["event"]
    if event.get("status") not in {"Sent", "ProviderAccepted"} or type(event.get("material")) is not bool:
        raise ValueError("Require an original successful Gmail handoff and explicit material classification; never enroll an unknown handoff")
    identity = {k: token(event[k]) for k in ("account", "provider", "message_id", "location_id", "contact_id", "context_key")}
    root, email = page_id(data["root_id"]), page_id(data["email_task_id"])
    if not all(re.fullmatch(r"[0-9a-f]{32}", x or "") for x in (root, email)):
        raise ValueError("Use the actual installation root and original email task IDs")
    sent_at = stamp(event["sent_at"])
    # Context/version updates do not change the actual provider-event identity.
    event_key = "material:" + key({"root": root, **{k: identity[k] for k in identity if k != "context_key"}})
    if event["material"] is False:
        return {"status": "MaterialHandoffPlanned", "record": {
            "contract": "material-handoff-v1", "event_key": event_key, "email_task_id": email,
            "content_version": token(data["content_version"]), "root_id": root, **identity,
            "sent_at": sent_at.isoformat(), "state": "NotApplicable", "material": False,
            "reason": "This verified reply did not deliver project materials; no SMS enrollment",
            "create_native_task": False, "customer_send_allowed": False}, "scope": SCOPE}
    if data.get("cycle_query_complete") is not True or not isinstance(data.get("cycles"), list):
        raise ValueError("Complete scoped cycle discovery is required before create/reuse")
    related, active = [], []
    for cycle in data["cycles"]:
        if cycle.get("location_id") != identity["location_id"] or cycle.get("contact_id") != identity["contact_id"]:
            raise ValueError("Cycle discovery must belong to this exact CRM customer")
        token(cycle["cycle_key"])
        if not re.fullmatch(r"[0-9a-f]{32}", page_id(cycle.get("page_id", "")) or ""):
            raise ValueError("Reuse requires the actual original cycle page identity before any write")
        if (type(cycle.get("total_count")) is not int or not 0 <= cycle["total_count"] <= 2
                or type(cycle.get("active")) is not bool or not isinstance(cycle.get("material_events"), list)
                or cycle.get("unknown_attempt") is not False
                or type(cycle.get('maximum_count', 2)) is not int or cycle.get('maximum_count', 2) not in (1, 2)
                or any(k in cycle and type(cycle[k]) is not bool for k in ('stop', 'manual_pause'))):
            raise ValueError("Unknown attempt/count or malformed cycle requires reconciliation, never a new cycle")
        if event_key in cycle["material_events"] or cycle.get("context_key") == identity["context_key"]:
            related.append(cycle)
        if cycle['active']:
            active.append(cycle)
    if (len(related) > 1 or len(active) > 1
            or related and active and related[0] is not active[0]):
        raise ValueError("Ambiguous related/active cycles; do not reset or create another")
    existing = (related or active or [None])[0]
    for field in ("stop", "manual_pause", "channel_verified", "automatic_sms_enabled"):
        if type(data.get(field)) is not bool:
            raise ValueError("Use an observed boolean for " + field)
    reasons = []
    authorization, scoped_stop = context_authorization(data, identity, root, sent_at)
    recovering = bool(existing and blocked_registration(data, existing, event_key, identity, root, email, authorization))
    limit = existing.get('maximum_count', 2) if existing else 2
    if authorization and (existing is None or existing.get('context_key') == identity['context_key']):
        limit = min(limit, authorization['maximum_count'])
    stopped = (data['stop'] or scoped_stop or data['manual_pause']
               or bool(existing and (existing.get('stop') is True or existing.get('manual_pause') is True
                                     or not existing['active'] and not recovering
                                     or existing['total_count'] >= limit)))
    if data["cycles"] and existing is None:
        if authorization is None:
            stopped = True
            reasons.append("Previous cycles exist; a different context requires explicit manual new-cycle authorization")
    if stopped:
        reasons.append("Customer stop, operator pause or closed/capped cycle; never reopen automatically")
    if not data.get("recipient"):
        reasons.append("Customer SMS number required")
    elif not re.fullmatch(r"\+[1-9][0-9]{7,14}", data["recipient"]):
        raise ValueError("Use a verified E.164 recipient or leave it missing")
    if not data["channel_verified"]:
        reasons.append("Own-number display, stable send and ordinary-inbox replies not verified")
    if not data["automatic_sms_enabled"]:
        reasons.append("Automatic SMS disabled; prepare only, do not silently enable")
    record = {"contract": "material-handoff-v1", "event_key": event_key,
              "material": True,
              "email_task_id": email, "content_version": token(data["content_version"]), "root_id": root, **identity,
              "sent_at": sent_at.isoformat(),
              "first_due_not_before": (sent_at + timedelta(minutes=30)).isoformat(),
              "cycle_key": existing["cycle_key"] if existing else "sms-cycle:" + key(event_key),
              "operation": "reuse" if existing else "create",
              "state": "Stopped" if stopped else "Blocked" if reasons else "ReadyForNotification",
              "total_count": existing["total_count"] if existing else 0,
              "reasons": reasons, "recipient": data.get("recipient"),
              "executor": "shared-approved-work", "create_native_task": False,
              "customer_send_allowed": False}
    if authorization is not None and (existing is None or recovering):
        record.update(first_due_not_before=(sent_at + timedelta(minutes=authorization['first_delay_minutes'])).isoformat(),
                      maximum_count=authorization['maximum_count'], second_sms_allowed=authorization['second_sms_allowed'],
                      authorization=authorization)
        if recovering:
            record['registration_recovery'] = 'ClosedPriorContextBlocksExplicitNewContext'
    elif existing is not None:
        record.update(maximum_count=limit, second_sms_allowed=limit == 2)
        if existing.get('first_due_not_before') is not None:
            record['first_due_not_before'] = stamp(existing['first_due_not_before']).isoformat()
    return {"status": "MaterialHandoffPlanned", "record": record, "scope": SCOPE}


def saved_record(capture, expected):
    payload = object_result(capture)
    if payload.get("metadata", {}).get("type") != "page":
        raise ValueError("Use the original saved page fetch")
    body = page_body(capture)
    matches = []
    for block in re.findall(r"```json\s*\n(.*?)\n```", body, re.S):
        value = json.loads(block)
        if isinstance(value, dict) and value.get("contract") == "material-handoff-v1" and value.get("event_key") == expected["event_key"]:
            matches.append(value)
    if matches != [expected]:
        raise ValueError("Missing, duplicated or changed saved handoff record")
    return page_id(payload["id"])


def verify(data):
    expected = plan(data["input"])["record"]
    email_id = saved_record(data["saved_email_task"], expected)
    cycle_id = saved_record(data["saved_cycle"], expected) if expected["material"] else None
    if email_id != expected["email_task_id"] or email_id == cycle_id:
        raise ValueError("Handoff must persist on the original email task and its distinct cycle page")
    if expected.get("operation") == "reuse":
        cycles = [c for c in data["input"]["cycles"] if c["cycle_key"] == expected["cycle_key"]]
        if len(cycles) != 1 or page_id(cycles[0].get("page_id", "")) != cycle_id:
            raise ValueError("Reuse must keep the original cycle page, not a duplicate")
    entity_id = email_id
    if data.get('saved_recovery_task') is not None:
        from email_presentation import blocks, properties
        capture = data['saved_recovery_task']
        props = properties(capture)
        entity_id = page_id(object_result(capture)['id'])
        record = blocks(capture, 'material-handoff-recovery-v1')[1]
        outcome = record['current_outcome']
        if (entity_id in {email_id, cycle_id} or props.get('OwnerSkill') != 'eightdegrees-sales-reply'
                or props.get('ResumeStep') != 'RecordMaterialHandoff' or props.get('StepId') != 'RecordMaterialHandoff'
                or props.get('ContentVersion') != expected['content_version']
                or page_id(props.get('SourceURL', '')) != email_id
                or page_id(record['original_send_task_id']) != email_id
                or outcome.get('message_id') != expected['message_id'] or outcome.get('sent') is not True
                or outcome.get('content_version') != expected['content_version']):
            raise ValueError('Recovery must bind the original email task, Sent message and version')
    return {"status": "MaterialHandoffVerified", "entity_id": entity_id, "email_task_id": email_id,
            "projection_page_ids": [v for v in (email_id, cycle_id) if v is not None], "cycle_page_id": cycle_id,
            "event_key": expected["event_key"], "state": expected["state"],
            "message_id": expected["message_id"], "content_version": expected["content_version"], "scope": SCOPE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "verify"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text()
        result = {"plan": plan, "verify": verify}[args.command](json.loads(raw))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        result = {"status": "NeedsCorrection", "issues": [str(exc)], "scope": SCOPE}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"MaterialHandoffPlanned", "MaterialHandoffVerified"} else 2


if __name__ == "__main__":
    sys.exit(main())
