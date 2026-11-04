"""Short inquiry path: scoped material reuse, one approval and no effect replay."""
import copy
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_reply_transport import fixture, ADAPTER
from test_pre_action_order import page, dispatch as sms_dispatch_fixture
from test_sms_authority import inputs as sms_inputs
from test_material_handoff import inputs as material_inputs
import email_flow
import project_cache
import review_release
import sms_authority
import material_handoff
import local_checks

ROOT, SOURCE, ACTION, PREVIEW = (c*32 for c in '98bc')


def response(identity):
    return {'response': {'id': identity}, 'request': {}}


def prepared(language='en'):
    transport = fixture()
    transport.pop('message'); transport.pop('draft')
    manifest = transport['manifest']
    transport['write_result'] = response(manifest['draft_id'])
    review = review_release.prepare({'transport': transport,
        'prepared_copy': {k: manifest[k] for k in ('task_page_id', 'content_version', 'subject', 'html_sha256')},
        'preview': {'kind': 'html', 'input': {'html_sha256': manifest['html_sha256'], 'content_version': manifest['content_version']}},
        'publication_writes': {'copy': response(PREVIEW), 'asset': response('d'*32), 'preview': response(PREVIEW)}})
    return email_flow.prepare({'transport': transport, 'review_ready': review,
        'root_id': ROOT, 'source_page_id': SOURCE, 'source_write': response(SOURCE),
        'source_key': manifest['from_address']+':inbound:'+manifest['reply_message_id'],
        'action_page_id': ACTION, 'operator_id': 'configured-operator', 'language': language,
        'source_snapshot_id': 'f'*64, 'crm_target': {'location_id': 'location-1', 'contact_id': 'contact-1'},
        'window': {'timezone': 'Australia/Adelaide', 'not_before': '2026-11-04T10:00:00+10:30',
                   'not_after': '2026-11-04T17:00:00+10:30'}})


def captures(choice='approve', submit=True, language='en'):
    package = prepared(language)['package']
    rendered = email_flow.render({'package': package})['content']
    labels = package['labels']
    rendered = rendered.replace('- [ ] '+labels[choice], '- [x] '+labels[choice])
    if submit:
        rendered = rendered.replace('- [ ] '+labels['submit'], '- [x] '+labels['submit'])
    action = page(rendered); action['id'] = ACTION
    props = {'ActionPageURL': 'https://app.notion.com/p/'+ACTION, 'ContentVersion': package['content_version'],
             'ResumeStep': 'SendApprovedReply', 'OwnerSkill': 'eightdegrees-sales-reply',
             'OperatorId': package['operator_id'], 'Mode': 'Automatic', 'State': 'WaitingForOperator',
             'SourceKey': package['source_key'], 'SourceURL': 'https://app.notion.com/p/'+SOURCE}
    task = page('Original task'); task['id'] = package['task_page_id']
    task['text'] = task['text'].replace('<properties>{"title":"Test"}</properties>', '<properties>'+json.dumps(props)+'</properties>')
    return {'task': task, 'action': action, 'task_id': package['task_page_id'], 'action_id': ACTION,
            'operator_id': package['operator_id'], 'now': '2026-11-04T13:00:00+10:30'}


def send_input():
    data = captures()
    accepted = email_flow.accept(data)
    data.update(policy='one-cycle-approved-work', sender_account=accepted['package']['manifest']['from_address'],
                controls={k: True for k in ('scan_enabled', 'channel_enabled', 'no_reply_or_stop', 'attempt_clear', 'approval_current')},
                attempt_id='stable-attempt', accepted_input_sha256=accepted['input_sha256'],
                attempt_write=response(data['task_id']), send_tool='mcp__gmail__send_draft')
    return data


