#!/usr/bin/env python3
"""Render/reconcile a deterministic approved email-result CRM receipt offline."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

import crm_note
import api_result


VERSION = "send-receipt-v2"
LEGACY_VERSION = "send-receipt-v1"


def render(data):
    approval, sent, customer = data["approved"], data["sent"], data["customer"]
    template = approval.get("receipt_template")
    allowed = {"Sent", "ProviderAccepted"} if template == VERSION else {"Sent"}
    if template not in {VERSION, LEGACY_VERSION} or sent.get("read_verified") is not True or sent.get("status") not in allowed:
        raise ValueError("The send approval must include this receipt template and the original successful Gmail dispatch response")
    if not re.fullmatch(r"[a-f0-9]{64}", approval.get("payload_sha256", "")) or not approval.get("content_version"):
        raise ValueError("Bind the original approved content version and SHA-256")
    for key in ("location_id", "contact_id"):
        if not isinstance(customer.get(key), str) or not customer[key] or approval.get(key) != customer[key]:
            raise ValueError("Receipt customer differs from the approved CRM " + key)
    for key in ("sender", "recipient", "subject", "payload_sha256"):
        if not isinstance(approval.get(key), str) or not approval[key] or approval[key] != sent.get(key):
            raise ValueError("Actual sent message differs from approved " + key)
    if not isinstance(sent.get("message_id"), str) or not sent["message_id"] or not data.get("task_id"):
        raise ValueError("Actual message and original task IDs are required")
    instant = datetime.fromisoformat(sent["sent_at"].replace("Z", "+00:00"))
    if instant.utcoffset() is None:
        raise ValueError("Actual send time must include its offset")
    moment = instant.astimezone(ZoneInfo(data["timezone"])).isoformat()
    # One receipt per immutable sender/message, independent of retries or later page versions.
    key = "email-send:" + hashlib.sha256((sent["sender"] + "\n" + sent["message_id"]).encode()).hexdigest()
    payload = {"template_version": crm_note.TEMPLATE_VERSION, "communication_id": key,
               "content_version": template, "communication_time": moment, "timezone": data["timezone"],
               "source_url": data["source_url"], "location_id": customer["location_id"],
               "contact_id": customer["contact_id"], "customer_name": customer["name"],
               "sections": {
                   "context_background": ["Approved customer email; exact content and approval are retained at the source."],
                   "action": ["One approved email sent." if template == LEGACY_VERSION else "One approved email handed to Gmail for sending.", "Sender: " + sent["sender"],
                              "Recipient: " + sent["recipient"], "Provider message ID: " + sent["message_id"],
                              "Provider status: Sent; recipient delivery is not inferred." if template == LEGACY_VERSION else
                              "Provider status: " + sent["status"] + "; dispatch handed off; no external verification requested."],
                   "recommendation": ["No new recommendation or customer-persona change in this send-result receipt."],
                   "next_schedule": ["Follow the separately approved follow-up plan; no new appointment is created by this receipt."]}}
    body = crm_note.render(payload).decode("utf-8")
    return {"status": "ReceiptPrepared", "entity_id": data["task_id"], "receipt_key": key,
            "note": body, "sha256": hashlib.sha256(body.encode()).hexdigest(), "payload": payload,
            "scope": "Deterministic internal send-result receipt only; never a new send or inferred delivery"}


def verify(data):
    expected = render(data)
    if 'write_result' in data:
        receipt = api_result.confirm({**data['write_result'], 'service': 'crm',
                                      'entity_id': data['task_id'], 'purpose': 'crm-note',
                                      'content_version': data['approved']['content_version']})
        if receipt['status'] != 'APIWriteConfirmed':
            return receipt
        return {'status': 'CRMReceiptVerified', 'entity_id': data['task_id'],
                'content_version': data['approved']['content_version'], 'receipt_key': expected['receipt_key'],
                'crm_note_id': receipt['record_id'], 'message_id': data['sent']['message_id'],
                'payload_sha256': data['approved']['payload_sha256'], 'sha256': expected['sha256'],
                'verification_basis': receipt['verification_basis'], 'stored_content_verified': False}
    observed = data["note_readback"]
    customer = data["customer"]
    if (observed.get("read_verified") is not True or not observed.get("id")
            or observed.get("contact_id") != customer["contact_id"]
            or observed.get("location_id") != customer["location_id"]
            or observed.get("body") != expected["note"]):
        return {"status": "NeedsReconciliation", "reason": "CRM receipt target or exact saved bytes differ", "entity_id": data["task_id"]}
    return {"status": "CRMReceiptVerified", "entity_id": data["task_id"], "content_version": data["approved"]["content_version"], "receipt_key": expected["receipt_key"],
            "crm_note_id": observed["id"], "message_id": data["sent"]["message_id"],
            "payload_sha256": data["approved"]["payload_sha256"], "sha256": expected["sha256"]}


def reconcile(data):
    expected = render(data)
    if data.get("pending_attempt_status") not in (None, "Resolved", "RejectedBeforeDispatch", "NoEffectVerified"):
        return {"status": "NeedsReconciliation", "reason": "Resolve original CRM append attempt; never append another receipt"}
    if data.get("list_complete") is not True or not isinstance(data.get("existing_notes"), list):
        return {"status": "NeedsReconciliation", "reason": "Receipt absence requires complete scoped CRM note evidence"}
    marker = "CommunicationId: " + expected["receipt_key"]
    matches = [n for n in data["existing_notes"] if marker in n.get("body", "").splitlines()]
    if len(matches) > 1:
        return {"status": "NeedsReconciliation", "reason": "Duplicate receipt markers; do not append"}
    if matches:
        resolved = {**data, "note_readback": matches[0]}
        if 'write_result' in data:
            resolved['write_result'] = {**data['write_result'], 'expected_id': matches[0]['id'],
                                        'existence_response': matches[0]}
        result = verify(resolved)
        return {**result, "append_allowed": False}
    return {"status": "EligibleForReceiptAppend", "entity_id": data["task_id"],
            "receipt_key": expected["receipt_key"], "sha256": expected["sha256"], "append_allowed": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("render", "verify", "reconcile"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = {"render": render, "verify": verify, "reconcile": reconcile}[args.command](json.loads(source))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        result = {"status": "NeedsCorrection", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"ReceiptPrepared", "CRMReceiptVerified", "EligibleForReceiptAppend"} else 2


if __name__ == "__main__":
    sys.exit(main())
