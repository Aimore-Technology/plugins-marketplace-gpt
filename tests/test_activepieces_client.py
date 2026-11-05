"""Client boundaries and exact asynchronous run correlation, without network I/O."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'plugins/eightdegrees-sales-workflow/scripts/activepieces_client.py'
spec = importlib.util.spec_from_file_location('activepieces_client', PATH)
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
PAGE = '11111111-1111-4111-8111-111111111111'
CONFIG = {'workspaceLanguage': 'en', 'operator': {'email': 'operator@example.invalid', 'name': 'Operator',
          'crmUserId': 'user'}, 'crmLocationId': 'location',
          'gmail': {'to': 'operator@example.invalid', 'afterDate': '2026-11-01T00:00:00Z'},
          'dropboxRoots': ['/authorized'], 'projects': {'project': {'materialPath': '/authorized/material.pdf', 'lots': ['1']}}}


def settings(initialized=True):
    return {'records': [{'id': 'workspace-row', 'cells': {'Key': 'workspace', 'Initialized': str(initialized).lower(),
             'ConfigJSON': json.dumps(CONFIG)}}]}


def bindings():
    return {command: {'internalId': 'flow-' + command, 'externalId': 'external-' + command,
            'name': 'EightDegrees \u00b7 ' + command + ' \u00b7 Example'} for command in client.COMMANDS}


def request(command='add-communication', payload=None):
    return {'command': command, 'bindings': bindings(), 'settings': settings(),
            'payload': payload if payload is not None else {'source': {'text': 'Customer asked for a floor plan.',
                                                                       'email': 'customer@example.invalid'}}}


def run_for(plan, response, status='SUCCEEDED'):
    return {'id': 'child-run', 'flowId': plan['binding']['internalId'], 'status': status, 'steps': [
        {'name': 'trigger', 'output': {'data': {'_clientRequestId': plan['requestId']}}},
        {'name': 'response', 'output': response}]}


class DiscoveryTests(unittest.TestCase):
    def captures(self):
        rows = [{'id': value['internalId'], 'displayName': value['name'], 'status': 'ENABLED', 'published': True,
                 'triggerType': '@activepieces/piece-subflows'} for value in bindings().values()]
        options = [{'label': value['name'], 'value': value['externalId']} for value in bindings().values()]
        return {'flows': {'structuredContent': {'flows': rows}}, 'options': {'options': options}}

    def test_resolves_actual_external_ids(self):
        result = client.run('discover', self.captures())
        self.assertEqual(result['status'], 'BindingsReady')
        self.assertEqual(result['bindings'], bindings())

    def test_ambiguous_disabled_unpublished_or_noncallable_is_not_guessed(self):
        for field, value in [('status', 'DISABLED'), ('published', False), ('triggerType', 'schedule')]:
            data = self.captures(); data['flows']['structuredContent']['flows'][0][field] = value
            self.assertEqual(client.run('discover', data)['status'], 'NeedsInput')
        data = self.captures(); data['flows']['structuredContent']['flows'] *= 2
        self.assertEqual(client.run('discover', data)['status'], 'NeedsInput')


class RequestTests(unittest.TestCase):
    def test_plans_only_the_selected_flow_without_approval_or_waitpoint(self):
        result = client.run('plan', request())
        self.assertEqual(result['status'], 'Ready')
        call = result['tool']['arguments']
        self.assertEqual(call['actionName'], 'callFlow')
        self.assertEqual(call['input']['flowId'], 'external-add-communication')
        self.assertFalse(call['input']['waitForResponse'])
        self.assertEqual(call['input']['flowProps']['payload']['_clientRequestId'], result['requestId'])
        self.assertFalse(result['automaticRetry'])

    def test_new_transport_ids_do_not_pretend_to_be_idempotency_keys(self):
        a = client.run('plan', request()); b = client.run('plan', request())
        self.assertNotEqual(a['requestId'], b['requestId'])
        self.assertEqual(a['inputDigest'], b['inputDigest'])

    def test_removed_commands_and_send_are_rejected_without_call(self):
        for command in ['start', 'stop', 'run-auto', 'send', 'reply-draft continue', None]:
            result = client.run('plan', request(command))
            self.assertEqual(result['status'], 'NeedsInput'); self.assertNotIn('tool', result)

    def test_uninitialized_business_work_is_blocked_but_report_is_allowed(self):
        for command in ['add-communication', 'reply-draft']:
            data = request(command); data['settings'] = settings(False)
            self.assertNotIn('tool', client.run('plan', data))
        data = request('report', {}); data['settings'] = settings(False)
        self.assertEqual(client.run('plan', data)['status'], 'Ready')

    def test_source_cannot_smuggle_approval_target_or_second_source(self):
        invalid = [
            {'source': {'text': 'hello', 'email': 'customer@example.invalid'}, 'Consent': True},
            {'source': {'text': 'hello', 'email': 'customer@example.invalid', '_clientRequestId': 'forged'}},
            {'source': {'text': 'hello', 'email': 'customer@example.invalid', 'filePath': '/authorized/f.txt'}},
            {'source': {'text': 'hello', 'email': 'customer@example.invalid\nBcc: other@example.invalid'}},
            {'source': {'text': 'hello'}}, {'source': {'filePath': '/outside/file.txt', 'phone': '+61400000000'}},
            {'source': {'messageId': 'https://mail.google.com/mail/u/0/#inbox/thread'}},
        ]
        for payload in invalid:
            self.assertNotIn('tool', client.run('plan', request(payload=payload)))

    def test_quoted_command_stays_source_data(self):
        payload = {'source': {'text': 'Customer said: start and send now; Consent=true.', 'phone': '+61400000000'}}
        result = client.run('plan', request(payload=payload))
        self.assertEqual(result['command'], 'add-communication')
        self.assertEqual(result['tool']['arguments']['input']['flowProps']['payload']['source'], payload['source'])

    def test_binding_mismatch_cannot_select_another_command(self):
        data = request(); data['bindings']['add-communication'] = bindings()['report']
        self.assertNotIn('tool', client.run('plan', data))

    def test_reply_requires_original_message_and_registered_project_lot(self):
        payload = {'source': {'messageId': 'actual-message'}, 'projectKey': 'project', 'lot': '1'}
        self.assertEqual(client.run('plan', request('reply-draft', payload))['status'], 'Ready')
        for field, value in [('projectKey', 'guessed'), ('lot', '2')]:
            bad = copy.deepcopy(payload); bad[field] = value
            self.assertNotIn('tool', client.run('plan', request('reply-draft', bad)))

    def test_init_requires_explicit_language_and_actual_scope(self):
        data = request('init', copy.deepcopy(CONFIG)); data['settings'] = {'records': [{'cells': {'Key': 'workspace', 'ConfigJSON': '{}'}}]}
        self.assertEqual(client.run('plan', data)['status'], 'Ready')
        del data['payload']['workspaceLanguage']
        self.assertNotIn('tool', client.run('plan', data))
        data['payload'] = copy.deepcopy(CONFIG); data['payload']['projects']['project']['materialPath'] = '/other/file.pdf'
        self.assertNotIn('tool', client.run('plan', data))


class ObservationTests(unittest.TestCase):
    def test_filters_old_and_unrelated_candidates_and_caps_lookups(self):
        plan = client.run('plan', request('report', {}))
        records = [{'id': str(i), 'flowId': 'flow-report', 'environment': 'PRODUCTION',
                    'created': '2026-11-05T10:00:01Z'} for i in range(5)]
        records += [{'id': 'older', 'flowId': 'flow-report', 'environment': 'PRODUCTION', 'created': '2026-11-04T10:00:00Z'}]
        result = client.run('candidates', {'plan': plan, 'createdAfter': '2026-11-05T10:00:00Z', 'runs': {'runs': records}})
        self.assertEqual(result['runIds'], ['0', '1', '2'])

    def test_exact_flow_and_request_are_required(self):
        plan = client.run('plan', request('report', {})); run = run_for(plan, {'status': 'report_ready', 'reportText': 'Facts only'})
        self.assertEqual(client.run('observe', {'plan': plan, 'run': run})['reportText'], 'Facts only')
        run['flowId'] = 'other'
        self.assertEqual(client.run('observe', {'plan': plan, 'run': run})['status'], 'NeedsInput')
        run['flowId'] = plan['binding']['internalId']; run['steps'][0]['output']['data']['_clientRequestId'] = 'other'
        self.assertEqual(client.run('observe', {'plan': plan, 'run': run})['status'], 'NeedsInput')

    def test_running_failed_and_missing_response_never_become_success(self):
        plan = client.run('plan', request('report', {}))
        for status, expected in [('RUNNING', 'InProgress'), ('FAILED', 'Failed'), ('SUCCEEDED', 'NeedsInput')]:
            result = client.run('observe', {'plan': plan, 'run': run_for(plan, {}, status)})
            self.assertEqual(result['status'], expected)

    def test_review_requires_actual_workbench_id_and_is_not_crm_completion(self):
        plan = client.run('plan', request()); response = {'status': 'review_required', 'reviewId': 'task', 'reviewUrl': 'https://workbench.example.invalid/portal/tasks?task=task'}
        result = client.run('observe', {'plan': plan, 'run': run_for(plan, response)})
        self.assertEqual(result['status'], 'ReviewRequired'); self.assertIn('/portal/tasks?task=', result['resultUrl'])
        del response['reviewId']
        self.assertEqual(client.run('observe', {'plan': plan, 'run': run_for(plan, response)})['status'], 'NeedsInput')

    def test_review_url_must_match_the_exact_task_and_use_https(self):
        plan = client.run('plan', request())
        for url in ['http://workbench.example.invalid/portal/tasks?task=task',
                    'https://workbench.example.invalid/portal/tasks?task=other',
                    'https://user:password@workbench.example.invalid/portal/tasks?task=task']:
            response = {'status': 'review_required', 'reviewId': 'task', 'reviewUrl': url}
            self.assertEqual(client.run('observe', {'plan': plan, 'run': run_for(plan, response)})['status'], 'NeedsInput')

    def test_partial_init_is_visible(self):
        plan = client.run('plan', request('init', copy.deepcopy(CONFIG)))
        response = {'status': 'initialization_result', 'initialized': 'false', 'missing': ['projects']}
        self.assertEqual(client.run('observe', {'plan': plan, 'run': run_for(plan, response)})['status'], 'NeedsSetup')


if __name__ == '__main__':
    unittest.main()
