"""Show saved business setup without inventing consent or adding runtime gates."""
from notion_checks import object_result


def audit(data):
    settings = data['settings']
    setup = settings.get('customer_setup') or {}
    fields, issues = [], []
    def field(name, value, step, required=True):
        present = value is not None and value != '' and value != []
        fields.append({'field': name, 'value': value, 'state': 'Saved' if present else 'Missing',
                       'required': required, 'reference': step,
                       'confirmed_this_deployment': False,
                       'provenance': 'Existing RunSettings; preserved, not new consent' if present else 'Not configured'})
        if required and not present:
            issues.append({'field': name, 'reason': 'No saved value', 'recovery': 'Collect the actual operator choice in init',
                           'scope': name})
    field('operator_name', setup.get('operator_name'), 'init.1')
    field('notion_root', setup.get('notion_root_id'), 'init.1/3')
    field('workspace_language', setup.get('workspace_language'), 'init.1')
    field('gmail_account', setup.get('gmail_account'), 'init.5')
    labels = setup.get('allowed_label_ids')
    field('gmail_read_labels', labels, 'init.5 / email-scanning discovery')
    field('gmail_time_scope', setup.get('mail_scope') or setup.get('mail_time_range'), 'init.5')
    folders = setup.get('dropbox_work_folders')
    field('dropbox_authorized_folders', folders, 'init.2 / sales-reply sources')
    field('sender_account', setup.get('sender_account'), 'init.5 / email dispatch')
    field('signature', setup.get('signature'), 'init.5 / reply preparation')
    field('crm_location_id', setup.get('crm_location_id'), 'init.1 / customer matching')
    field('internal_reminders', setup.get('internal_reminder_scope'), 'init.5', False)
    shadow = (settings.get('dropbox') or {}).get('work_folders')
    if isinstance(folders, list) and isinstance(shadow, list) and set(folders) != set(shadow):
        issues.append({'field': 'dropbox_authorized_folders', 'reason': 'Legacy Dropbox folder projection differs from customer_setup',
                       'canonical_value': folders, 'legacy_value': shadow,
                       'recovery': 'Show both; preserve current authorized scope, never union/expand automatically',
                       'scope': 'Dropbox setup projection'})
    label_names = {}
    if data.get('gmail_labels_capture') is not None:
        original = object_result(data['gmail_labels_capture'])
        catalog = original['labels']
        label_names = {v['id']: v['name'] for v in catalog}
        for label in labels or []:
            if label not in label_names:
                issues.append({'field': 'gmail_read_labels', 'reason': 'Saved label absent from actual connected mailbox catalog: '+label,
                               'recovery': 'Select the actual label for this account; retain original pending sources',
                               'scope': 'New Gmail discovery only'})
    notes = ['This is configuration inspection, not operator confirmation, connection certification or sending authority.']
    if labels == ['UNREAD']:
        notes.append('UNREAD selects all authorized unread mail in the saved time scope; it is not a dedicated inquiry label. Show this explicitly and offer actual label selection in init.')
    if labels and settings.get('scanned_label_id') in labels:
        issues.append({'field': 'gmail_read_labels', 'reason': 'Progress checkpoint label is being used as read authorization',
                       'recovery': 'Ask for the actual inquiry/read scope; do not relabel mail into scope', 'scope': 'Gmail discovery'})
    return {'status': 'ConfigurationAuditPrepared', 'fields': fields, 'issues': issues,
            'gmail_label_names': label_names,
            'missing_required': [f['field'] for f in fields if f['required'] and f['state'] == 'Missing'],
            'notes': notes, 'runtime_gate': False,
            'scope': 'Display/reconciliation only; do not disable running work, replace stop state or manufacture authorization'}
