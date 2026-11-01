# One queue; SMS notifications do not need another approval

Trigger: a user has submitted Notion input, an email has actually sent materials,
or a notification becomes due.

The 0.1.23 review showed an unnecessary second continuation step for manually
initiated communications, and per-message SMS approval despite their notification
purpose. 0.1.24 changes that procedure: preserve Manual intake provenance but
let the shared queue validate submitted communication decisions and continue.
Email/CRM fact review stays. Factual SMS notifications use default enabled
notification-sms-v1 standing authority, not ContentReview/SendApproval per message.

Apply queue-execution and sms-notifications before dispatch. Inspect relevant
reply/stop first, freeze exact notification text and source, validate current
policy/device/target/time/count and prior attempts, then send when due. A ready
successor may run in the same bounded cycle; a human wait, future time, stop or
unknown result does not loop. No private owner/continue command, no per-email
Cron and no fabricated human approval. Keep existing disable/revocation/history.

Verify actual public command behavior, current accepted snapshot and original
provider results. Offline guards cover policy/binding/body checks; no real send,
native scheduler or end-to-end acceptance is proved by changing instructions.

## Observed in 0.1.25

A network SMS result left old data/action/parent-run copy at AwaitingPhone. Stop was enforced in the cycle while the persona retained an older SMS permission. Several scans exceeded the 15-minute target. Use [unattended operation](../references/unattended-operation.md), related seven-page SMS readback and the separate restrictive overlay. Preserve historical payload/approval. Bound work and save a restart checkpoint; never shorten approval/stop checks or retry an unknown request to meet a tick. Offline fixes require separate host acceptance.

A 0.1.26 simulation exposed an over-broad ownership guard: cloud/global serialization was demanded for the explicitly assigned public on-demand conversation. Use the scoped current thread/turn plus original settings and complete installation Scan observations under unattended-operation.md. Do not mark global host coverage true or weaken native schedule ownership.
