# EightDegrees Sales Workflow 0.1.32

This release applies the operator's dispatch boundary: Gmail owns email
transport; AndroidSync owns SMS transport after successful request acceptance.
Our workflow verifies its content, approval, destination, current stop/window/
count rules, original request binding and own saved records. It retains exact
CRM write readback as the explicit external exception.

A successful original Gmail response completes email dispatch. AndroidSync
AwaitingPhone/PendingApproval/ProviderAccepted also completes our submission;
those raw statuses remain provider metadata. No post-send Gmail Sent/raw MIME,
AndroidSync status polling, receiving-mailbox/handset checks or receipt-only
follow-up work is required. Normal inbound business reply/stop processing stays.
An ambiguous/rejected handoff is recorded honestly and never automatically
resent or polled. Internal record recovery never repeats the external request.

The new offline provider.handoff check binds the original successful response
ID to the exact verified Gmail draft or frozen authorized SMS request. New
phase contracts use provider-handoff instead of future sent-MIME evidence.
Outcome projections/UI/counts describe submitted requests; accepted SMS closes
our original task/run and finalizes its slot once. Already-captured legacy
Sent/Delivered/receipt proof remains history, without new external queries.

Material follow-up registration starts from successful email handoff, not an
additional Sent lookup. New CRM send receipts use the explicitly declared
send-receipt-v2 template; previously approved v1 bytes remain unchanged and
readable. Missing/incorrect CRM readback still blocks its internal completion.
Configured one-way SMS no longer requires an inbound/delivery/stability trial;
actual unavailable inbound coverage remains disclosed and stop checks stay.

Both editions receive the same business policy, helpers, defaults and Experience
card. Identity, sharing, permissions, command inventory and the 30-minute default
(20 optional), 900-second budget and 120-second reserve are unchanged. No live
accounts, schedules or historical reports are edited by this release. Offline
regressions and package checks do not establish a new live timing improvement.

Verified before publication: 433 offline tests passed in each edition, including
18 provider-boundary regressions. Marketplace/schema/reference gates passed;
the deterministic archives and common business-file parity are release gates.
