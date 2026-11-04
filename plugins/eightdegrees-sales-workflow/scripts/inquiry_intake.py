"""Resolve supplied name evidence and plan additive inquiry labels; no connector I/O."""
from email.utils import parseaddr


def name(data):
    status = data.get('crm_match', 'none')
    if status not in {'matched', 'none', 'ambiguous'}:
        raise ValueError('Use the actual CRM match outcome')
    for field, source in (('crm_name', 'CRM'), ('signature_name', 'Signature'),
                          ('sender_name', 'Sender')):
        value = data.get(field)
        if field == 'crm_name' and status != 'matched':
            continue
        if field == 'sender_name' and not value:
            value = parseaddr(data.get('from_header', ''))[0]
        if value is not None and not isinstance(value, str):
            raise ValueError('Name evidence must be text or null')
        value = (value or '').strip()
        if value:
            if any(c in value for c in '\r\n<>') or '@' in value:
                raise ValueError('Use one actual name, not an address or markup')
            return {'status': 'InquiryNameResolved', 'customer_name': value,
                    'name_source': source, 'greeting': 'Dear '+value+',',
                    'ask_customer_name': False, 'crm_match': status,
                    'identity_approval': False, 'crm_write_allowed': False}
    return {'status': 'InquiryNameResolved', 'customer_name': None,
            'name_source': 'Anonymous', 'greeting': 'Dear Customer,',
            'ask_customer_name': True, 'crm_match': status,
            'identity_approval': False, 'crm_write_allowed': False}


def label(data):
    if data.get('in_authorized_scope') is not True:
        raise ValueError('Labels cannot authorize or expand mailbox reads')
    if not data.get('account') or not data.get('message_id'):
        raise ValueError('Use the original authorized mailbox and immutable message ID')
    classification = data.get('classification')
    if classification not in {'Inquiry', 'Other', 'Uncertain'}:
        raise ValueError('Classify the actual current incoming message first')
    target = data.get('label_name', 'AimoreInquiry')
    if not isinstance(target, str) or not target.strip() or target == 'AimoreScanned':
        raise ValueError('Inquiry and saved-progress labels must be distinct')
    catalog, observed = data['labels'], data['message_label_ids']
    matches = [x for x in catalog if x.get('name') == target]
    if len(matches) > 1 or any(not x.get('id') for x in matches):
        raise ValueError('Resolve conflicting actual mailbox label metadata')
    base = {'status': 'InquiryLabelPlanned', 'account': data['account'],
            'message_id': data['message_id'], 'classification': classification,
            'remove_label_ids': [], 'send_authority': False}
    if classification != 'Inquiry':
        return dict(base, action='None', add_label_ids=[], label_name=target)
    if not matches:
        return dict(base, action='CreateOrReuseLabelThenReplan', label_name=target,
                    add_label_ids=[])
    identity = matches[0]['id']
    return dict(base, action='None' if identity in observed else 'AddLabel',
                label_name=target, add_label_ids=[] if identity in observed else [identity])
