"""Persisted handoff, resend and failure regressions without external effects."""

import copy
import json
import unittest

from test_notion_checks import page, REPORT
import material_handoff as HANDOFF


def inputs():
    return {"root_id": "a" * 32, "email_task_id": REPORT, "content_version": "test-v1",
            "event": {"status": "Sent", "material": True, "provider": "gmail",
                      "account": "operator@example.com", "message_id": "sent-one",
                      "location_id": "location-one", "contact_id": "contact-one",
                      "context_key": "thread-one", "sent_at": "2026-11-02T00:00:00Z"},
            "cycle_query_complete": True, "cycles": [], "stop": False,
            "manual_pause": False, "recipient": "+61400000000",
            "channel_verified": True, "automatic_sms_enabled": True}


def cycle(data):
    r = HANDOFF.plan(data)["record"]
    return {k: r[k] for k in ("cycle_key", "location_id", "contact_id", "context_key")} | {
        "page_id": "d" * 32, "material_events": [r["event_key"]],
        "active": True, "total_count": 1, "unknown_attempt": False}


def saved(data, field="saved_cycle"):
    record = HANDOFF.plan(data)["record"]
    result = page("```json\n" + json.dumps(record) + "\n```")
    if field == "saved_cycle":
        result["id"] = "d" * 32
    return result


def authorized(data):
    """Original saved installation + current inquiry initiation (offline)."""
    data['observed_at'] = '2026-11-02T00:01:00Z'
    data['event']['source_message_id'] = 'inquiry-new'
    settings_id = 'f' * 32
    context = data['event']['context_key']
    override = {'explicitly_initiated': True, 'context_key': context,
                'source_message_id': 'inquiry-new', 'recipient': data['recipient'],
                'first_delay_minutes': 0, 'max_messages_per_cycle_including_manual': 1,
                'second_sms_allowed': False, 'expires_at': '2026-11-02T02:00:00Z',
                'authorization_ref': 'https://app.notion.com/p/' + 'e' * 32}
    config = {'settings_schema_version': 2,
              'customer_setup': {'notion_root_id': data['root_id'], 'operator_id': 'operator-one',
                                 'notion_ids': {'settings': settings_id},
                                 'gmail_account': data['event']['account'], 'crm_location_id': 'location-one'},
              'sms_follow_up': {'automatic_sending_enabled': True, 'first_delay_minutes': 30,
                                'context_overrides': {context: override}},
              'sms_notifications': {'policy': 'notification-sms-v1', 'enabled': True, 'revoked_at': None,
                                    'per_message_review_required': False, 'root_id': data['root_id'],
                                    'operator_id': 'operator-one'},
              'enquiries': {context: {'location_id': 'location-one', 'contact_id': 'contact-one',
                                     'phone': data['recipient'], 'source_message_id': 'inquiry-new'}},
              'sms_stops': {'old-thread': {'location_id': 'location-one', 'contact_id': 'contact-one',
                                          'context_key': 'old-thread', 'channel': 'sms', 'stopped': True}}}
    set_settings(data, config, settings_id)
    return config


def set_settings(data, config, identity='f' * 32):
    data['saved_settings'] = page('```json\n' + json.dumps(config) + '\n```')
    data['saved_settings']['id'] = identity


def history(data):
    prior = copy.deepcopy(data)
    prior['event'].update(message_id='sent-old', context_key='old-thread')
    c = cycle(prior)
    c.update(active=False, context_key='old-thread', material_events=[], stop=True, maximum_count=1)
    data['cycles'] = [c]
    return c


