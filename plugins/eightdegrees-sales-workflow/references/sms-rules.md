# Notification SMS cycle rules

Factual notifications use default enabled standing notification-sms-v1 authority
under [SMS notifications](sms-notifications.md). No individual SMS content/send
review or extra continue command is required. Generate/edit the copy, freeze its
actual text/recipient/device/version and send when due after the fresh checks.
Email approval and CRM fact review remain separate.

- First follow-up >= actual material Sent+30 minutes. Second >= first actual
  follow-up+24 hours, not its planned time. Internal reminders use their own
  configured deduplicated phases.
- Customer SMS window defaults Mon-Fri 10:00-17:00 Australia/Adelaide with DST
  and configured no-send dates. Roll outside-window due work to the next allowed
  time; never send early just to fit. The standing SMS policy includes that
  calendar fallback; an unverified holiday list is disclosed without asking for
  approval per SMS. Email holiday/date confirmation remains unchanged.
- Manual and AI related follow-ups count together toward TWO per cycle. One
  active cycle/customer. Repeated material events/resends never reset counts or
  existing due times. Unknown results reserve a slot and block later attempts.
- Store CycleId, actual material event/source/version/time, each send's actual
  time/AttemptId/result, manual+AI count, next due/window, latest reply/stop/Pause
  and handover. A closed/stopped/capped cycle is not automatically reopened.
- Reply/rejection/complaint/opt-out or operator Pause stops affected unsent work
  before ordinary processing. Authority revocation blocks future dispatch.
  Unconnected channel replies are not observed automatically.
- Verify actual own-number display, stable gateway and ordinary-inbox reply
  visibility, device ownership and latest accessible reply coverage. Permission
  is enabled by default; unverified capability still blocks actual dispatch.
  Do not substitute a service sender ID or force another app approval route
  when the actual device is already Trusted.
- A changed unsent notification needs a new frozen version/check, not a human
  decision. An already pending/unknown attempt must be reconciled first. Never
  mutate its text and resend or repair a log by another SMS.

## Explicit controlled channel test

A deliberate controlled-channel test may use a documented one-message exception
with exact configured recipient/device/body and actual result evidence. Record
any requested timing waiver and the genuine current device policy; do not ask
for a second human approval after the operator has authorized the controlled
notification. Existing stop/Pause/unknown attempts remain unchanged. A stand-alone
probe is not material-follow-up acceptance; a real follow-up still needs actual
material Sent. Network acceptance is not handset delivery, and old receipt
observations do not verify this new request. Never release abandoned old drafts.

## Automatic handoff

The email owner must register/reuse the downstream cycle/due/notification or
blocked/stopped result immediately after verified material Sent under
[material handoff](material-handoff.md). No per-email native task. The shared
queue handles due notification sending in the same eligible cycle or a later
run-auto/native tick without private owner or continue commands.
