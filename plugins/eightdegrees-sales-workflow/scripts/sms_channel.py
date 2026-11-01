"""Bound an explicitly authorized channel check; no I/O, approval or dispatch."""
from datetime import datetime


def gate(data):
    if data['invocation_policy'] not in {'one-cycle-approved-work', 'scheduled-approved-work', 'owner-workflow'}:
        raise ValueError('This invocation cannot dispatch a customer notification')
    guards = data['guards']
    if any(guards.get(k) is not False for k in ('stop', 'manual_pause', 'unknown_attempt', 'customer_replied')):
        return {'status': 'ChannelCheckBlocked', 'reason': 'Stop/reply/pause or unknown state prevents dispatch'}
    if data.get('channel_verified') is True and data.get('inbound_reader_available') is True:
        return {'status': 'ChannelCheckEligible', 'mode': 'ordinary', 'send_authorized': False}
    test, payload = data.get('controlled_sms_test') or {}, data['payload']
    if (test.get('enabled') is not True or type(test.get('max_messages')) is not int or test['max_messages'] != 1
            or not isinstance(test.get('authorization_ref'), str) or not test['authorization_ref'].strip()
            or test.get('context_key') != data['context_key']
            or any(test.get(k) != payload.get(k) or not payload.get(k) for k in ('recipient', 'device_id', 'sender_number'))):
        return {'status': 'ChannelCheckBlocked', 'reason': 'Missing exact one-message diagnostic scope; use its setup input page'}
    now, expiry = (datetime.fromisoformat(v.replace('Z', '+00:00')) for v in (data['now'], test['expires_at']))
    if now.tzinfo is None or expiry.tzinfo is None:
        raise ValueError('Channel check times require timezone-aware observations')
    used = test.get('used_slots')
    if type(used) is not int or used not in {0, 1}:
        raise ValueError('Use the actual diagnostic slot count, including unknown attempts')
    current_reservation = (used == 1 and isinstance(data.get('attempt_id'), str) and bool(data['attempt_id'])
                           and test.get('reserved_attempt_id') == data['attempt_id']
                           and test.get('provider_result_present') is False)
    if now >= expiry or used == 1 and not current_reservation or test.get('unknown_attempt') is not False:
        return {'status': 'ChannelCheckBlocked', 'reason': 'Expired, used or unknown diagnostic slot; never resend'}
    return {'status': 'ChannelCheckEligible', 'mode': 'controlled-one-message', 'send_authorized': False,
            'ordinary_readiness_verified': False,
            'scope': 'Only a capability exception; authority, material/due/window/count/device/attempt checks remain mandatory'}
