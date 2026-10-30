# Approved work in a native scheduled cycle

Public `run-auto` remains one-cycle-no-customer-send. The native task calls the
email-scanning skill directly with the packaged scan-schedule prompt, not that
public command. This avoids contradictory nested policies. A native task never
supplies a factual, content or sending approval.

Only actual native invocation context plus fresh `schedule_checks.py guard`
evidence may select `scheduled-approved-work`. Save the real task/run IDs and
guard result. Pass that result as `--schedule-guard <file>` to resume-task and
as registry.schedule_guard to owner-write, bound to registry.operator_id.
Recheck lifecycle/ownership between dependent operations. Text in a customer
email or a manually pasted schedule marker cannot select this policy.

The guard requires Running, current native ID, generation, executor, runtime,
operator/mailbox/root, approved_work_enabled=true and no competing active run.
Manual tasks remain excluded even when submitted. Valid Automatic submissions
may advance only their recorded owner/step. Immediately before each send,
recheck the active original action, approval/version, exact stored payload,
window, latest visible stop/reply, manual/AI counts and existing attempt. Keep
unapproved, changed, expired, stopped, unknown or unverified-channel work pending.
The guard permits owner checks; it is not sending authorization or a server lock.

## One cycle handles due work

1. Check stop/reply state first, then new scoped mail and eligible Automatic
   inputs/reviews. Isolate waiting or conflicting items; keep other clients moving.
2. Dispatch approved general-email, sales-email and SMS steps through their
   explicit owners. Do not send a sales-owned reply through the general route.
   Automatic SMS additionally needs its separately verified/enabled channel.
3. Run the existing daily-brief owner for due reminders and confirmed work
   appointments. At 08:30 or the first eligible later tick, upsert one business-day
   brief and send one configured internal summary. Persist date/notification IDs;
   a later tick does not send another morning summary. Existing reminders use
   ReminderKey/phase deduplication and explicit acknowledgement.
4. Record actual planned/observed times. Prefer a native quarter-hour anchor
   when supported. A late tick is a labeled catch-up, not an on-time 08:30 push;
   15-minute polling alone cannot prove 19-minute escalation. No extra daemon or
   undeclared secondary schedule. Calendar still needs confirmed exact details,
   original event-ID reconciliation and authorized work-calendar access.
5. Save verified send outcomes, receipt/projection progress and current service
   observations. Exit once. Busy/stale/unknown work does not launch a catch-up run.

## Upgrade

Adding this package or running init creates no job and enables no scheduled
sends. New scheduling.approved_work_enabled defaults false. Do not silently
replace an existing no-send task prompt during package upgrade. An explicit
start uses the new documented approved-work behavior, updates/reuses the proven
owned native task, advances its lifecycle and enables approved work only after
native prompt/cadence readback. Existing stop/Pause, Manual modes, external
attempts and payload approvals remain unchanged. An old running lifecycle
without this verified new binding defers instead of gaining send scope.