def recovery(data):
    """Original failed registration with no attempted SMS, as in the incident."""
    old = copy.deepcopy(data)
    old.pop('saved_settings', None)
    original = HANDOFF.plan(old)['record']
    current = {'record_type': 'sms-cycle-current-state', 'cycle_id': original['cycle_key'],
               'location_id': 'location-one', 'contact_id': 'contact-one', 'context_key': data['event']['context_key'],
               'active': False, 'stop': False, 'manual_pause': False, 'total_count': 0,
               'reserved_slots': 0, 'source_message_id': data['event']['source_message_id'],
               'state': 'BlockedImplementation', 'blocked_reason': 'ClosedPriorContextBlocksExplicitNewContext'}
    settings_body = data['saved_settings']['text']
    config = json.loads(settings_body.split('```json\n')[1].split('\n```')[0])
    current.update(authorization=copy.deepcopy(config['sms_follow_up']['context_overrides'][data['event']['context_key']]),
                   maximum_count=1, second_sms_allowed=False)
    c = {k: original[k] for k in ('cycle_key', 'location_id', 'contact_id', 'context_key')}
    c.update(page_id='c' * 32, material_events=[original['event_key']], active=False,
             total_count=0, unknown_attempt=False, state='BlockedImplementation')
    data['cycles'].append(c)
    set_recovery(data, original, current)
    return original, current


def set_recovery(data, original, current):
    data['recovery_cycle_page'] = page('```json\n' + json.dumps(original) + '\n```\n\n```json\n'
                                       + json.dumps(current) + '\n```')
    data['recovery_cycle_page']['id'] = 'c' * 32


