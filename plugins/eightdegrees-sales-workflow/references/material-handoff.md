# Verified material email to observable SMS work

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

The email owner must register follow-up after an successful material-email handoff.
It is a required downstream transition, not a suggestion to the operator to
invoke another skill. Email approval remains separate; factual SMS uses standing notification authority. No per-email native
task is created: one executor installed by start handles all due Automatic work.
Without a running schedule, public run-auto processes the same queue once.

## Registration before email-owner completion

1. Use the successful original Gmail dispatch response/account and our verified
   approved payload/material source version. An unsent draft or unknown handoff
   cannot enroll. An explicitly verified nonmaterial reply saves NotApplicable on the original email task with no SMS cycle; do not classify it as material merely to satisfy completion. Retain the actual Sent result before downstream work.
2. Read existing cycles through complete scoped discovery for this root and
   exact CRM location/contact, including closed cycles and pending handoff
   attempts. Match actual provider-event identity, related inquiry/context and
   any active customer cycle. Preserve its page, manual+AI count, due times,
   approvals, Pause/stop and attempts. A resend never resets a cycle. Ambiguous
   discovery or an unknown attempt pauses registration; never assume absence.
3. Run `material_handoff.py plan --input <original-normalized-evidence.json>`.
   Required input: root_id, email_task_id, content_version, event (original status=ProviderAccepted or Sent, material=true,
   provider/account/message_id/location_id/contact_id/context_key/sent_at),
   cycle_query_complete, cycles, stop, manual_pause, recipient (E.164 or null),
   channel_verified and automatic_sms_enabled. Each discovered cycle includes
   its actual page_id/cycle_key/location_id/contact_id/context_key/material_events,
   active, total_count and unknown_attempt=false; include actual stop/manual_pause,
   maximum_count and state when recorded. Supply real observations,
   not fabricated verification flags. Preserve the input for same-phase readback.
   For an explicitly initiated new context, also supply saved_settings (the
   actual RunSettings fetch), observed_at and event.source_message_id (the
   original incoming inquiry, distinct from the outgoing Gmail message_id).
   Use the saved authorization contract below; a loose authorized=true is not evidence.
4. Under the SMS owner's separate affected-role plan, create/reuse its cycle
   record in the customer's existing Communications area and one Automatic ScheduledWork
   PendingTasks item. Persist the returned compact material-handoff-v1 JSON
   audit block both on the original email task and the distinct original cycle
   page, with native links between them. Use exact-call preflight and saved-page
   checks. Registration cannot send, create native tasks or enable automatic SMS.
   Keep exactly one current block per event; preserve older snapshots in original history/logs or a history wrapper, not another top-level material-handoff-v1 JSON record for the same event.
5. Ready channel: prepare and freeze the first notification now, with due lower bound
   email acceptance+30 minutes by default, or the exact delay from the saved
   explicit context authorization. Persist its maximum_count, second_sms_allowed
   and expiry on the cycle/task; never widen a one-message exception to two.
   The SMS owner applies the configured business
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
   A distinct recovery also supplies saved_recovery_task, targeting its own
   completion as specified in [record contracts](record-contracts.md), without
   retargeting the original event. Include both saved projection pages.
   Freeze this as kind=material-handoff on the original email task in the sales
   send plan, alongside verified draft/provider-handoff and CRM receipt checks. A blocked
   but verified handoff is valid registration, never successful SMS delivery.

## Saved new-context initiation and scope

Read the original registered RunSettings page, not a copied boolean. Its
customer_setup binds notion_root_id, notion_ids.settings, gmail_account,
crm_location_id and operator_id. The existing sms_notifications standing policy
must remain enabled, unrevoked and bound to that root/operator. Explicit initiation
is stored at sms_follow_up.context_overrides[context_key]: explicitly_initiated=true,
source_message_id, recipient, authorization_ref (the original user request/run
page), and optional context_key/revoked_at/starts_at/expires_at. Its first_delay_minutes
defaults to the saved 30-minute rule; max_messages_per_cycle_including_manual is
one or two, with coherent second_sms_allowed. Save enquiries[context_key] with
location_id/contact_id/source_message_id/phone so authorization cannot migrate
to another customer, inquiry or number. Initialization records a user's explicit
new-context request once; a subsequent run-auto reads it without another approval.
Missing scope data uses the existing DataCompletion route, never guessed consent.

