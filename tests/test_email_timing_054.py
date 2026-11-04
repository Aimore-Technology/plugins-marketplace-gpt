"""Approved mail executes at any hour; historical windows never hold its queue."""
import copy
import json
import unittest

from test_consent_review_053 import prepared, dispatch_input, captures
from test_email_flow_049 import send_input as legacy_send
from test_event_probe import fixture, changed, saved, work
from test_unattended import cycle_fixture
import email_flow
import consent_review
import email_timing
import event_probe
import queue_construction
import scan_cycle


class AnytimeEmailTests(unittest.TestCase):
    def test_new_package_and_visible_narrative_have_no_sending_window(self):
        p=prepared()['package']
        self.assertNotIn('window',p)
        self.assertEqual(p['timing_policy'],email_timing.POLICY)
        self.assertNotIn('Window:',consent_review.narrative(p))

    def test_night_weekend_holiday_and_false_date_flag_do_not_defer_email(self):
        for at in ('2026-11-04T23:50:00+10:30','2026-11-08T03:00:00+10:30','2026-12-25T02:00:00+10:30'):
            d=dispatch_input();d['now']=at
            d['controls'].update(date_allowed=False,window_eligible=False)
            self.assertTrue(email_flow.dispatch(d)['send_allowed'],at)

    def test_original_legacy_approval_with_expired_or_future_window_sends_same_draft(self):
        for at in ('2026-11-04T02:00:00+10:30','2026-11-08T23:00:00+10:30'):
            d=legacy_send();d['now']=at;d['controls']['date_allowed']=False
            before=copy.deepcopy(d)
            r=email_flow.dispatch(d)
            self.assertTrue(r['send_allowed']);self.assertEqual(r['call']['args'],{'draft_id':'r-draft-1'})
            self.assertEqual(d,before)

    def test_old_future_email_timer_becomes_ready_without_new_mail_or_changed_feed(self):
        d=changed(fixture(),events=[work(kind='timer',step='SendApprovedReply',due_at='2026-12-01T00:00:00Z')])
        first=event_probe.probe(d)
        self.assertEqual(first['status'],'ScanWorkReady')
        self.assertNotIn('due_at',first['ready'][0])
        # Simulate an actual old saved timer, preserving its original event key.
        original=copy.deepcopy(first)
        pending=next(iter(original['candidate_index']['pending'].values()))
        pending.update(kind='timer',due_at=pending.pop('legacy_email_due_at'))
        d['index_page']=saved(original)
        r=event_probe.probe(d)
        self.assertEqual(r['status'],'ScanWorkReady');self.assertTrue(r['persist_required'])
        self.assertEqual(set(r['candidate_index']['pending']),set(original['candidate_index']['pending']))

    def test_approved_email_row_is_recovery_demand_despite_old_next_due(self):
        row={'url':'https://app.notion.com/p/'+'c'*32,'SourceKey':'mail:original',
             'Mode':'Automatic','State':'WaitingForOperator','Consent':'__YES__',
             'OwnerSkill':'eightdegrees-sales-reply','ResumeStep':'SendApprovedReply',
             'ContentVersion':'reply-v1','date:NextDue:start':'2026-12-01T00:00:00Z'}
        r=queue_construction.ready_task_records([row])
        self.assertEqual(len(r),1);self.assertNotIn('due_at',r[0]['events'][0])
        row['Consent']='__NO__'
        self.assertEqual(queue_construction.ready_task_records([row]),[])
        row.update(Consent='__YES__',State='Completed')
        self.assertEqual(queue_construction.ready_task_records([row]),[])

    def test_cycle_does_not_leave_approved_email_in_future_due_bucket(self):
        d=cycle_fixture();d['items'][0]['due_at']='2026-12-01T00:00:00Z'
        r=scan_cycle.advance(d)
        self.assertTrue(any(v['step']=='SendApprovedReply' for v in r['work']))

    def test_sms_quiet_hours_and_provider_backoff_are_preserved(self):
        for step,extra in [('SendNotificationSms',{}),('SendApprovedReply',{'provider_retry_after':'later'})]:
            item={'step':step,'due_at':'2026-12-01T00:00:00Z',**extra}
            self.assertEqual(email_timing.release(item),item)

    def test_stops_unchecked_consent_and_unknown_attempts_remain_blocked_at_night(self):
        for field in ('scan_enabled','channel_enabled','no_reply_or_stop','attempt_clear','approval_current'):
            d=dispatch_input();d['now']='2026-11-08T03:00:00+10:30';d['controls'][field]=False
            self.assertFalse(email_flow.dispatch(d)['send_allowed'])
        d=dispatch_input();d['attempt_status']='Unknown'
        self.assertFalse(email_flow.dispatch(d)['send_allowed'])

    def test_provider_backoff_survives_checkpoint_and_restart(self):
        d=cycle_fixture();d['items'][0].update(due_at='2026-12-01T00:00:00Z',
                                              provider_retry_after='2026-12-01T00:00:00Z')
        first=scan_cycle.advance(d)
        self.assertEqual(first['work'],[])
        self.assertEqual(first['checkpoint']['work_items'][0]['provider_retry_after'],
                         '2026-12-01T00:00:00Z')
        d.update(checkpoint_page={'id':d['root_id'],'metadata':{'type':'page'},
                 'text':'<content>\n```json\n'+json.dumps(first['checkpoint'])+'\n```\n</content>'},items=[])
        self.assertEqual(scan_cycle.advance(d)['work'],[])
