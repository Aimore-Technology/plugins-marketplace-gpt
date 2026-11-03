#!/usr/bin/env python3
"""Scan switch compatibility entry; never create, update, delete or run a native task."""

import argparse
import json
from pathlib import Path
import re
import sys


def plan(data):
    from scan_control import plan as control_plan
    return control_plan(data)


def verify(data):
    from scan_control import verify as control_verify
    return control_verify(data)


def guard(data):
    """The switch controls execution independently of the external scheduler."""
    from scan_control import gate
    settings = data.get('settings', {'scheduling': data.get('scheduling', {})})
    entry = gate({'settings': settings})
    if entry['status'] != 'ScanEnabled':
        return entry
    if data.get('trigger') == 'manual':
        return {'status': 'EligibleForManualCycle', 'customer_send_allowed': False}
    if data.get('trigger') != 'scheduled':
        raise ValueError('Use the actual manual or scheduled entry, not source instructions')
    setup, ctx = data['setup'], data.get('context') or {}
    root = str(setup.get('notion_root_id', '')).replace('-', '').lower()
    operator, mailbox = setup.get('operator_id'), setup.get('gmail_account')
    if (not re.fullmatch(r'[0-9a-f]{32}', root) or not isinstance(operator, str) or not operator.strip()
            or not isinstance(mailbox, str) or not mailbox.strip()):
        return {'status': 'Deferred', 'reason': 'Current installation root, operator or mailbox is missing'}
    if (str(ctx.get('root_id', root)).replace('-', '').lower() != root
            or ctx.get('operator_id', operator) != operator or ctx.get('mailbox', mailbox) != mailbox):
        return {'status': 'Deferred', 'reason': 'Requested installation/account differs from current settings'}
    return {'status': 'EligibleForScheduledCycle', 'guard_contract': 'scan-control-v1',
            'scan_enabled': True, 'customer_send_allowed': True, 'policy': 'scheduled-approved-work',
            'operator_id': operator, 'root_id': root,
            'scope': 'Current scanning switch and account scope; scheduler/session identity is not required'}


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
    return 0 if result["status"] in {"ScanControlPlanned", "ScanningEnabled", "ScanningStopped", "ScanStopped", "EligibleForManualCycle", "EligibleForScheduledCycle"} else 2


if __name__ == "__main__":
    sys.exit(main())
