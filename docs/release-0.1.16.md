# 0.1.16: fact integrity and native periodic scan commands

## Problem and resulting behavior

The partial 0.1.15 realistic-business run exercised initialization, manual intake,
input validation and one scan. Unconfirmed finance was projected as false before
being corrected; Notes drafts included workflow plumbing. Pre-form route checks
used confusing execution context, some connector proposals were refused, and
repeated source/publication reads increased work. Actual replies, SMS and report
were not exercised before the desktop cross-session bridge became unavailable.

Unknown customer boolean facts now stay Unknown/null through an offline
pre-write check. The standard Notes renderer rejects specific execution terms
in business action/next-step sections, including terms adjacent to localized
prose. Genuine source quotations and required audit headers are preserved.
Form registration has a metadata-only phase under the actual policy and PageId;
its result cannot substitute for execute-phase completion evidence.

The command surface is now init, start, stop, add-communication, run-auto,
reply-draft and report. Start creates/reuses one native 15-minute run-auto task;
stop deletes only that installation-owned task and verifies actual absence.
Each tick stays Automatic-only and CustomerSendAllowed=false. StopRequested,
generation, actual native IDs and executor binding reject stale ticks; unknown
attempts require reconciliation. There is no daemon/backend and no schedule is
created on installation or init. Missing exact native cadence/deletion is an
explicit incomplete result, never a fake success or alternate cadence.

## Scope and reviewer path

- Scheduling: references/scheduling.md, scripts/schedule_checks.py and the new
  eightdegrees-automation-control Skill; platform runtime files remain separate.
- Facts/Notes: scripts/fact_checks.py, scripts/crm_note.py and customer-facts.md.
- Ownership/routing: workflow_checks.py register phase, scheduling-only policy,
  notion_checks.py owner policy, frozen completion contracts.
- Read cost: owner-completion.md, notion-io.md and connector-io.md use affected
  targets, current captures and actual source IDs; fresh action checks remain.

The property preflight now rejects JSON-shaped ExternalIds before dispatch. ExternalIds uses a plain-text index after the observed JSON-shaped property
refusal; full evidence stays in page history. Known Dropbox IDs/revisions precede
search rediscovery. Bounded read recovery preserves earlier errors. These changes
do not claim a repair to third-party connector internals or measured speedup.

## Verification and limits

Both editions run the full offline suite, package validators and Skill checks.
Scheduler fixtures test create/readback/reuse, paused updates, duplicate and
cross-host ownership, unknown attempts, marker drift, exact deletion and stale/
busy ticks. They never create native schedules. Captured 0.1.15 evidence is
replayed outside this repository: unknown/false is rejected, corrected null
passes; the execution-heavy draft is rejected and the reviewed 1486-byte v2 is
accepted unchanged. No customer source data is packaged.

Live native scheduling cadence, UI confirmation/deletion, actual scheduled
invocation metadata, cloud skill/connector access, concurrency and runtime
latency remain unverified until the next authorized installed-plugin run.
The earlier incomplete mail/CRM/SMS/report acceptance is still incomplete.

## Upgrade and data/security impact

Reload 0.1.16 and explicitly run init to add missing lifecycle fields, preserving
actual IDs, actors, approvals, contact fields and provider attempts. Legacy active
schedules with uncertain ownership require reconciliation, not a second scanner.
Old approved text failing a new prose guard needs a fresh reviewed version; never
silently edit it or repeat an already successful CRM append. The package grants
no account permission, sends no customer message and rewrites no customer data.
Existing valid business Notes retain their approved bytes. Native schedule
management authority is limited to explicit start/stop and the exact owner
marker/root/provider/account/host. Notion is not an atomic lock or host enforcer.

## Next live acceptance

Use test-0.1.16.md. Keep recovered errors and expected validation refusals
separate from business case outcomes. Publish the final user-facing test log in
Chinese. Do not claim that an offline helper result proves live execution order.
