"""Scope, restart and standing-notification regressions without connector I/O."""
import copy
import json
import unittest

from test_email_presentation import page, block
from test_handover_regressions_037 import capture
from test_material_handoff import inputs, history, authorized, set_settings
from test_sms_authority import inputs as sms_inputs, saved as sms_saved, current_material
from test_pre_action_order import dispatch, ready
from test_unattended import cycle_fixture
import invocation_context
import material_handoff
import sms_authority
import scan_cycle
import dispatch_admission

def context(policy='one-cycle-no-customer-send'):
    args={'command':'run-auto','policy':policy,'restrictions':['Do not send customer messages'],
          'invocation_id':'turn','executor_id':'thread','root_id':'a'*32,
          'started_at':'2026-11-03T04:00:00Z'}
    record=invocation_context.prepare(args)['record']
    return args|{'context_record':record,'now':'2026-11-03T04:01:00Z'}

def scope(contact, **extra):
    return {'location_id':'location','contact_id':contact,**extra}

def scoped_cycle():
    d=cycle_fixture()
    d.update(budget_seconds=900,reserve_seconds=120,now='2026-11-01T00:10:01Z')
    d['items']=[
        {'source_key':'customer-A','step':'SendNotificationSms','version':'v1','input_digest':'old',
         'unknown_attempt':True,'attempt_id':'original-A','estimated_seconds':600,'scope':scope('A')},
        {'source_key':'customer-B','step':'ReviewCommunication','version':'v1','input_digest':'new',
         'estimated_seconds':60,'scope':scope('B')}]
    return d

def limits_fixture():
    d=inputs();old=history(d);old.update(active=True,stop=False,total_count=0,maximum_count=2)
    authorized(d)
    record=material_handoff.plan(d)['record']
    state={'record_type':'sms-cycle-current-state','cycle_id':record['cycle_key'],
           'location_id':'location-one','contact_id':'contact-one','context_key':'old-thread',
           'active':True,'stop':False,'manual_pause':False,'unknown_attempt':False,
           'count_verified':True,'total_count':0,'reserved_count':0,'maximum_count':2,
           'context_counts_complete':True,'context_counts':{'old-thread':0,'thread-one':0}}
    original=page('d'*32,block(state),{})
    return d,{'limits':record['notification_limits'],'saved_cycle':original,
              'cycle_page_id':'d'*32,'now':'2026-11-02T00:01:00Z'},state

def saved_state(data,state):
    data['saved_cycle']=page('d'*32,block(state),{})

class InvocationRestrictions(unittest.TestCase):
    def test_recovered_no_send_policy_still_blocks_both_dispatch_channels(self):
        policy=invocation_context.resume(context())['policy']
        for channel in ['email','sms']:
            d=dispatch(channel);d['scan']['policy']=policy
            with self.assertRaises(ValueError):dispatch_admission.prepare(d)

    def test_no_send_policy_and_extra_restrictions_survive_compaction(self):
        d=context();r=invocation_context.resume(d)
        self.assertEqual(r['policy'],'one-cycle-no-customer-send')
        self.assertEqual(r['default_policy'],'one-cycle-approved-work')
        self.assertEqual(r['restrictions'],d['restrictions'])
        self.assertFalse(r['external_actions_allowed'])

    def test_changed_policy_restrictions_or_default_cannot_resume(self):
        for patch in [{'policy':'one-cycle-approved-work'},{'restrictions':[] }]:
            d=context();d.update(patch)
            with self.assertRaises(ValueError):invocation_context.resume(d)
        d=context();d['context_record']['default_policy']='draft-only'
        with self.assertRaises(ValueError):invocation_context.resume(d)

    def test_other_commands_cannot_use_a_broader_policy(self):
        for command in ['init','report','reply-draft','add-communication','start','stop']:
            d=context();d['command']=command;d['policy']='one-cycle-approved-work'
            with self.assertRaises(ValueError):invocation_context.prepare(d)

    def test_legacy_pin_without_effective_restrictions_is_closeout_only(self):
        d=context('one-cycle-approved-work');d.pop('restrictions')
        d['context_record'].pop('default_policy');d['context_record'].pop('restrictions')
        r=invocation_context.resume(d)
        self.assertTrue(r['legacy_restrictions_unverified']);self.assertTrue(r['closeout_only'])
        self.assertEqual(r['policy'],'one-cycle-no-customer-send')

