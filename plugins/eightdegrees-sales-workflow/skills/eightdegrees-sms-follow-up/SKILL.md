---
name: eightdegrees-sms-follow-up
description: "Register and send factual material/follow-up notifications under standing permission, with current source-scoped stop, channel, timing and count controls."
---

# Notify without per-message review

After successful Gmail material handoff, register/reuse the original SMS
cycle immediately; a CRM receipt fault does not suppress registration. This is
part of [email-flow](../../references/email-flow.md), not a user command or new
native schedule. Standing notification-sms-v1 authorizes factual notifications
without ContentReview, SendApproval or repeated chat permission. An existing
explicit disable/revocation remains effective. Never create a human SMS review.

Use the verified own-number device/channel and actual recipient. Missing number
or tool is a scoped input/capability issue; unavailable inbound reading is only
coverage metadata. Do not require network/delivery or sender-display probes.
Use material.plan and current source-bound cycle limits. Confirm persistence
with material.verify(email_write,cycle_write), then freeze the factual payload
with sms.prepare and sms.verify(write_result), reusing original API responses.
No saved-body comparison or seven-page projection validation is required.

Use notification.dispatch once at actual due sending; check current standing policy, affected source/channel
reply/stop/Pause, device/recipient, window, manual+AI count and original attempt
once. Persist stable AttemptId/idempotency key before request_sms. Keep the
observed limits, context counts, unknown attempts and existing stopped contexts;
never let one old unrelated project stop block a newly authorized context.
The real connector's Trusted route is used when configured; actual provider
restrictions are not bypassed. Factual text stays within the adapter contract,
without marketing, quotations, commitments or fabricated appointments.

The successful original AndroidSync acknowledgement completes dispatch. Count
it once, save only affected results and next due pointer, and return. No status
polling, recipient confirmation, repeated permission, automatic retry or new
per-email timer. Failure repairs only its original effect/projection.