The helper checks these actual saved bindings, current observation time and
expiry/revocation. It emits the frozen authorization reference/digest and limits
with a new or recovered registration. It does not create authorization, change
settings, dispatch SMS or waive the normal business window. A deliberate saved
zero-delay exception is honored only within its own recorded scope/expiry.

Keep all cycles in complete discovery. A closed cycle from another project is
history, not a global stop: it may coexist with a separately authorized new cycle.
An active customer cycle is reused; no second active cycle is created. Existing
same-event/same-context cycles retain their identity, count, due time and limits,
including a one-message cap. A stop on the current context, wildcard/global SMS
stop, CRM DND, Pause, revoked authority or unknown attempt still prevents sending.
Compute the stop input for the applicable scope; never OR every historical
project stop into a customer-global prohibition. Use the current restrictive
persona overlay via contact.dispatch-gate as well as fresh CRM/queue guards.
Authorization to start another context never reopens an old stopped/capped cycle.

The local helper validates normalized input and saved Notion evidence only.
Original response binding, fresh stop checks, full cycle discovery and actual tool
order remain the owners' duties. It grants no approval or exactly-once guarantee.

## Partial success and recovery

If email Sent but registration fails, display "Email sent; SMS handoff pending"
with the provider result and one ExecutionExceptions/RecordMaterialHandoff task
on the original sales owner. Keep the send result, prior attempts and original
run; do not mark overall completion or ask the operator to re-send the email.
If Notion cannot save the recovery task, retain durable local evidence under
the existing recovery contract and report the partial result honestly.

The next authorized cycle uses the saved original acknowledgement and existing cycle/key
before completing only this handoff. It calls the registration-only SMS phase,
not SendApprovedReply or a fresh intake. Receipt backfill and handoff recovery
are independent; either may succeed while the other waits. No helper may
reenter the scanner or widen report/draft-only/no-send restrictions.

For the 0.1.33 ClosedPriorContextBlocksExplicitNewContext defect, retain the
original zero-attempt stub. Include its actual state in the normalized cycle
discovery and supply recovery_cycle_page as the original page fetch alongside
saved_settings. material.plan permits in-place reuse only when its one current
sms-cycle-current-state is BlockedImplementation with that exact blocked_reason,
active/stop/manual_pause=false, total_count/reserved_slots=0, and no prior
attempt/outcome/request. The original material-handoff-v1 must bind the same
root/email/provider message/context/customer/event/cycle and current source
authorization. A genuine stop, cap, unknown/reserved slot or different original
never qualifies. Keep old failure history and patch only the current registration;
preserve page/key, email handoff and CRM receipt. Verify the updated email/cycle
readbacks before clearing the blocker. Then the ordinary shared queue handles
the due notification; no new email, duplicate receipt, SMS approval or user
continue command. This recovery also requires current unexpired authorization;
do not silently extend an expired one-off window.

Explicit init upgrade registers this known implementation repair as one stable
recovery-feed revision (scoped-sms-initiation-v2) for the existing SMS task's
PrepareSmsFollowUp step/version. A ready recovery event wakes public run-auto;
do not require the user to edit a read-only blocker or submit another approval.
After actual owner completion, acknowledge it with the saved result and next
notification wake-up. Unchanged ticks do not rediscover/re-run the same repair,
and the repair cannot turn stopped/expired/unknown work into eligible work.

## Public acceptance

Use only published plugin commands, ordinary inquiry inputs and actual Notion
human submissions. Do not call private owners or add invented continue syntax
to make a missing transition pass. Verify email Sent -> automatic notification
or actionable blocked setup -> standing-authorized due execution -> successful service acceptance;
repeat unchanged cycles to prove no duplicate cycle/task/send. Also verify
unknown email result, missing number, disabled gateway, stopped/closed cycle,
same-event retry, resends, partial handoff save and already-sent recovery.
