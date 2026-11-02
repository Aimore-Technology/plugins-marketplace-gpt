# Standing authority for factual SMS notifications

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

P0 SMS is a notification channel. Initialization defaults sms_notifications to
enabled notification-sms-v1, per_message_review_required=false and automatic
follow-up permission enabled. State this in setup and save the actual root,
operator, own sending number/device and recipient scope. Do not add an extra
permission question for each notification. Existing recorded explicit disable,
revocation, customer opt-out or operator Pause still applies.

This authority covers material receipt, a light follow-up notice, a confirmed
appointment reminder and an internal operator alert. It does not authorize
quotation dispatch, offers, advice, commitments, payment/signing or fabricated
facts. Email sending and CRM facts/Notes/persona review are unchanged.

Permission and capability are separate. Check the authenticated actual device,
own-number display, stable send, ordinary-inbox reply visibility and available
reply/stop coverage. A gateway limitation is a capability task, not a request to
approve the same SMS. Trusted AndroidSync uses its actual request route; genuine
native phone/Web restrictions cannot be bypassed or described as completed.

## Prepare, freeze and send

1. Generate/edit concise notification copy from actual material/send/appointment
   or reminder evidence and saved style. Verify recipient and purpose. A material
   notification can say the email is in the inbox only after actual Sent; it must
   not claim the customer read it. No per-message ContentReview or SendApproval.
2. Create/reuse one canonical ScheduledWork task with OwnerSkill SMS,
   ResumeStep=SendNotificationSms and Mode=Automatic. Its ordinary result page is
   read-only workflow copy, not a form; show queued/due/status and original links.
   Keep it out of the five human issue views. Missing data uses DataCompletion;
   actual error/unknown authority/capability uses ExecutionExceptions. Do not
   create an approval task merely because permission is standing rather than
   message-specific. Preserve old approval pages as historical evidence.
3. Run sms_authority.py prepare with current authority and payload. Authority
   contains policy, enabled, per_message_review_required, allowed_intents,
   actual root_id/operator_id/sender_number/device_id/operator_sms_number.
   Payload contains those root/operator bindings plus task_id/content_version,
   intent, recipient_role (customer/operator), recipient/sender_number/device_id,
   body, source_refs and facts_verified from actual source checking. Supply the
   real invocation_policy; report/draft/setup/explicit-no-send cannot dispatch.
4. Persist the exact returned sms-notification-v1 JSON in the original task,
   preserving source/version and current due/window. Fetch that actual saved
   task and run verify with the same current authority/payload, saved_task and
   dispatch={recipient,device_id,body} containing the exact proposed provider
   arguments' corresponding fields. Require exit 0/SMSNotificationVerified.
   Freeze kind=sms-authority on the original task in the owner plan. The helper
   checks binding/bytes, not semantic truth, gateway readiness or current time.
5. Immediately before dispatch reread current authority/revocation, customer
   stop/Pause and relevant replies, window/date/due, manual+AI count, current
   device/target/text and prior attempt. Save AttemptId first. A changed text
   needs a new frozen version/check, without human approval. A pending/unknown
   old attempt blocks text mutation and retry until reconciliation.
6. Record actual request ID/result, the SHA-256 of the actual submitted body,
   from the original successful response, without a status readback. Supply that actual digest as provider.payload_sha256 to
   outcome_checks. SendNotificationSms completion requires sms-authority plus
   current outcome evidence for that same task/version and matching body digest.
   Successful service acceptance completes this dispatch, including AwaitingPhone/PendingApproval. Delivered and handset observations are optional metadata, never required confirmation or further polling. Repair log/projection
   failures without resending. The read-only result page can serve the existing
   action-result projection contract; it contains no approval controls.

## Timing and stopping

Standing notification authority includes the configured SMS weekday/hour and
no-send-date policy; it does not require a separate holiday-date approval per
SMS. Use configured exclusions, disclose an unverified holiday list and keep
the actual calendar source/cutoff visible. Email holiday/date approval rules
remain unchanged. A task-specific explicit expiry/Pause is preserved; do not
catch up an expired legacy one-off authorization automatically.

First material follow-up is no earlier than Gmail acceptance+30 minutes; second is no earlier
than first accepted notification request+24 hours. Count manual+AI related messages together
up to two per cycle. Unknown reserves a slot. Customer reply/stop, authority
revocation, cap and manual Pause prevent further sends. Internal operator alerts
are separately deduplicated by ReminderKey+phase and only use the configured
operator destination. Notification authority does not authorize a customer reply
to a campaign or substitute a service sender ID.

## Upgrade

Explicit init adopts the new default standing policy, adds ScheduledWork to the
existing Category select and preserves original database IDs and the five human
views. Add complete discovery of ScheduledWork for the queue; do not derive
execution coverage from Today display views. Do not overwrite a recorded user
disable/revocation or reopen stopped/unknown/expired work. Missing live policy
binding stays a single configuration/capability task, never repeated message
approval. Old SendApprovedSms results remain historical; migrate only eligible
unsent factual notifications with verified intent, payload and current standing
authority, keeping IDs/mode/history and no invented old approval. The verified new notification route may execute with preserved Manual provenance under standing authority; it does not require a human submission.

New dispatches use provider-handoff-v1. Configure the authorized connector/device
without a test delivery. Original successful AndroidSync acceptance finalizes
the used request count and our task, including AwaitingPhone/PendingApproval.
No provider-status, receiving-phone, own-number display or stability probe is
required for completion. Inbound capability is recorded separately; its absence
is not a delivery-check gate for one-way factual notifications. Keep actual
observable customer stop/reply and all authority/window/count checks.

Use [prospective action gates](pre-action-order.md) before opening new email
review controls or emitting outgoing call arguments. A post-action check cannot
repair missing historical order. Run these only on the affected event phase.
