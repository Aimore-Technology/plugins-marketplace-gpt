"""Review -> send -> notification regressions; all provider captures are offline."""

import copy
import json
import unittest

import test_owner_completion as owner
from test_execution_preflight import PREFLIGHT, capture
from test_workflow_checks import task
from test_reply_transport import ADAPTER, fixture
from test_scheduled_outcomes import OUTCOME, RECEIPT, saved_outcome, receipt_input, note_readback, outcome
from test_material_handoff import inputs as handoff_input, saved as saved_handoff
from test_email_presentation import fixture as presentation_input, apply_plan
from test_sms_authority import inputs as sms_input, saved as saved_sms
import email_presentation
import material_handoff
import sms_authority
import workflow_checks
from phase_contracts import ROUTES, MINIMUM_EVIDENCE
from fixtures_intake import handoff

RUN, TASK, ACTION, HUB = owner.RUN, owner.TASK, owner.ACTION, owner.HUB
FUTURE, FUTURE_ACTION = '1' * 32, '2' * 32


def append_check(data, kind, identity, result):
    name = kind + ':' + identity
    data['registry']['required_checks'][name] = {'kind': kind, 'entity_id': identity}
    data['completion']['required_checks'][name] = {'kind': kind, 'entity_id': identity}
    data['completion']['checks'].append({'name': name, 'invocation_id': 'run-1',
        'publication_version': 'publication-v1', 'exit_code': 0, 'result': result})


def request(data):
    registry = data['registry']
    routes = {r['result']['entity_id']: r['result']['resume_step']
              for r in data['completion']['checks'] if registry['required_checks'][r['name']]['kind'] == 'route'}
    resources = [{'role': 'run', 'type': 'run', 'entity_id': RUN}]
    for index, identity in enumerate(registry['task_page_ids']):
        resources.append({'role': 'task-' + str(index), 'type': 'task', 'entity_id': identity,
            'content_version': registry['task_versions'][identity], 'resume_step': routes[identity]})
        for action, binding in registry['action_bindings'].items():
            if binding == identity:
                resources.append({'role': 'action-' + str(index), 'type': 'action', 'entity_id': action,
                    'task_role': 'task-' + str(index)})
    resources.extend({'role': 'projection-' + str(i), 'type': 'publication', 'entity_id': identity}
                     for i, identity in enumerate(registry['publication_page_ids']))
    return {'verification_mode': 'legacy-readback', 'owner_skill': registry['owner_skill'], 'policy': registry['policy'], 'operation': 'review',
            'invocation_id': 'run-1', 'publication_version': 'publication-v1', 'resources': resources,
            'intake_handoff': handoff()}


def phased(data):
    """Prepare/persist/read back the real generated phase contract around captures."""
    prepared = PREFLIGHT.prepare(request(data))
    ready = PREFLIGHT.ready({'prepared': prepared, 'saved_plan': capture(prepared, RUN)})
    existing = {(data['registry']['required_checks'][r['name']]['kind'],
                 data['registry']['required_checks'][r['name']]['entity_id']): r['result']
                for r in data['completion']['checks']}
    data = copy.deepcopy(data)
    data['registry'] = ready['registry']
    required = ready['registry']['required_checks']
    checks = []
    for name, spec in required.items():
        result = ready if spec['kind'] == 'execution-plan' else existing.get((spec['kind'], spec['entity_id']))
        if result is None and spec['kind'] == 'page-links':
            result = owner.CHECKS.page_links({'page': owner.page(spec['entity_id'], 'Saved fixture page.')})
        if spec['kind'] == 'task-summary':
            item = task(ready['registry']['stage_step'], 'Manual')
            item.update(PageId=TASK, State='InProgress', Decision='Approve' if item['ResumeStep'].startswith('Send') else 'Confirm', DecisionVersion='test-v1')
            body = '<properties>' + json.dumps(item) + '</properties>\n<content>\n## Current status\n\nVersion: test-v1. Decision recorded.\n\n## Processing result\n\nCurrent step verified.\n</content>'
            actual = {'id': TASK, 'metadata': {'type': 'page'}, 'text': body}
            result = owner.CHECKS.task_summary({'page': actual, 'task': item})
        if result is not None:
            checks.append({'name': name, 'invocation_id': 'run-1', 'publication_version': 'publication-v1',
                           'exit_code': 0, 'result': result})
    data['completion'] = {'invocation_id': 'run-1', 'publication_version': 'publication-v1',
                          'required_checks': copy.deepcopy(required), 'checks': checks}
    return data


def reviewed():
    data = owner.completion_for('eightdegrees-sales-reply', 'ReviewReplyDraft')
    draft = fixture(); draft['manifest'].update(task_page_id=TASK, content_version='test-v1')
    append_check(data, 'reply-draft', TASK, ADAPTER.verify(draft))
    return data


