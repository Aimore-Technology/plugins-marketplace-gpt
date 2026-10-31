# Verified material email to observable SMS work

The email owner must register follow-up after an actual material Sent result.
It is a required downstream transition, not a suggestion to the operator to
invoke another skill. Email approval remains separate; factual SMS uses standing notification authority. No per-email native
task is created: one executor installed by start handles all due Automatic work.
Without a running schedule, public run-auto processes the same queue once.

## Registration before email-owner completion

1. Verify the actual Sent message/account, exact approved payload and material
   source/version under stored-reply transport. A draft, send request or unknown
   result cannot enroll. An explicitly verified nonmaterial reply saves NotApplicable on the original email task with no SMS cycle; do not classify it as material merely to satisfy completion. Retain the actual Sent result before downstream work.
2. Read existing cycles through complete scoped discovery for this root and
   exact CRM location/contact, including closed cycles and pending handoff
   attempts. Match actual provider-event identity, related inquiry/context and
   any active customer cycle. Preserve its page, manual+AI count, due times,
   approvals, Pause/stop and attempts. A resend never resets a cycle. Ambiguous
   discovery or an unknown attempt pauses registration; never assume absence.
3. Run `material_handoff.py plan --input <original-normalized-evidence.json>`.
   Required input: root_id, email_task_id, content_version, event (actual status=Sent, material=true,
   provider/account/message_id/location_id/contact_id/context_key/sent_at),
   cycle_query_complete, cycles, stop, manual_pause, recipient (E.164 or null),
   channel_verified and automatic_sms_enabled. Each discovered cycle includes
   its actual page_id/cycle_key/location_id/contact_id/context_key/material_events,
   active, total_count and unknown_attempt=false. Supply real observations,
   not fabricated verification flags. Preserve the input for same-phase readback.
4. Under the SMS owner's separate affected-role plan, create/reuse its cycle
   record in the customer's existing Communications area and one Automatic ScheduledWork
   PendingTasks item. Persist the returned compact material-handoff-v1 JSON
   audit block both on the original email task and the distinct original cycle
   page, with native links between them. Use exact-call preflight and saved-page
   checks. Registration cannot send, create native tasks or enable automatic SMS.
   Keep exactly one current block per event; preserve older snapshots in original history/logs or a history wrapper, not another top-level material-handoff-v1 JSON record for the same event.
5. Ready channel: prepare and freeze the first notification now, with due lower bound
   actual email Sent+30 minutes. The SMS owner applies the configured business
   window/date/holiday rules to calculate the eligible time; the helper's UTC
   lower bound is not permission to send. No per-message SMS review is required; use the current standing policy and fresh dispatch checks. Missing number -> DataCompletion/PrepareSmsFollowUp; unverified
   or disabled channel -> one actionable readiness task with original settings
   link and clear reason; no guessed number or automatic enable. A stop/closed
   or capped cycle -> explicit Stopped/no-new-follow-up result, no new notification.
6. For reuse, append this material event association without changing existing
   count/due/approved payload or reopening a closed cycle. The planned first_due
   is this event's audit lower bound, not a replacement cycle timer. A different
   material context with an active cycle does not create a second active cycle.
7. Fetch the saved email task and cycle. Run `material_handoff.py verify` with
   input=<frozen plan input>, saved_email_task and saved_cycle as their actual
   original Notion fetches (saved_cycle is omitted only for explicit nonmaterial NotApplicable). It checks exact persisted blocks, original email
   target and same cycle page for reuse. Require exit 0/MaterialHandoffVerified;
   ordinary owner publication checks additionally cover the task/action/binding.
   Freeze this as kind=material-handoff on the original email task in the sales
   send plan, alongside draft/sent transport and CRM receipt checks. A blocked
   but verified handoff is valid registration, never successful SMS delivery.

The local helper validates normalized input and saved Notion evidence only.
Provider verification, fresh stop checks, full cycle discovery and actual tool
order remain the owners' duties. It grants no approval or exactly-once guarantee.

## Partial success and recovery

If email Sent but registration fails, display "Email sent; SMS handoff pending"
with the provider result and one ExecutionExceptions/RecordMaterialHandoff task
on the original sales owner. Keep the send result, prior attempts and original
run; do not mark overall completion or ask the operator to re-send the email.
If Notion cannot save the recovery task, retain durable local evidence under
the existing recovery contract and report the partial result honestly.

The next authorized cycle checks actual sent evidence and existing cycle/key
before completing only this handoff. It calls the registration-only SMS phase,
not SendApprovedReply or a fresh intake. Receipt backfill and handoff recovery
are independent; either may succeed while the other waits. No helper may
reenter the scanner or widen report/draft-only/no-send restrictions.

## Public acceptance

Use only published plugin commands, ordinary inquiry inputs and actual Notion
human submissions. Do not call private owners or add invented continue syntax
to make a missing transition pass. Verify email Sent -> automatic cycle/draft
or blocked task -> distinct SMS approval -> due execution -> actual status;
repeat unchanged cycles to prove no duplicate cycle/task/send. Also verify
unknown email result, missing number, disabled gateway, stopped/closed cycle,
same-event retry, resends, partial handoff save and already-sent recovery.