class MaterialContext(unittest.TestCase):
    def test_one_message_exception_keeps_cap_expiry_recipient_and_delay_on_reuse(self):
        d,g,_=limits_fixture();before=copy.deepcopy(d)
        r=material_handoff.plan(d)['record']
        self.assertEqual(r['operation'],'reuse');self.assertEqual(r['maximum_count'],1)
        self.assertFalse(r['second_sms_allowed']);self.assertEqual(r['authorization']['authorization_kind'],'context-override')
        self.assertEqual(g['limits']['expires_at'],'2026-11-02T02:00:00Z')
        self.assertEqual(g['limits']['cycle_maximum_count'],2)
        self.assertEqual(g['limits']['first_due_not_before'],'2026-11-02T00:00:00+00:00')
        self.assertEqual(d,before)

    def test_current_inquiry_count_blocks_second_sms_despite_unused_customer_capacity(self):
        _,g,state=limits_fixture()
        self.assertEqual(material_handoff.dispatch_guard(g)['status'],'MaterialNotificationEligible')
        state.update(total_count=1,context_counts={'old-thread':0,'thread-one':1});saved_state(g,state)
        self.assertEqual(material_handoff.dispatch_guard(g)['status'],'MaterialNotificationBlocked')

    def test_other_context_count_does_not_consume_this_inquiry_limit(self):
        _,g,state=limits_fixture()
        state.update(total_count=1,context_counts={'old-thread':1,'thread-one':0});saved_state(g,state)
        self.assertEqual(material_handoff.dispatch_guard(g)['status'],'MaterialNotificationEligible')
        state.update(total_count=2,context_counts={'old-thread':2,'thread-one':0});saved_state(g,state)
        self.assertEqual(material_handoff.dispatch_guard(g)['status'],'MaterialNotificationBlocked')

    def test_expiry_pause_unknown_future_due_and_wrong_original_still_block(self):
        _,g,state=limits_fixture()
        for field in ['stop','manual_pause','unknown_attempt']:
            s=state|{field:True};bad=copy.deepcopy(g);saved_state(bad,s)
            self.assertEqual(material_handoff.dispatch_guard(bad)['status'],'MaterialNotificationBlocked')
        for now in ['2026-11-02T02:00:00Z','2026-11-01T23:59:59Z']:
            self.assertEqual(material_handoff.dispatch_guard(g|{'now':now})['status'],'MaterialNotificationBlocked')
        for field,value in [('contact_id','other'),('cycle_id','other')]:
            bad=copy.deepcopy(g);saved_state(bad,state|{field:value})
            with self.assertRaises(ValueError):material_handoff.dispatch_guard(bad)
        with self.assertRaises(ValueError):material_handoff.dispatch_guard(g|{'cycle_page_id':'e'*32})

    def test_only_same_original_reserved_attempt_uses_its_own_counted_slot(self):
        _,g,state=limits_fixture()
        state.update(total_count=1,reserved_count=1,pending_attempt_id='original',
                     pending_context_key='thread-one',context_counts={'thread-one':1})
        saved_state(g,state)
        self.assertEqual(material_handoff.dispatch_guard(g)['status'],'MaterialNotificationBlocked')
        self.assertEqual(material_handoff.dispatch_guard(g|{'attempt_id':'original'})['status'],'MaterialNotificationEligible')

    def test_cross_context_partial_counts_need_recovery_without_reset(self):
        d,_,_=limits_fixture();d['cycles'][0]['total_count']=1
        self.assertEqual(material_handoff.plan(d)['record']['state'],'Blocked')
        d['cycles'][0].update(context_counts_complete=True,context_counts={'old-thread':1,'thread-one':0})
        self.assertEqual(material_handoff.plan(d)['record']['state'],'ReadyForNotification')

    def test_standing_authority_registers_returning_customer_without_init_or_override(self):
        d=inputs();history(d);config=authorized(d)
        config['sms_follow_up']['context_overrides']={};set_settings(d,config)
        before=copy.deepcopy(d);r=material_handoff.plan(d)['record']
        self.assertEqual(r['state'],'ReadyForNotification');self.assertEqual(r['operation'],'create')
        self.assertEqual(r['authorization']['authorization_kind'],'standing-policy')
        self.assertEqual(r['first_due_not_before'],'2026-11-02T00:30:00+00:00')
        self.assertEqual(d,before)

    def test_actual_manual_policy_global_stop_revocation_and_wrong_enquiry_are_preserved(self):
        d=inputs();history(d);c=authorized(d);c['sms_follow_up']['context_overrides']={}
        c['sms_follow_up']['new_cycle_requires_explicit_manual_start']=True;set_settings(d,c)
        self.assertEqual(material_handoff.plan(d)['record']['state'],'Stopped')
        for field,value in [('contact_id','other'),('source_message_id','other'),('phone','+61400000001')]:
            d=inputs();history(d);c=authorized(d);c['sms_follow_up']['context_overrides']={}
            c['enquiries']['thread-one'][field]=value;set_settings(d,c)
            with self.assertRaises(ValueError):material_handoff.plan(d)
        d=inputs();history(d);c=authorized(d);c['sms_follow_up']['context_overrides']={}
        c['sms_stops']['old-thread']['context_key']='*';set_settings(d,c)
        self.assertEqual(material_handoff.plan(d)['record']['state'],'Stopped')
        c['sms_notifications']['enabled']=False;set_settings(d,c)
        with self.assertRaises(ValueError):material_handoff.plan(d)

    def test_missing_number_stays_actionable_data_gap_not_a_consent_error(self):
        d=inputs();history(d);c=authorized(d);c['sms_follow_up']['context_overrides']={}
        d['recipient']=None;c['enquiries']['thread-one']['phone']=None;set_settings(d,c)
        r=material_handoff.plan(d)['record']
        self.assertEqual(r['state'],'Blocked');self.assertIn('Customer SMS number required',r['reasons'])

    def test_sms_freeze_cannot_drop_material_limits(self):
        d=sms_inputs();r=sms_authority.prepare(d)['record']
        self.assertIn('material_limits',r)
        d['saved_task']=sms_saved(d)
        d['saved_task']['text']=d['saved_task']['text'].replace('"maximum_count": 2','"maximum_count": 1')
        with self.assertRaises(ValueError):sms_authority.verify(d)
        d=sms_inputs();del d['material_handoff']
        with self.assertRaises(KeyError):sms_authority.prepare(d)