class MaterialHandoffTests(unittest.TestCase):
    def test_explicit_new_inquiry_is_not_blocked_by_an_old_project_stop(self):
        data = inputs(); old = history(data); authorized(data)
        before = copy.deepcopy(data)
        r = HANDOFF.plan(data)['record']
        self.assertEqual(r['state'], 'ReadyForNotification')
        self.assertEqual(r['operation'], 'create')
        self.assertNotEqual(r['cycle_key'], old['cycle_key'])
        self.assertEqual(r['first_due_not_before'], data['event']['sent_at'].replace('Z', '+00:00'))
        self.assertEqual(r['maximum_count'], 1); self.assertFalse(r['second_sms_allowed'])
        self.assertEqual(r['total_count'], 0); self.assertFalse(r['customer_send_allowed'])
        self.assertEqual(data, before)

    def test_global_current_stop_and_manual_pause_still_win_over_new_authorization(self):
        for field in ('stop', 'manual_pause'):
            data = inputs(); history(data); authorized(data); data[field] = True
            self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Stopped')
        for scope in ('thread-one', '*'):
            data = inputs(); history(data); config = authorized(data)
            config['sms_stops']['old-thread']['context_key'] = scope
            set_settings(data, config)
            self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Stopped')

    def test_disabled_gateway_still_blocks_an_authorized_new_inquiry(self):
        data = inputs(); history(data); authorized(data); data['channel_verified'] = False
        self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Blocked')

    def test_loose_boolean_is_not_explicit_new_context_evidence(self):
        data = inputs(); history(data)
        data['new_context_authorized'] = True
        self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Stopped')

    def test_authorization_bindings_expiry_revocation_and_policy_are_checked(self):
        changes = [
            ('customer_setup', 'notion_root_id', 'b' * 32),
            ('customer_setup', 'gmail_account', 'other@example.com'),
            ('customer_setup', 'crm_location_id', 'another'),
            ('sms_notifications', 'enabled', False),
            ('sms_notifications', 'revoked_at', '2026-11-02T00:00:00Z'),
            ('sms_notifications', 'per_message_review_required', True),
            ('sms_notifications', 'operator_id', 'other'),
        ]
        for section, field, value in changes:
            with self.subTest(section=section, field=field):
                data = inputs(); history(data); config = authorized(data)
                config[section][field] = value; set_settings(data, config)
                with self.assertRaises(ValueError): HANDOFF.plan(data)
        changes = {'explicitly_initiated': False, 'context_key': 'old-thread',
                   'recipient': '+61400000001', 'source_message_id': 'another',
                   'expires_at': '2026-11-02T00:01:00Z', 'first_delay_minutes': True,
                   'max_messages_per_cycle_including_manual': True, 'second_sms_allowed': True,
                   'authorization_ref': 'missing', 'revoked_at': '2026-11-02T00:00:00Z'}
        for field, value in changes.items():
            with self.subTest(field=field):
                data = inputs(); history(data); config = authorized(data)
                config['sms_follow_up']['context_overrides']['thread-one'][field] = value
                set_settings(data, config)
                with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_authorization_cannot_move_to_another_source_contact_or_number(self):
        for section, field, value in [('enquiries', 'contact_id', 'other'),
                                      ('enquiries', 'source_message_id', 'other'),
                                      ('enquiries', 'phone', '+61400000001')]:
            data = inputs(); history(data); config = authorized(data)
            config[section]['thread-one'][field] = value; set_settings(data, config)
            with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); history(data); authorized(data); data['event']['source_message_id'] = 'other'
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_truncated_or_duplicate_settings_cannot_authorize_a_cycle(self):
        data = inputs(); history(data); authorized(data)
        data['saved_settings']['truncated'] = True
        with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); history(data); config = authorized(data)
        data['saved_settings']['text'] = data['saved_settings']['text'].replace(
            '</content>', '```json\n' + json.dumps(config) + '\n```\n</content>')
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_explicit_authorization_never_reopens_same_context_closed_cycle(self):
        for change in ({'active': False}, {'total_count': 1, 'maximum_count': 1},
                       {'stop': True}, {'manual_pause': True}):
            data = inputs(); c = cycle(data); c.update(change); data['cycles'] = [c]; authorized(data)
            before = copy.deepcopy(data)
            r = HANDOFF.plan(data)['record']
            self.assertEqual(r['state'], 'Stopped'); self.assertEqual(r['operation'], 'reuse')
            self.assertEqual(r['cycle_key'], c['cycle_key']); self.assertEqual(data, before)

    def test_active_other_context_is_reused_not_a_second_active_cycle(self):
        data = inputs(); old = history(data); old.update(active=True, stop=False, total_count=0)
        authorized(data)
        r = HANDOFF.plan(data)['record']
        self.assertEqual(r['operation'], 'reuse'); self.assertEqual(r['cycle_key'], old['cycle_key'])

    def test_unknown_history_and_competing_active_cycles_are_not_bypassed(self):
        data = inputs(); old = history(data); old['unknown_attempt'] = True; authorized(data)
        with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); history(data); authorized(data); recovery(data)
        data['cycles'][0]['active'] = True
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_original_zero_attempt_implementation_stub_recovers_in_place(self):
        data = inputs(); history(data); authorized(data); recovery(data)
        before = copy.deepcopy(data)
        r = HANDOFF.plan(data)['record']
        self.assertEqual(r['state'], 'ReadyForNotification'); self.assertEqual(r['operation'], 'reuse')
        self.assertEqual(r['cycle_key'], data['cycles'][1]['cycle_key'])
        self.assertEqual(r['registration_recovery'], 'ClosedPriorContextBlocksExplicitNewContext')
        self.assertEqual(r['total_count'], 0); self.assertEqual(data, before)
        original = saved(data, 'email'); cycle_page = saved(data)
        cycle_page['id'] = 'c' * 32
        self.assertEqual(HANDOFF.verify({'input': data, 'saved_email_task': original,
                                        'saved_cycle': cycle_page})['cycle_page_id'], 'c' * 32)

    def test_recovery_cannot_reopen_a_stop_pause_reserved_attempt_or_wrong_original(self):
        changes = {'stop': True, 'manual_pause': True, 'total_count': 1, 'reserved_slots': 1, 'reserved_count': 1,
                   'unknown_attempt': True, 'last_request_id': 'request-one',
                   'attempts': [{'state': 'Unknown'}], 'current_outcome': {'sent': False},
                   'state': 'Closed', 'source_message_id': 'other', 'maximum_count': 2,
                   'second_sms_allowed': True, 'authorization': {'explicitly_initiated': True}}
        for field, value in changes.items():
            with self.subTest(field=field):
                data = inputs(); history(data); authorized(data); old, current = recovery(data)
                current[field] = value; set_recovery(data, old, current)
                with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); history(data); authorized(data); recovery(data)
        data.pop('recovery_cycle_page')
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_retry_reuses_authorized_cycle_and_cannot_reset_one_message_limit(self):
        data = inputs(); history(data); authorized(data)
        record = HANDOFF.plan(data)['record']
        c = {k: record[k] for k in ('cycle_key', 'location_id', 'contact_id', 'context_key', 'maximum_count')}
        c.update(page_id='c' * 32, material_events=[record['event_key']], active=True,
                 total_count=1, unknown_attempt=False)
        data['cycles'].append(c)
        for sent_id in ('sent-one', 'resent-two'):
            data['event']['message_id'] = sent_id
            r = HANDOFF.plan(data)['record']
            self.assertEqual(r['state'], 'Stopped'); self.assertEqual(r['cycle_key'], c['cycle_key'])
            self.assertEqual(r['total_count'], 1)

    def test_current_saved_one_message_limit_applies_even_to_legacy_cycle_projection(self):
        data = inputs(); history(data); authorized(data)
        record = HANDOFF.plan(data)['record']
        c = {k: record[k] for k in ('cycle_key', 'location_id', 'contact_id', 'context_key')}
        c.update(page_id='c' * 32, material_events=[record['event_key']], active=True,
                 total_count=1, unknown_attempt=False)
        data['cycles'].append(c)
        self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Stopped')

    def test_reuse_preserves_the_original_cycle_timer_and_lower_limit(self):
        data = inputs(); existing = cycle(data)
        existing.update(total_count=0, maximum_count=1, first_due_not_before='2026-11-02T04:00:00Z')
        data['cycles'] = [existing]; authorized(data)
        data['event']['message_id'] = 'resend-two'
        r = HANDOFF.plan(data)['record']
        self.assertEqual(r['first_due_not_before'], '2026-11-02T04:00:00+00:00')
        self.assertEqual(r['maximum_count'], 1); self.assertFalse(r['second_sms_allowed'])

    def test_upgrade_recovery_wakes_once_then_idle_without_replaying_the_email(self):
        import event_probe
        from test_event_probe import fixture, saved as saved_index
        data = inputs(); history(data); authorized(data); recovery(data)
        r = HANDOFF.plan(data)['record']
        probe = fixture()
        probe['observations']['recovery']['records'] = [{
            'id': 'c' * 32, 'revision': 'scoped-sms-initiation-v2:' + r['authorization']['authorization_sha256'],
            'events': [{'kind': 'recovery', 'evidence_ref': 'https://app.notion.com/p/' + 'c' * 32,
                        'source_key': r['event_key'], 'step': 'PrepareSmsFollowUp', 'version': 'followup-v1',
                        'input_digest': r['authorization']['authorization_sha256']}]}]
        ready = event_probe.probe(probe)
        self.assertEqual(ready['status'], 'ScanWorkReady'); self.assertEqual(len(ready['ready']), 1)
        self.assertEqual(ready['ready'][0]['step'], 'PrepareSmsFollowUp')
        probe['index_page'] = saved_index(ready)
        probe['acknowledgements'] = [{'key': ready['ready'][0]['key'], 'state': 'completed',
                                     'receipt_ref': 'capture:saved-registration-and-notification-wake'}]
        done = event_probe.probe(probe)
        self.assertEqual(done['status'], 'ScanIdle')
        probe['index_page'] = saved_index(done); probe.pop('acknowledgements')
        again = event_probe.probe(probe)
        self.assertEqual(again['status'], 'ScanIdle'); self.assertFalse(again['persist_required'])

    def test_nonmaterial_reply_records_not_applicable_without_a_cycle_or_sms(self):
        data = inputs(); data['event']['material'] = False
        r = HANDOFF.plan(data)['record']
        self.assertEqual(r['state'], 'NotApplicable'); self.assertNotIn('cycle_key', r)
        result = HANDOFF.verify({'input': data, 'saved_email_task': saved(data, 'email')})
        self.assertEqual(result['status'], 'MaterialHandoffVerified'); self.assertIsNone(result['cycle_page_id'])
        data['event']['material'] = None
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_closed_unrelated_cycle_requires_manual_new_context_authorization(self):
        data = inputs(); c = cycle(data); c.update(active=False, context_key='old-thread', material_events=[])
        data['cycles'] = [c]
        self.assertEqual(HANDOFF.plan(data)['record']['state'], 'Stopped')

    def test_actual_send_plans_one_registration_and_never_a_dispatch_or_cron(self):
        data = inputs(); before = copy.deepcopy(data)
        r = HANDOFF.plan(data)["record"]
        self.assertEqual(r["state"], "ReadyForNotification")
        self.assertEqual(r["first_due_not_before"], "2026-11-02T00:30:00+00:00")
        self.assertFalse(r["create_native_task"]); self.assertFalse(r["customer_send_allowed"])
        self.assertEqual(data, before)

    def test_disabled_channel_or_missing_number_still_produces_observable_blocked_handoff(self):
        for field, value in (("recipient", None), ("channel_verified", False), ("automatic_sms_enabled", False)):
            data = inputs(); data[field] = value
            r = HANDOFF.plan(data)["record"]
            self.assertEqual(r["state"], "Blocked"); self.assertTrue(r["reasons"])

    def test_unknown_email_and_incomplete_discovery_do_not_enroll(self):
        for status in ("Unknown", "Draft", "Accepted"):
            data = inputs(); data["event"]["status"] = status
            with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); data["cycle_query_complete"] = False
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_same_event_and_resend_preserve_original_cycle_and_manual_ai_count(self):
        data = inputs(); existing = cycle(data); data["cycles"] = [existing]
        for message in ("sent-one", "sent-again"):
            data["event"]["message_id"] = message
            r = HANDOFF.plan(data)["record"]
            self.assertEqual(r["operation"], "reuse")
            self.assertEqual(r["cycle_key"], existing["cycle_key"]); self.assertEqual(r["total_count"], 1)

    def test_stop_pause_and_closed_or_capped_cycle_never_reopen(self):
        for field in ("stop", "manual_pause"):
            data = inputs(); data[field] = True
            self.assertEqual(HANDOFF.plan(data)["record"]["state"], "Stopped")
        for change in ({"active": False}, {"total_count": 2}):
            data = inputs(); c = cycle(data); c.update(change); data["cycles"] = [c]
            r = HANDOFF.plan(data)["record"]
            self.assertEqual(r["state"], "Stopped"); self.assertEqual(r["operation"], "reuse")

    def test_unknown_count_attempt_and_competing_cycles_require_reconciliation(self):
        for change in ({"total_count": None}, {"total_count": True}, {"unknown_attempt": True}):
            data = inputs(); c = cycle(data); c.update(change); data["cycles"] = [c]
            with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); data["cycles"] = [cycle(data), cycle(data)]
        with self.assertRaises(ValueError): HANDOFF.plan(data)

    def test_changed_context_or_version_does_not_change_provider_event_identity(self):
        data = inputs(); original = HANDOFF.plan(data)["record"]["event_key"]
        data["event"]["context_key"] = "new-context"
        self.assertEqual(HANDOFF.plan(data)["record"]["event_key"], original)

    def test_original_email_and_distinct_cycle_readback_are_required(self):
        data = inputs(); payload = {"input": data, "saved_email_task": saved(data, "email"), "saved_cycle": saved(data)}
        self.assertEqual(HANDOFF.verify(payload)["status"], "MaterialHandoffVerified")
        for field in ("saved_email_task", "saved_cycle"):
            changed = copy.deepcopy(payload); changed[field]["truncated"] = True
            with self.assertRaises(ValueError): HANDOFF.verify(changed)
            changed = copy.deepcopy(payload); changed[field]["text"] = changed[field]["text"].replace('ReadyForNotification', 'Sent')
            with self.assertRaises(ValueError): HANDOFF.verify(changed)
        payload["saved_cycle"]["id"] = REPORT
        with self.assertRaises(ValueError): HANDOFF.verify(payload)

    def test_reuse_cannot_persist_to_a_duplicate_cycle_page(self):
        data = inputs(); data["cycles"] = [cycle(data)]
        payload = {"input": data, "saved_email_task": saved(data, "email"), "saved_cycle": saved(data)}
        self.assertEqual(HANDOFF.verify(payload)["status"], "MaterialHandoffVerified")
        payload["saved_cycle"]["id"] = "e" * 32
        with self.assertRaises(ValueError): HANDOFF.verify(payload)

    def test_display_markdown_and_naive_time_cannot_supply_source_identity(self):
        data = inputs(); data["event"]["contact_id"] = "[Customer](https://example.com)"
        with self.assertRaises(ValueError): HANDOFF.plan(data)
        data = inputs(); data["event"]["sent_at"] = "2026-11-02T00:00:00"
        with self.assertRaises(ValueError): HANDOFF.plan(data)
