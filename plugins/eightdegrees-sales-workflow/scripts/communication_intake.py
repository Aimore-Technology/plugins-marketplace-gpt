"""Bound communication reads and render standard Notes locally; no connector I/O."""
import hashlib

import crm_note

SOURCE_KINDS = {'provided-text', 'gmail-message', 'dropbox-file'}


def plan(data):
    kind, phase = data['source_kind'], data.get('phase', 'draft')
    if kind not in SOURCE_KINDS or phase not in {'draft', 'approved-write'}:
        raise ValueError('Use a concrete source kind and current communication phase')
    if type(data.get('verify_project_facts', False)) is not bool:
        raise ValueError('Project fact verification must be an explicit boolean')
    reads = ['current RunSettings and registered IDs',
             'current scoped CRM match/contact',
             'registered CRMNotes template and approved persona needed for the proposal',
             'only affected original source/task/action and customer archive']
    if kind == 'gmail-message':
        reads.append('the supplied authorized Gmail message only')
    elif kind == 'dropbox-file':
        reads.append('the supplied authorized Dropbox transcript/file only')
    if data.get('verify_project_facts'):
        reads.append('explicitly requested project facts from registered authorized sources only')
    if phase == 'approved-write':
        reads.extend(['fresh original submitted action and exact approved payload',
                      'current CRM target and saved attempts; scoped existence only for unknown attempts',
                      'original CRM/Notion write success responses and returned record IDs'])
    return {'status': 'CommunicationReadPlanPrepared', 'source_kind': kind, 'phase': phase,
            'reads': reads,
            'skip': ['init/readiness re-audit', 'mailbox scanning', 'all-client/tree searches',
                     'unrelated CRM history', 'all Dropbox project folders',
                     'HTML/image preview and sending procedures', 'Calendar/SMS queries',
                     'global dashboard/Health rebuild'],
            'required_checks': ['execution.prepare and API-ack execution.ready',
                                'facts.canonical for actual proposals', 'communication.note',
                                'exact notion.mutation before each actual write',
                                'current pre-call route and receipt completion'],
            'detail_reference': 'references/communication-fast-path.md',
            'crm_write_allowed': False, 'send_allowed': False,
            'scope': 'Read planning only; no approval, lock, stored readback or provider authority'}


def note(data):
    body = crm_note.render(data['payload']).decode('utf-8')
    return {'status': 'CommunicationNotePrepared', 'note': body,
            'sha256': hashlib.sha256(body.encode('utf-8')).hexdigest(),
            'template_version': crm_note.TEMPLATE_VERSION,
            'crm_write_allowed': False,
            'scope': 'Deterministic plain-text layout only; facts, identity and exact approval remain required'}