class ScopedQueue(unittest.TestCase):
    def test_recovery_cannot_change_original_unknown_attempt_or_clear_it_as_waiting(self):
        d=scoped_cycle();u=d['items'][0];k=scan_cycle.key(u)
        d['results']=[{'key':k,'state':'unknown','attempt_id':'original-A','receipt_ref':'capture:timeout'}]
        saved=scan_cycle.advance(d);d['checkpoint_page']=page('f'*32,block(saved['checkpoint']),{})
        for patch in [{'state':'unknown','attempt_id':'new-attempt'}, {'state':'waiting','attempt_id':'original-A'},
                      {'state':'completed','attempt_id':'new-attempt'}]:
            d['results']=[{'key':k,'receipt_ref':'capture:new',**patch}]
            with self.assertRaises(ValueError):scan_cycle.advance(d)

    def test_unrelated_customer_review_and_send_continue_past_unfitting_unknown(self):
        d=scoped_cycle()
        self.assertEqual(scan_cycle.advance(d)['work'][0]['source_key'],'customer-B')
        d['items'][1]['step']='SendNotificationSms'
        self.assertEqual(scan_cycle.advance(d)['work'][0]['source_key'],'customer-B')

    def test_same_customer_changed_version_or_context_still_cannot_bypass_unknown(self):
        for patch in [{'version':'v2'},{'input_digest':'changed'},{'step':'SendApprovedReply'}]:
            d=scoped_cycle();d['items'][1].update(scope=scope('A',context_key='another-project'),**patch)
            self.assertEqual(scan_cycle.advance(d)['work'],[])

    def test_global_stop_and_unscoped_legacy_unknown_remain_conservative(self):
        d=scoped_cycle();d['items'][0].update(step='ObserveStop',unknown_attempt=False,scope={'global':True})
        self.assertEqual(scan_cycle.advance(d)['work'],[])
        d=scoped_cycle();d['items'][0].pop('scope')
        self.assertEqual(scan_cycle.advance(d)['work'][0]['source_key'],'customer-B')
        d['items'][1]['source_key']='customer-A'
        self.assertEqual(scan_cycle.advance(d)['work'],[])

    def test_stop_is_scoped_but_must_be_saved_before_same_customer_sends(self):
        d=scoped_cycle();d['items'][0].update(step='ObserveStop',unknown_attempt=False)
        self.assertEqual(scan_cycle.advance(d)['work'][0]['source_key'],'customer-B')
        d['items'][1]['scope']=scope('A')
        self.assertEqual(scan_cycle.advance(d)['work'],[])

    def test_unknown_scope_and_unchanged_recovery_are_retained_across_ticks(self):
        d=scoped_cycle();unknown=d['items'][0];k=scan_cycle.key(unknown)
        d['results']=[{'key':k,'state':'unknown','attempt_id':'original-A','receipt_ref':'capture:original-timeout'}]
        first=scan_cycle.advance(d)
        self.assertEqual(first['work'][0]['source_key'],'customer-B')
        d['checkpoint_page']=page('f'*32,block(first['checkpoint']),{});d.pop('results');d['items']=[]
        self.assertEqual(scan_cycle.advance(d)['work'][0]['source_key'],'customer-B')
        d['items']=[unknown|{'recovery_wakeup':{'evidence_ref':'capture:operator-input','revision':'r1'}}]
        d['now']='2026-11-01T00:01:00Z'
        fresh=scan_cycle.advance(d);self.assertEqual(fresh['work'][0]['action'],'reconcile')
        d['results']=[{'key':k,'state':'unknown','attempt_id':'original-A','receipt_ref':'capture:still-unknown'}]
        waiting=scan_cycle.advance(d)
        d['checkpoint_page']=page('f'*32,block(waiting['checkpoint']),{});d.pop('results')
        again=scan_cycle.advance(d)
        self.assertTrue(all(v['action']!='reconcile' for v in again['work']))
        self.assertEqual(again['checkpoint']['items'][k]['attempt_id'],'original-A')
        self.assertEqual(again['checkpoint']['work_items'][0]['scope'],scope('A'))

    def test_saved_scope_cannot_be_removed_or_moved_to_another_customer(self):
        d=scoped_cycle();first=scan_cycle.advance(d)
        d['checkpoint_page']=page('f'*32,block(first['checkpoint']),{})
        for change in [None,scope('B')]:
            bad=copy.deepcopy(d)
            if change is None:bad['items'][0].pop('scope')
            else:bad['items'][0]['scope']=change
            with self.assertRaises(ValueError):scan_cycle.advance(bad)

    def test_recovery_timer_runs_once_and_is_not_a_tick_wide_retry(self):
        d=scoped_cycle();d['now']='2026-11-01T00:01:00Z';u=d['items'][0];k=scan_cycle.key(u)
        u['recovery_due_at']='2026-11-01T00:00:30Z'
        r=scan_cycle.advance(d);self.assertEqual(r['work'][0]['action'],'reconcile')
        d['results']=[{'key':k,'state':'unknown','attempt_id':'original-A','receipt_ref':'capture:result'}]
        r=scan_cycle.advance(d);d.pop('results')
        d['checkpoint_page']=page('f'*32,block(r['checkpoint']),{})
        self.assertTrue(all(v['action']!='reconcile' for v in scan_cycle.advance(d)['work']))