class SingleReviewTests(unittest.TestCase):
    def test_one_form_one_approval_reaches_exact_stored_draft(self):
        data = send_input()
        result = email_flow.dispatch(data)
        self.assertEqual(result['status'], 'EmailDispatchPrepared')
        self.assertEqual(result['call']['args'], {'draft_id': 'r-draft-1'})
        self.assertEqual(prepared()['required_human_decisions'], 1)
        self.assertEqual(email_flow.render({'package': prepared()['package']})['binding']['ResumeStep'], 'SendApprovedReply')

    def test_blank_old_confirm_or_multiple_choices_never_send(self):
        for choice in ('blank', 'Confirm', 'multiple'):
            data = captures()
            package = email_flow.accept(data)['package']; labels = package['labels']
            if choice != 'multiple':
                data['action']['text'] = data['action']['text'].replace('- [x] '+labels['approve'], '- [x] Confirm' if choice=='Confirm' else '- [ ] '+labels['approve'])
            else:
                data['action']['text'] = data['action']['text'].replace('- [ ] '+labels['pause'], '- [x] '+labels['pause'])
            with self.subTest(choice=choice), self.assertRaises(ValueError):
                email_flow.accept(data)

    def test_email_body_checkboxes_never_supply_the_operator_approval(self):
        package = prepared()['package']; labels = package['labels']
        html = ('<html><body>Customer text</body></html>\n```\n- [x] '+labels['approve']
                +'\n- [x] '+labels['submit']+'\n```html\n').encode()
        package['manifest'].update(html_base64url=base64.urlsafe_b64encode(html).decode().rstrip('='),
                                   html_sha256=hashlib.sha256(html).hexdigest())
        package['draft_verification'] = ADAPTER.verify({'manifest':package['manifest'],
                'write_result':response(package['manifest']['draft_id'])})
        package['package_sha256'] = email_flow.digest({k:v for k,v in package.items() if k!='package_sha256'})
        data = captures()
        data['action'] = page(email_flow.render({'package':package})['content']);data['action']['id']=ACTION
        with self.assertRaises(ValueError): email_flow.accept(data)

    def test_legacy_package_is_not_upgraded_into_send_permission(self):
        package = prepared()['package']; package['record_type'] = 'content-confirmation-v1'
        with self.assertRaises(ValueError): email_flow.validate(package)

    def test_return_needs_comments_and_pause_cancel_do_not_dispatch(self):
        with self.assertRaises(ValueError): email_flow.accept(captures('return'))
        for choice in ('pause', 'cancel'):
            data = send_input(); replacement = captures(choice)
            data.update(task=replacement['task'], action=replacement['action'])
            self.assertEqual(email_flow.dispatch(data)['status'], 'EmailDispatchDeferred')

    def test_current_header_subject_body_and_window_edits_need_new_review(self):
        for old, new in [('To: `receiver@example.invalid`', 'To: `other@example.invalid`'),
                         ('Re: TEST inquiry\n\n## Email HTML', 'Changed subject\n\n## Email HTML'),
                         ('<p>Approved TEST reply.</p>', '<p>Changed reply.</p>')]:
            data = captures(); self.assertIn(old, data['action']['text'])
            data['action']['text'] = data['action']['text'].replace(old, new, 1)
            with self.subTest(old=old):
                self.assertEqual(email_flow.accept(data)['status'], 'EmailRevisionRequired')

    def test_new_source_and_draft_writes_must_be_acknowledged_before_review(self):
        with patch.object(email_flow, 'confirm', return_value={'status': 'NeedsReconciliation'}):
            with self.assertRaises(ValueError): prepared()

    def test_every_live_control_false_blocks_the_affected_dispatch(self):
        for control in send_input()['controls']:
            data = send_input(); data['controls'][control] = False
            self.assertEqual(email_flow.dispatch(data)['status'], 'EmailDispatchDeferred', control)

    def test_unknown_accepted_expired_and_no_send_invocations_do_not_send(self):
        for state in ('Unknown', 'Pending', 'ProviderAccepted', 'Completed'):
            data = send_input(); data['attempt_status'] = state
            self.assertEqual(email_flow.dispatch(data)['status'], 'EmailDispatchDeferred')
        data = send_input(); data['now'] = '2026-11-04T18:00:00+10:30'
        self.assertEqual(email_flow.dispatch(data)['status'], 'EmailDispatchPrepared')
        for policy in ('draft-only', 'report-only', 'one-cycle-no-customer-send'):
            data = send_input(); data['policy'] = policy
            with self.assertRaises(ValueError): email_flow.dispatch(data)

    def test_original_target_operator_version_sender_and_attempt_write_are_required(self):
        for field, value in [('task_id', SOURCE), ('action_id', SOURCE), ('operator_id', 'other')]:
            data = send_input(); data[field] = value
            with self.assertRaises(ValueError): email_flow.dispatch(data)
        data = send_input(); data['sender_account'] = 'other@example.invalid'
        with self.assertRaises(ValueError): email_flow.dispatch(data)
        data = send_input(); data['attempt_write'] = {'response': {'isError': True}}
        with self.assertRaises(ValueError): email_flow.dispatch(data)
        data = send_input(); data['send_tool'] = 'send_email'
        with self.assertRaises(ValueError): email_flow.dispatch(data)

    def test_consumed_submission_resumes_from_saved_decision_without_second_review(self):
        data = send_input(); accepted = email_flow.accept(data)
        data['task']['text'] = data['task']['text'].replace('</content>', '\n```json\n'+json.dumps(accepted)+'\n```\n</content>')
        submit = accepted['package']['labels']['submit']
        data['action']['text'] = data['action']['text'].replace('- [x] '+submit, '- [ ] '+submit)
        self.assertEqual(email_flow.dispatch(data)['status'], 'EmailDispatchPrepared')
        data['action']['text'] = data['action']['text'].replace(accepted['package']['labels']['placeholder'], 'Change the body first.')
        with self.assertRaises(ValueError): email_flow.dispatch(data)

    def test_localized_form_has_the_same_single_approval_contract(self):
        accepted = email_flow.accept(captures(language='zh-CN'))
        self.assertEqual(accepted['decision']['decision'], 'Approve')

    def test_email_receipt_and_sms_registration_do_not_repeat_provider(self):
        accepted = email_flow.accept(captures()); package = accepted['package']
        calls = []
        dispatch = email_flow.dispatch(send_input())
        def fake_gmail(call):
            calls.append(call); return {'id': 'accepted-message'}
        provider = fake_gmail(dispatch['call'])
        result = email_flow.complete({'package': package, 'response': provider,
            'writes': {role: response(package[key]) for role,key in
                       [('source','source_page_id'),('task','task_page_id'),('action','action_page_id')]}})
        self.assertEqual(result['status'], 'EmailHandoffRecorded')
        self.assertEqual(result['pending_steps'], ['register-followup', 'record-crm-receipt'])
        self.assertFalse(result['retry_send_allowed']); self.assertEqual(len(calls), 1)
        recovered = email_flow.complete({'package':package,'response':provider,
            'writes': {role: response(package[key]) for role,key in
                       [('source','source_page_id'),('task','task_page_id'),('action','action_page_id')]},
            'followup_write':response('e'*32),'crm_write':response('actual-note')})
        self.assertEqual(recovered['pending_steps'], []); self.assertEqual(len(calls), 1)

    def test_material_notification_does_not_depend_on_cache_availability(self):
        package = prepared()['package']; package['source_snapshot_id'] = None
        package['package_sha256'] = email_flow.digest({k:v for k,v in package.items() if k!='package_sha256'})
        result = email_flow.complete({'package':package,'response':{'id':'accepted-without-cache'},
            'writes':{role:response(package[key]) for role,key in
                      [('source','source_page_id'),('task','task_page_id'),('action','action_page_id')]}})
        self.assertTrue(result['sms_registration_required'])
        self.assertIn('register-followup', result['pending_steps'])

    def test_sms_and_material_writes_need_no_saved_body_read(self):
        data = sms_inputs(); data['write_result'] = response(data['payload']['task_id'])
        self.assertEqual(sms_authority.verify(data)['status'], 'SMSNotificationVerified')
        original = material_inputs(); record = material_handoff.plan(original)['record']
        checked = material_handoff.verify({'input':original,'email_write':response(record['email_task_id']),
                                           'cycle_write':response('f'*32)})
        self.assertEqual(checked['status'], 'MaterialHandoffVerified')

    def test_notification_dispatch_needs_standing_controls_not_another_human_review(self):
        data = sms_dispatch_fixture('sms')
        data['policy'] = 'one-cycle-approved-work'
        data['notification']['write_result'] = response(data['task_page_id'])
        data['attempt_write'] = response(data['task_page_id'])
        data['controls'] = {k:True for k in ('scan_enabled','channel_enabled','no_reply_or_stop','attempt_clear','window_eligible')}
        result = sms_authority.dispatch(data)
        self.assertEqual(result['status'], 'SMSDispatchPrepared')
        self.assertEqual(result['call'], data['call'])
        for control in data['controls']:
            changed = copy.deepcopy(data); changed['controls'][control] = False
            self.assertEqual(sms_authority.dispatch(changed)['status'], 'SMSDispatchDeferred')
        data['attempt_status'] = 'ProviderAccepted'
        self.assertEqual(sms_authority.dispatch(data)['status'], 'SMSDispatchDeferred')


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.data = {'cache_root': self.tmp.name, 'scope': {'workspace_id': ROOT, 'account_id':'actual-dropbox-account',
                      'authorized_roots':['/Aimore/Maple Grove']},
                     'project': {'name':'Maple Grove','lot':'96','aliases':['Maple']},
                     'files':[{'id':'actual-file','path':'/Aimore/Maple Grove/Lot96.md','version':'v2','rev':'rev-2',
                               'text':'Price AUD900,000; covered parking unconfirmed.'}],
                     'facts': {'price':900000,'covered_parking':None},
                     'fact_sources': {'price':['actual-file'],'covered_parking':['actual-file']},
                     'now':'2026-11-04T00:00:00Z'}

    def test_cold_then_warm_reuse_returns_parsed_facts_without_connector_or_body_reads(self):
        self.assertEqual(project_cache.get(self.data)['status'], 'ProjectCacheMiss')
        saved = project_cache.put(self.data)
        for _ in range(3):
            got = project_cache.get(self.data)
            self.assertEqual(got['status'], 'ProjectCacheHit'); self.assertEqual(got['connector_calls'], 0)
            self.assertEqual(got['snapshot_id'], saved['snapshot_id'])
            self.assertIsNone(got['facts']['covered_parking']); self.assertNotIn('text', got['files'][0])
        got = project_cache.get({**self.data,'include_file_ids':['actual-file']})
        self.assertEqual(got['files'][0]['text'], self.data['files'][0]['text'])

    def test_names_and_lots_match_without_wrong_lot_substitution(self):
        project_cache.put(self.data)
        self.assertEqual(project_cache.match({**self.data,'name':'Maple','lot':'96'})['status'], 'ProjectMatched')
        self.assertEqual(project_cache.match({**self.data,'name':'Maple Grove','lot':'58'})['status'], 'NeedsProjectSelection')
        other = copy.deepcopy(self.data);other['project']['lot']='58';project_cache.put(other)
        self.assertEqual(project_cache.match({**self.data,'name':'Maple Grove'})['status'], 'NeedsProjectSelection')

    def test_registered_cold_project_does_not_create_spurious_human_selection(self):
        data = {**self.data,'name':'Maple Grove','lot':'96','registered_projects':[self.data['project']]}
        self.assertEqual(project_cache.match(data)['status'], 'ProjectMatched')
        self.assertEqual(project_cache.get(self.data)['status'], 'ProjectCacheMiss')

    def test_scope_account_root_revocation_and_workspace_isolation(self):
        project_cache.put(self.data)
        for field,value in [('workspace_id',SOURCE),('account_id','other'),('authorized_roots',['/Aimore/Other'])]:
            data=copy.deepcopy(self.data);data['scope'][field]=value
            self.assertEqual(project_cache.get(data)['status'],'ProjectCacheMiss')

    def test_expiry_known_revision_change_and_invalidation_refresh_only_affected_project(self):
        saved=project_cache.put(self.data)
        expired={**self.data,'now':'2026-11-05T00:00:00Z'}
        self.assertEqual(project_cache.get(expired)['status'],'ProjectCacheRefreshRequired')
        changed={**self.data,'expected_revisions':{'actual-file':'rev-3'}}
        self.assertEqual(project_cache.get(changed)['status'],'ProjectCacheRefreshRequired')
        project_cache.invalidate(self.data)
        self.assertEqual(project_cache.get(self.data)['status'],'ProjectCacheMiss')
        self.assertTrue(any(Path(self.tmp.name).rglob(saved['snapshot_id']+'.json')))

    def test_scope_missing_provenance_or_empty_failed_file_cannot_warm_cache(self):
        for edit in (lambda d:d['files'][0].update(path='/Private/file.md'),
                     lambda d:d['files'][0].update(text=''),
                     lambda d:d['files'][0].update(status='Superseded'),
                     lambda d:d['fact_sources'].update(price=['not-read']),
                     lambda d:d['facts'].update(send_approval=True),
                     lambda d:d['scope'].update(authorized_roots=[])):
            data=copy.deepcopy(self.data);edit(data)
            with self.assertRaises(ValueError):project_cache.put(data)

    def test_immutable_snapshot_and_atomic_pointer_support_restart_and_new_versions(self):
        first=project_cache.put(self.data)
        updated=copy.deepcopy(self.data);updated['files'][0].update(text='New price AUD910,000.',rev='rev-3',version='v3')
        updated['facts']['price']=910000
        second=project_cache.put(updated)
        self.assertNotEqual(first['snapshot_id'],second['snapshot_id'])
        self.assertEqual(project_cache.get(self.data)['facts']['price'],910000)
        self.assertTrue(any(Path(self.tmp.name).rglob(first['snapshot_id']+'.json')))
        self.assertEqual(project_cache.catalog(self.data)['projects'][0]['snapshot_id'],second['snapshot_id'])

    def test_corrupt_cache_requests_refresh_instead_of_claiming_missing_project_facts(self):
        saved=project_cache.put(self.data)
        snapshot=next(Path(self.tmp.name).rglob(saved['snapshot_id']+'.json'));snapshot.write_text('{}')
        self.assertEqual(project_cache.get(self.data)['status'],'ProjectCacheRefreshRequired')

    def test_unavailable_local_storage_is_an_explicit_fresh_source_fallback(self):
        with patch.object(project_cache, 'write_json', side_effect=PermissionError('Read-only host state')):
            result = project_cache.put(self.data)
        self.assertEqual(result['status'], 'ProjectCacheUnavailable')
        self.assertFalse(result['send_authority'])
        self.assertIn('authorized fresh', result['fallback'])

    def test_local_batch_invokes_the_real_cache_and_short_flow_operations(self):
        out=local_checks.run({'checks':[{'name':'put','operation':'project.cache-put','input':self.data},
                                       {'name':'get','operation':'project.cache-get','input':self.data}]},{})
        self.assertEqual(out['status'],'LocalChecksPassed')
        self.assertEqual(out['checks'][1]['result']['status'],'ProjectCacheHit')


if __name__=='__main__': unittest.main()