def sent():
    data = owner.completion_for('eightdegrees-sales-reply', 'SendApprovedReply')
    draft = fixture(); draft['manifest'].update(task_page_id=TASK, content_version='test-v1')
    append_check(data, 'reply-draft', TASK, ADAPTER.verify(draft))
    message = copy.deepcopy(draft); message.update(phase='sent', sent_message_id='sent-1')
    message['message'].update(id='sent-1', label_ids=['SENT'])
    import provider_handoff
    ack = provider_handoff.verify({'operation': 'email', 'manifest': draft['manifest'],
        'draft_verification': ADAPTER.verify(draft), 'request': {'draft_id': draft['manifest']['draft_id']},
        'response': {'id': 'sent-1', 'thread_id': draft['manifest']['thread_id'], 'label_ids': ['SENT']}})
    append_check(data, 'provider-handoff', TASK, ack)
    append_check(data, 'outcome', TASK, OUTCOME.verify_projection(saved_outcome()))
    receipt = receipt_input()
    for key, value in {'sender': draft['manifest']['from_address'], 'recipient': draft['manifest']['to'],
                       'subject': draft['manifest']['subject'], 'payload_sha256': draft['manifest']['html_sha256']}.items():
        receipt['approved'][key] = receipt['sent'][key] = value
    receipt['note_readback'] = note_readback(receipt)
    append_check(data, 'crm-receipt', TASK, RECEIPT.verify(receipt))
    handoff = handoff_input(); handoff['email_task_id'] = TASK; handoff['event']['message_id'] = 'sent-1'
    append_check(data, 'material-handoff', TASK, material_handoff.verify({'input': handoff,
        'saved_email_task': saved_handoff(handoff, 'email') | {'id': TASK}, 'saved_cycle': saved_handoff(handoff)}))
    presentation = presentation_input(); presentation['saved_pages'] = apply_plan(presentation)
    result = email_presentation.verify(presentation)
    for identity in result['projection_page_ids']:
        if identity not in (RUN, TASK, ACTION, HUB):
            data['registry']['publication_page_ids'].append(identity)
            append_check(data, 'page-links', identity, owner.CHECKS.page_links({'page': owner.page(identity, 'Saved result.')}))
    append_check(data, 'email-presentation', TASK, result)
    return data


