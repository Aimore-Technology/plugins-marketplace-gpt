"""Mail is ready after approval at any hour; SMS timing is independent."""
import copy

POLICY = 'email-immediate-after-approval-v1'
STEPS = {'SendApprovedReply', 'SendGeneralReply'}


def is_email(item):
    return (item.get('step', item.get('ResumeStep')) in STEPS
            and (item.get('scope') or {}).get('channel', 'email') == 'email')


def release(item):
    """Remove obsolete mail calendar delays without releasing other blockers."""
    value = copy.deepcopy(item)
    if (not is_email(value) or value.get('unknown_attempt')
            or value.get('retry_not_before') or value.get('provider_retry_after')
            or value.get('delay_reason') in {'provider-rate-limit', 'provider-retry'}):
        return value
    if value.get('due_at'):
        value.setdefault('legacy_email_due_at', value.pop('due_at'))
        if value.get('kind') == 'timer':
            value['kind'] = 'recovery'
    return value
