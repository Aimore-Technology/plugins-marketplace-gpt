---
name: eightdegrees-sms-follow-up
description: "Prepare and execute approved, bounded SMS follow-ups after verified material delivery; stop on replies and reconcile manual sends, channel limitations and unknown results."
---

# Follow up after materials

Apply [provider handoff completion](../../references/provider-boundary.md): successful Gmail/AndroidSync acceptance finishes dispatch. Verify our request/approval and own records; CRM writes retain readback. Do not re-query external send status or verify delivery.

Before dependent writes, use [execution preflight](../../references/execution-preflight.md) to generate, persist and read back this owner's affected-role plan; a failed preparation stops the phase. Apply the [owner completion contract](../../references/owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action. Before EVERY Notion page write, including the first create and progress/result properties, run [exact-call preflight](../../references/notion-mutation.md); only use its returned unchanged arguments after exit 0 and NotionMutationPrepared.

Before dispatch read [connector experience](../../Experience/connector-contracts.md), [SMS rules](../../references/sms-rules.md), [notification authority](../../references/sms-notifications.md) and [operating-contract](../../references/operating-contract.md). Discover the actual request tool and configured device; record inbound-reader availability separately and current device policy. AndroidSync request_sms uses its genuine Trusted route when configured; do not introduce a forced-native-approval draft as a default. Genuine phone/Web restrictions remain a connector capability, not something this Skill can bypass.

1. On verified material email Sent, perform [handoff registration](../../references/material-handoff.md) immediately: one original customer cycle, actual material/source/version/time, current due information and an Automatic ScheduledWork notification task or an explicit blocked/stopped result. A draft/approval/unknown email does not start a cycle. Reuse provider-event identity, original cycle and manual+AI counts; a resend never resets them. No per-email native task and no operator continue command.
2. Verify the actual own sending number/device, customer number, current factual source and reply/stop/Pause state. Default notification authority is enabled at init, while capability readiness is separately observed. A configured explicit disable/revocation still blocks. Unverified gateway or missing inbound coverage produces a capability task, not per-message approval. Never substitute another service sender.
3. Calculate first due >= actual material send+30 minutes, second due >= first actual follow-up+24 hours, using configured customer weekdays/hours and no-send dates. Internal operator alerts use their own configured reminder timing. Apply the standing SMS calendar policy; do not ask for a human holiday/date approval on every SMS. Unknown holiday coverage is reported honestly. Preserve explicit old one-off expiry/Pause and prior attempts; do not silently catch up a revoked/expired legacy exception.
4. Generate/edit concise factual notification copy using verified source and saved style. The allowed purposes are material receipt, follow-up notice, confirmed appointment reminder and internal operator alert. No marketing offer, quotation, advice, commitment, signing/payment or fabricated appointment under notification authority. No ContentReview or SendApproval for individual notifications. Freeze the exact body/recipient/device/version and source references in the original ScheduledWork task with a read-only current result page; no human submission controls.
5. Use sms_authority.py prepare/verify under [notification authority](../../references/sms-notifications.md), with the current saved policy and actual original task fetch. Freeze sms-authority evidence in this owner's plan. Immediately before sending re-read current policy, target/device/body, time/date, latest reply/stop/Pause, single ownership, prior attempts and manual+AI count. Persist AttemptId before the actual request. A changed body needs a new frozen version/check, not human review; an unknown/pending old attempt blocks mutation/resending.
6. Record actual provider result and payload digest, publish channel-local results from the original successful dispatch response. New SendNotificationSms completion requires both the current standing-policy/payload check and the matching original provider request digest. AndroidSync acceptance completes our dispatch, including AwaitingPhone/PendingApproval; close after our saved-result checks without status polling. Do not ask for receipt confirmation. Missing log/publication saving repairs only that step; it never repeats the provider request.
7. On observed reply/rejection/complaint, stop unsent affected work first; record opt-out and hand off the communication for normal fact review. Unconnected WeChat/WhatsApp/Telegram/phone replies require the operator's Notion stop/Pause; do not claim cross-channel real-time coverage. Revoking standing authority prevents future dispatch but cannot retract an already accepted provider request.
8. Stop after TWO related follow-ups total from the operator and AI. Unknown results reserve a slot and block later sends until reconciled. One active cycle/customer; closed/capped/stopped cycles do not automatically reopen. A new unrelated cycle still needs the configured explicit new-context initiation, without reviving old stopped work. Return actual counts, result/next due/stop reason and original links; run-auto or the shared native queue handles successors without separate continue commands.

## Current outcome and operator path

Apply [outcome state](../../references/outcome-state.md), [operator experience](../../references/operator-experience.md) and [local batches](../../references/local-check-batch.md). Read-only notification pages show Queued, due time, actual provider status or blocking reason. Do not show approval buttons or tell the operator to re-authorize each SMS. Manual probe history and old review pages remain historical; never release abandoned native drafts or invent cleanup APIs. Package checks do not prove actual own-number, reply-reader or delivery capability.

## Reconcile original status, not only a new run

Use [unattended operation](../../references/unattended-operation.md), sms.presentation-plan/verify and RefreshSmsOutcome only for a known stale internal result, using the original response as provider_status; do not query AndroidSync. Refresh all seven original task/action/run/cycle surfaces; machine waiting is not WaitingForOperator. Preserve exact attempt/payload, receipt history, counts and stopped state. Before dispatch also check the current source-bound contact restriction overlay; historical approved permission cannot override it.

## Actionable capability and bounded diagnostic

Apply [SMS channel setup](../../references/sms-channel-setup.md) rather than
leaving a blocked notification with only a read-only reason. Reuse one separate
DataCompletion/PrepareSmsFollowUp input for setup. An already authorized
one-message diagnostic is processed by run-auto without another SMS approval.
Use local sms.channel-check with actual policy, guards, payload, context/time
and saved controlled_sms_test. ChannelCheckBlocked means no dispatch even when
the local check itself exits cleanly. ChannelCheckEligible never supplies
standing authority, material/due/window/attempt proof or ordinary readiness.
Reserve the bounded test slot with the original AttemptId before request.

## Terminal sending status

Run sms.progress on the original normalized outcome before automatic status
queries. Successful acceptance needs no later provider query or
operator confirmation; keep the original provider status as detail. Pending
results are retained without polling; Unknown/Failed never authorize automatic
resend. Optional later delivery information may be recorded if already observed,
but is never a completion/acceptance prerequisite. Future due notifications and
connected reply/stop observations keep their separate existing rules.

New send plans freeze sms-authority, provider-handoff and outcome. Apply
provider.handoff to the frozen request and original successful response. Include
the existing SMS Health row in the owned publication plan and save this actual
request timestamp/status once; no separate service probe is needed. An accepted
request closes our task/run and finalizes its used count without waiting for
network transmission, delivery or an ordinary-inbox capability test.