class PhaseOrderingTests(unittest.TestCase):
    def test_original_mixed_review_and_future_send_is_refused_before_any_work(self):
        data = request(reviewed())
        data['resources'].append({'role': 'future-send', 'type': 'task', 'entity_id': FUTURE,
                                  'content_version': 'test-v1', 'resume_step': 'SendApprovedReply'})
        before = copy.deepcopy(data)
        with self.assertRaisesRegex(ValueError, 'Mixed completion phases'):
            PREFLIGHT.prepare(data)
        self.assertEqual(data, before)

    def test_content_review_finishes_with_unsent_draft_no_sent_or_sms_required(self):
        data = phased(reviewed())
        self.assertEqual(owner.CHECKS.owner_write(data)['status'], 'WithinOwnerScope')
        kinds = {s['kind'] for s in data['registry']['required_checks'].values()}
        self.assertFalse(kinds & {'reply-sent', 'outcome', 'crm-receipt', 'material-handoff', 'email-presentation'})
        data['call']['args']['page_id'] = FUTURE
        self.assertEqual(owner.CHECKS.owner_write(data)['status'], 'Deferred')

    def test_content_review_still_needs_exact_stored_draft(self):
        data = reviewed()
        data['completion']['checks'] = [r for r in data['completion']['checks']
                                       if data['registry']['required_checks'][r['name']]['kind'] != 'reply-draft']
        self.assertEqual(owner.CHECKS.owner_write(phased(data))['status'], 'Deferred')

    def test_future_send_proof_cannot_be_added_to_a_review_phase(self):
        for kind in ('reply-sent', 'outcome', 'crm-receipt', 'material-handoff', 'email-presentation', 'sms-authority'):
            data = request(reviewed()); data['resources'][1]['evidence'] = [kind]
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'another phase'):
                PREFLIGHT.prepare(data)

    def test_missing_step_or_other_owner_is_refused_during_preparation(self):
        for step in (None, 'NotARoute', 'SendNotificationSms'):
            data = request(reviewed()); data['resources'][1]['resume_step'] = step
            with self.subTest(step=step), self.assertRaises(ValueError):
                PREFLIGHT.prepare(data)

    def test_all_registered_routes_generate_only_their_phase_requirements(self):
        for step, route in ROUTES.items():
            data = {'verification_mode': 'legacy-readback', 'owner_skill': route['owner'], 'policy': 'owner-workflow', 'operation': 'recovery',
                'invocation_id': 'run-1', 'publication_version': 'v1', 'resources': [
                    {'role': 'run', 'type': 'run', 'entity_id': RUN},
                    {'role': 'task', 'type': 'task', 'entity_id': TASK, 'content_version': 'v1', 'resume_step': step},
                    {'role': 'action', 'type': 'action', 'entity_id': ACTION, 'task_role': 'task'}]}
            with self.subTest(step=step):
                data['intake_handoff'] = handoff()
                prepared = PREFLIGHT.prepare(data)
                required = prepared['execution_plan']['required_checks']
                self.assertEqual({s['kind'] for s in required.values()} - {'page-links', 'route', 'task-display', 'task-summary'},
                                 set(MINIMUM_EVIDENCE.get(step, ())))

    def test_no_send_invocation_cannot_prepare_sending_phase(self):
        for policy in ('draft-only', 'one-cycle-no-customer-send'):
            data = request(sent()); data['policy'] = policy
            with self.subTest(policy=policy), self.assertRaisesRegex(ValueError, 'does not allow'):
                PREFLIGHT.prepare(data)

    def test_send_phase_cannot_finish_on_approval_or_draft_alone(self):
        data = owner.completion_for('eightdegrees-sales-reply', 'SendApprovedReply')
        draft = fixture(); draft['manifest'].update(task_page_id=TASK, content_version='test-v1')
        append_check(data, 'reply-draft', TASK, ADAPTER.verify(draft))
        self.assertEqual(owner.CHECKS.owner_write(phased(data))['status'], 'Deferred')

    def test_successive_review_email_send_and_notification_contracts_complete(self):
        self.assertEqual(owner.CHECKS.owner_write(phased(reviewed()))['status'], 'WithinOwnerScope')
        self.assertEqual(owner.CHECKS.owner_write(phased(sent()))['status'], 'WithinOwnerScope')
        data = owner.completion_for('eightdegrees-sms-follow-up', 'SendNotificationSms')
        source = sms_input(); source['payload'].update(task_id=TASK, content_version='test-v1')
        source['saved_task'] = saved_sms(source) | {'id': TASK}
        authority = sms_authority.verify(source)
        event = outcome('sms', 'SentToNetwork'); event['provider']['payload_sha256'] = authority['body_sha256']
        append_check(data, 'sms-authority', TASK, authority)
        import provider_handoff
        frozen = sms_authority.prepare(source)['record']
        ack = provider_handoff.verify({'operation': 'sms', 'notification': frozen, 'authority': authority,
            'request': {'body': frozen['body'], 'recipient': frozen['recipient'], 'deviceId': frozen['device_id'],
                        'idempotencyKey': 'one-original-attempt'}, 'response': {'Id': 'sent-1', 'Status': 'SentToNetwork'}})
        append_check(data, 'provider-handoff', TASK, ack)
        append_check(data, 'outcome', TASK, OUTCOME.verify_projection(saved_outcome(event)))
        self.assertEqual(owner.CHECKS.owner_write(phased(data))['status'], 'WithinOwnerScope')

    def test_no_send_result_obligation_can_be_deleted_from_frozen_plan(self):
        data = phased(sent())
        for kind in MINIMUM_EVIDENCE['SendApprovedReply']:
            bad = copy.deepcopy(data)
            name = next(k for k, spec in bad['registry']['required_checks'].items() if spec['kind'] == kind)
            del bad['registry']['required_checks'][name]
            del bad['completion']['required_checks'][name]
            bad['completion']['checks'] = [r for r in bad['completion']['checks'] if r['name'] != name]
            with self.subTest(kind=kind):
                self.assertEqual(owner.CHECKS.owner_write(bad)['status'], 'Deferred')

    def test_frozen_step_and_execution_route_must_agree(self):
        data = phased(reviewed())
        for change in ('route', 'registry', 'missing'):
            bad = copy.deepcopy(data)
            if change == 'route':
                next(r for r in bad['completion']['checks'] if r['name'].endswith(':route'))['result']['resume_step'] = 'SendApprovedReply'
            elif change == 'registry':
                bad['registry']['stage_step'] = 'SendApprovedReply'
            else:
                bad['registry']['task_steps'] = {}
            with self.subTest(change=change):
                self.assertEqual(owner.CHECKS.owner_write(bad)['status'], 'Deferred')

    def test_old_mixed_plan_is_retained_and_not_silently_reinterpreted(self):
        data = reviewed(); before = copy.deepcopy(data)
        item = task('SendApprovedReply', 'Manual'); item['PageId'] = FUTURE
        data['registry']['task_page_ids'].append(FUTURE); data['registry']['task_versions'][FUTURE] = 'test-v1'
        append_check(data, 'page-links', FUTURE, owner.CHECKS.page_links({'page': owner.page(FUTURE, 'Send pending.')}))
        append_check(data, 'route', FUTURE, workflow_checks.check_resume(item, 'owner-workflow', True))
        original = copy.deepcopy(data)
        self.assertIn('Mixed completion phases', owner.CHECKS.owner_write(data)['reason'])
        self.assertEqual(data, original)
        self.assertEqual(owner.CHECKS.owner_write(phased(before))['status'], 'WithinOwnerScope')

    def test_single_phase_legacy_plan_readback_remains_supported(self):
        data = request(reviewed()); prepared = PREFLIGHT.prepare(data)
        plan = prepared['execution_plan']; plan['contract_version'] = 'execution-v1'; plan.pop('stage_step')
        for resource in plan['resources']:
            resource.pop('resume_step', None)
        plan['required_checks'] = PREFLIGHT.compile_checks(plan['resources'], phased=False)
        prepared['plan_sha256'] = PREFLIGHT.digest(plan)
        result = PREFLIGHT.ready({'prepared': prepared, 'saved_plan': capture(prepared, RUN)})
        self.assertEqual(result['status'], 'ExecutionPlanReady')
        self.assertNotIn('stage_step', result['registry'])

    def test_approved_canonical_and_action_status_cannot_still_request_review(self):
        for step, decision, old in [('ReviewReplyDraft', 'Confirm', 'Waiting for content review.'),
                                    ('SendApprovedReply', 'Approve', 'Waiting for independent send decision.'),
                                    ('ReviewReplyDraft', 'Confirm', '\u7b49\u5f85\u5ba1\u6838'),
                                    ('SendApprovedReply', 'Approve', '\u7b49\u5f85\u72ec\u7acb\u53d1\u9001\u51b3\u5b9a')]:
            item = task(step, 'Manual'); item.update(PageId=TASK, Decision=decision, DecisionVersion='test-v1')
            body = '## Current status\n\nVersion: test-v1. ' + old + '\n\n## Processing result\n\nDecision recorded.'
            actual = owner.page(TASK, body)
            actual['text'] = '<properties>' + json.dumps(item) + '</properties>\n' + actual['text']
            self.assertEqual(owner.CHECKS.task_summary({'page': actual, 'task': item})['status'], 'NeedsCorrection')
            actual['text'] = actual['text'].replace(old, 'Approval accepted; workflow prerequisites are blocked.')
            self.assertEqual(owner.CHECKS.task_summary({'page': actual, 'task': item})['status'], 'DisplayConsistentForCheckedPatterns')
            actual['id'] = ACTION; item['ActionPageURL'] = ACTION
            self.assertEqual(owner.CHECKS.task_display({'page': actual, 'task': item})['status'], 'DisplayConsistentForCheckedPatterns')
            actual['text'] = actual['text'].replace('Approval accepted; workflow prerequisites are blocked.', old)
            self.assertEqual(owner.CHECKS.task_display({'page': actual, 'task': item})['status'], 'NeedsCorrection')

    def test_task_summary_rejects_wrong_original_or_stale_saved_decision(self):
        item = task('ReviewReplyDraft', 'Manual'); item.update(PageId=TASK, Decision='Confirm', DecisionVersion='test-v1')
        body = '## Current status\n\nVersion: test-v1. Decision recorded.\n\n## Processing result\n\nAccepted.'
        actual = owner.page(TASK, body); actual['text'] = '<properties>' + json.dumps(item) + '</properties>\n' + actual['text']
        for change in ('target', 'saved'):
            bad = copy.deepcopy(actual)
            if change == 'target': bad['id'] = ACTION
            else: bad['text'] = bad['text'].replace('"Decision": "Confirm"', '"Decision": ""')
            with self.subTest(change=change), self.assertRaises(ValueError):
                owner.CHECKS.task_summary({'page': bad, 'task': item})

    def test_opaque_legacy_multi_task_plan_is_stopped_before_dependent_work(self):
        data = request(reviewed()); prepared = PREFLIGHT.prepare(data)
        plan = prepared['execution_plan']; plan['contract_version'] = 'execution-v1'; plan.pop('stage_step')
        for resource in plan['resources']: resource.pop('resume_step', None)
        plan['resources'].append({'role': 'future', 'type': 'task', 'entity_id': FUTURE, 'content_version': 'test-v1'})
        plan['required_checks'] = PREFLIGHT.compile_checks(plan['resources'], phased=False)
        prepared['plan_sha256'] = PREFLIGHT.digest(plan)
        with self.assertRaisesRegex(ValueError, 'Legacy multi-task plan'):
            PREFLIGHT.ready({'prepared': prepared, 'saved_plan': capture(prepared, RUN)})


if __name__ == '__main__':
    unittest.main()
