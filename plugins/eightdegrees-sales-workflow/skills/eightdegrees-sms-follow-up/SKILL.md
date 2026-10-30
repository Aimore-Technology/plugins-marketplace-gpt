---
name: eightdegrees-sms-follow-up
description: "Prepare and execute approved, bounded SMS follow-ups after verified material delivery; stop on replies and reconcile manual sends, channel limitations and unknown results."
---

# Follow up after materials

Before dependent writes, use [execution preflight](../../references/execution-preflight.md) to generate, persist and read back this owner's affected-role plan; a failed preparation stops the phase. Apply the [owner completion contract](../../references/owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action.

Before approval/dispatch, read [connector experience](../../Experience/connector-contracts.md) for the observed AndroidSync body/key constraints and distinguish network state from delivery. Revalidate actual current limits; do not shorten approved text silently.

Read [operating-contract](../../references/operating-contract.md) and [sms rules](../../references/sms-rules.md). Load task fields from [notion-model](../../references/notion-model.md) when creating or resuming records.

An explicitly authorized one-message channel acceptance/timing exception follows sms-rules, with a separate owner invocation, exact test recipient/device/approval and actual status evidence. It does not enable automatic enrollment, bypass old stop/Pause or widen run-auto/report. A stand-alone probe is not a completed material-follow-up workflow.

1. Require a verified ACTUAL material-send record, customer, source/version, time and provider/manual evidence. A draft, approval or unknown send does not start a cycle. Reuse the same cycle per material event; at most one active cycle per customer. Resending materials never resets counts.
2. Check the operator's own sending number, customer number, verified channel capability and latest accessible reply/stop/manual-pause state. For production follow-ups an unverified gateway permits drafts/tasks only, not automatic sends or substituted service IDs; the explicitly authorized one-message channel acceptance above remains a separate test. The operator may send manually and register actual time/result; include those messages in the cycle count.
3. Schedule the first follow-up no earlier than actual material send +30 minutes, the second no earlier than first actual follow-up +24 hours. Use the configured send window/no-send dates; outside-window due times roll to the next permitted day 10:00. Missing holiday list requires the operator's date confirmation in that send approval. An explicit one-message approved window can override the default, not the two-message cap.
4. Prepare light acknowledgement/follow-up copy. ContentReview handles edits; SendApproval separately binds own number, recipient, exact text/version and earliest/latest window for EACH message. Email approval is not SMS approval. Changed text/number/window or expired approval requires new approval; do not catch up an expired send.
5. Before sending, reread approval, attempt ownership, manual+AI count, latest reply/stop state, time and channel checks. Persist AttemptId first; send only when all pass. Record actual provider/manual result. Unknown reserves the slot and suspends later messages until reconciled; a log failure is repaired without resending.
6. On an observed reply/rejection/complaint, stop unsent cycle messages first, then hand the communication to its processing workflow or the operator. Do-not-contact remains stopped. Unconnected WeChat/WhatsApp/Telegram/phone replies require the operator's Notion pause/cancel; do not claim cross-channel real-time coverage.
7. Stop after two related follow-ups TOTAL from the operator and AI. Unknown manual count pauses the cycle; one manual send leaves one slot, two leave none. Handover at cycle end; a new cycle requires the operator's explicit manual start with new context and approvals, never an automatic reset for a third old-cycle message.
8. Return actual counts, result IDs, next eligible time or stop reason and original task/run links. Do not mark unverified gateway, paused or unknown results as completed delivery. Verify the own-number and original-inbox reply experience before enabling automated SMS.

## Tool selection and current outcome

Discover the actual SMS request tool and stored device policy before approval.
For AndroidSync, request_sms follows that policy; android_create_sms_draft is a
draft/forced-native-approval route, not the default Trusted send path. Do not
introduce a second approval gate by picking it. Respect a genuine current
Manual/Web approval requirement. A missing inbound reader keeps automated SMS
disabled; one observed send does not establish two-way readiness. Apply
[outcome state](../../references/outcome-state.md) to separate current result,
operator receipt/sender observations and immutable approval-time snapshots.
Use the outcome verification in send completion; never release an abandoned
native candidate or invent a provider cancellation. Missing native cleanup API
is a capability limit, not a request to approve that old draft.