class DispatchRecheck(unittest.TestCase):
    def test_material_expiry_is_rechecked_at_final_release(self):
        d=dispatch('sms');sms=d['notification'];mat=sms['material_handoff']['input']
        cfg=authorized(mat);mat['observed_at']='2026-11-01T00:00:01Z'
        cfg['sms_follow_up']['context_overrides']['thread-one']['expires_at']='2026-11-01T00:01:05Z'
        set_settings(mat,cfg)
        from test_material_handoff import saved as material_saved
        sms['material_handoff']['saved_email_task']=material_saved(mat,'email')
        sms['material_handoff']['saved_email_task']['id']=mat['email_task_id']
        sms['material_handoff']['saved_cycle']=material_saved(mat)
        sms['saved_task']=sms_saved(sms)
        d['material_current']=current_material(sms)
        d=ready(d)
        with self.assertRaisesRegex(ValueError,'expired'):dispatch_admission.release(d)

    def test_actual_sending_rules_do_not_require_inbound_or_delivery_trials(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]/'plugins/eightdegrees-sales-workflow'
        skill=(root/'skills/eightdegrees-sms-follow-up/SKILL.md').read_text()
        self.assertNotIn('Unverified gateway or missing inbound coverage produces',skill)
        rules=(root/'references/sms-rules.md').read_text()
        self.assertNotIn('- Verify actual own-number display, stable gateway',rules)
        settings=json.loads((root/'references/pilot-defaults.json').read_text())
        self.assertFalse(settings['sms_follow_up']['new_cycle_requires_explicit_manual_start'])

    def test_changed_current_cycle_caps_or_unknown_after_admission_return_no_call(self):
        for patch in [{'total_count':2},{'unknown_attempt':True},{'stop':True}]:
            d=ready(dispatch('sms'));current=d['current_material_current']
            from email_presentation import blocks
            state=blocks(current['saved_cycle'],'sms-cycle-current-state')[1]
            state.update(patch)
            capture=copy.deepcopy(current['saved_cycle'])
            capture['text']=capture['text'].replace(blocks(capture,'sms-cycle-current-state')[0],block(state))
            current['saved_cycle']=capture
            with self.assertRaises(ValueError):dispatch_admission.release(d)

    def test_no_sms_reply_reader_is_not_a_send_or_material_guard_requirement(self):
        from sms_channel import gate
        self.assertEqual(gate({'channel_verified':True,'inbound_reader_available':False,
            'invocation_policy':'one-cycle-approved-work',
            'guards':{'stop':False,'manual_pause':False,'unknown_attempt':False,'customer_replied':False}})['status'],'ChannelCheckEligible')
        self.assertEqual(material_handoff.dispatch_guard(limits_fixture()[1])['status'],'MaterialNotificationEligible')

if __name__=='__main__':
    unittest.main()
