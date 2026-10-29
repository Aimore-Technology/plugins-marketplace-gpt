# Native scan schedule lifecycle

`start` creates/reuses ONE native task every 15 minutes for this Aimore root.
`stop` deletes it. Both use scheduling-only: no immediate scan, customer send,
CRM update, business-task continuation, Calendar write or extra daily-report job.
The periodic prompt is [scan-schedule.md](../assets/scan-schedule.md); each tick
invokes the existing run-auto procedure once with its no-customer-send policy.

## Capability and ownership

Read the actual native create/list/read/update/delete schema. Codex first looks
for automation_update; use its supported scheduling interface, not raw directives
or guessed fields. Cowork uses its native Scheduled tasks flow. A UI-only
confirmation/deletion remains pending until the real host confirms it. Verify
the exact 15-minute cadence and installed skill/connector access in that account.
Do not substitute hourly execution, Chat reminders, /loop, crontab, a daemon,
another cloud service or an Agents API deployment. No scheduler is installed by
this package. Host availability does not follow from a manifest or documentation.

Build owner_key as `eightdegrees-scan:<normalized Notion root UUID>`. Identity
comes from this exact marker in the native task prompt, the saved actual task ID
and provider/account/host, never a matching title alone. List paused tasks too.
Another executor already registered for this root must be reconciled/stopped on
that executor before a new owner starts; GPT and Claude cannot independently
schedule the same work. Do not discard stale IDs to create a second scanner.

## State in RunSettings

Preserve existing settings and IDs. The additive scheduling record contains:
enabled, desired_state, state, generation, owner_key, provider, account_id,
owner_host, schedule_ids, actual_scan_minutes, prompt_sha256, pending_attempt and
last_verified_at. Existing target_scan_minutes remains 15. Fresh installations
are disabled/Stopped with empty IDs and no actual cadence. An explicit init
upgrade adds absent fields only; upgrading the plugin never schedules work.
Legacy enabled records without trustworthy native ownership need reconciliation.

Lifecycle: Stopped -> Starting -> Running; Running/Starting -> StopRequested ->
Stopped. Unknown native results use NeedsReconciliation and keep the AttemptId
and known native IDs. These are scheduling-body states, not new PendingTasks
select values. A native success followed by Notion failure is a partial projection;
recover its settings/log without creating/deleting again. A host-only deletion
failure is not Stopped merely because enabled was cleared locally.

## Start

1. Read actual setup and saved lifecycle, native task list including inactive
   records, and current task details. Resolve unknown earlier attempts first.
   A matching active task with exact prompt/cadence is reused; a paused or
   changed owned task can be updated through the supported native API. Multiple
   owned matches block start; don't create another. Never edit unrelated tasks.
2. Retain the generation for an unchanged running task. Increment it for a new
   lifecycle/replacement and save Starting intent plus one AttemptId before the
   native change. Bind the prompt to the actual root, operator, mailbox and
   generation; it includes no credentials or copied approval. Leave model and
   reasoning settings at the user's existing defaults.
3. Create/update through the real host. Save returned task ID/result promptly,
   read it back and list again to establish one owned task. Verify enabled state,
   exact 15 minutes, timezone and full prompt. Only then save enabled=true,
   desired_state/state=Running, actual_scan_minutes=15, IDs/digest and observed
   time. Persist operator/mailbox binding in the prompt and keep setup current.
   Return the native schedule link and first-run readiness, not delivery claims. RunningVerified establishes native configuration only; actual tick execution and source access remain unverified until a real scheduled run.

## Stop

1. Read ownership/list/current IDs. Save desired_state=Stopped and StopRequested
   before deletion so an observing scheduled run exits between steps.
2. Delete all proven duplicates for this SAME owner marker if present, using
   their exact IDs. Do not act on a title-only candidate or another host's
   unverified records. If deletion is unavailable, report the actual task link
   for native deletion and keep StopRequested; don't call a pause a delete.
3. Verify complete native absence including inactive tasks, then save
   enabled=false/state=Stopped, clear live IDs and record deletion evidence.
   Advance the generation once on the stop transition; repeat stop with verified
   absence is a no-op. Keep historical IDs/results in logs. A timeout/unknown
   result needs reconciliation. Do not delete business tasks or revoke approvals.

Stop prevents future scheduling and asks running scans to exit at their next
checked boundary. It cannot undo an already accepted provider operation or
guarantee mid-call cancellation. If native stop cannot interrupt a running task,
report it. Manual run-auto remains available as a separate one-cycle command.

## Every scheduled invocation

Read fresh RunSettings before business work and between dependent steps. Check
enabled, Running/desired Running, generation, actual native task ID, configured
operator/mailbox/root and executor. Stale queued ticks exit without business
mutations. A busy or uncertain scan owner defers the tick; no parallel catch-up,
sleep loop, takeover from a stale timestamp or nested scanner. Reconcile an
interrupted original run before unfinished work; external uncertainty never
triggers another send. Notion evidence is not an atomic lock. Keep native host
serialization where available and test concurrency separately.

Each eligible tick calls run-auto once. Manual tasks stay Manual; content and
send approvals are not created by the schedule. CustomerSendAllowed=false stays
in force. Existing configured internal reminders retain their own permissions.
Keep unchanged/non-actionable results quiet; surface new input/review tasks,
meaningful failures, completion and recovery with original links. Record actual
run/log progress and incomplete coverage rather than a fabricated successful scan.

## Offline helper and evidence

`schedule_checks.py plan|verify|guard --input <json>` has no scheduler/network
capability. Use normalized observations derived from actual native responses,
retaining the originals and field mapping. Input contains context (root_id,
root_url, operator_id, mailbox, provider, account_id, host_id, timezone,
generation), tasks, list_complete and list_includes_inactive. Each owned task
has actual id, full prompt, provider/account/host, read_verified, enabled,
interval_minutes and timezone. Supply real capabilities, saved scheduling and
pending_attempt, not guessed booleans. plan emits a proposed action/prompt;
verify requires fresh actual post-action reads. A plan is not Running/Stopped.
For guard, supply actual trigger, current scheduling and setup from RunSettings,
invocation (schedule_id, invocation_id), and any active_run. A stale-context or
busy result cannot satisfy completion. The helper is local evidence, not a host
enforcement layer or approval authority.

## Maintainer source notes

The [official OpenAI scheduling guide](https://developers.openai.com/codex/app/automations/)
describes minute-based existing-chat schedules and skill/plugin use; project-local
execution has desktop/machine availability requirements. The [official Cowork guide](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
describes native task management and built-in recurrence choices. Neither proves
that this particular account exposes a 15-minute create/delete tool. These
sources justify native discovery; actual readback remains acceptance evidence.

Pending native UI confirmation or a previously accepted result awaiting projection
recovery must be reconciled before another create/delete. Verification cannot
turn an unresolved in-flight create into Stopped from an early empty listing.
Generation zero is valid only for a fresh stopped lifecycle; starting/running
uses a positive generation.
