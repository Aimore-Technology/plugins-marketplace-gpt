# Native approved-work schedule lifecycle

start creates/reuses ONE native 15-minute task for this Aimore root; stop deletes
it. Both are scheduling-only: no immediate business execution or extra daily
task. The [prompt](../assets/scan-schedule.md) calls email-scanning directly under
[scheduled work](scheduled-work.md), not public manual run-auto. Valid Automatic
approvals can execute on ticks; Manual work and every normal approval gate stay.

## Runtime and ownership

GPT uses a cloud ChatGPT Work GPT task; Claude uses a Cowork native cron task.
These are host-owned tasks, not operating-system crontab or an external daemon.
Discover actual native list/read/create/update/delete tools, automation_update
first when exposed. Use the live schema and required native confirmation; do
not invent an endpoint or replace the selected runtime with a local Codex worker,
a reminder without connector access, a Page controller or another cloud service.

Verify actual plugin/Skill and authorized cloud connector access, exact 15-minute
cadence and timezone. Prefer a quarter-hour anchor where supported; otherwise
record actual due/check times and morning catch-up limitations. Recurrence
representations (RRULE/cron/native interval) follow the actual tool. A normalized
interval_minutes=15 is evidence derived from readback, not a guessed API field.
Cloud Work setup can be completed in Work when this Codex chat lacks its tools;
do not call that absence a failure of Work itself. Claude runtime acceptance
remains untested until observed in the customer's actual Cowork account.

Identity uses eightdegrees-scan:<normalized Notion root UUID> in the full native
prompt, the actual task ID and provider/account/executor/runtime. List paused
tasks too. Titles alone cannot establish ownership. A different executor must
be reconciled on its owner before starting another. Do not discard stale IDs.

## State and upgrade

Additive scheduling fields: enabled, desired_state, state, generation, owner_key,
provider, account_id, owner_host, runtime, schedule_ids, actual_scan_minutes,
prompt_sha256, approved_work_enabled, pending_attempt and last_verified_at.
Fresh defaults are Stopped/disabled, runtime unset and approved_work_enabled=false.
Installation and init create no tasks. Legacy jobs/approvals/Pause/attempts remain;
package upgrade never broadens an old no-send lifecycle. Explicit start establishes
the approved-work lifecycle after native readback. Unbound legacy state defers.

States: Stopped -> Starting -> Running; Running/Starting -> StopRequested ->
Stopped. Unknown native outcomes keep one pending AttemptId and NeedsReconciliation.
Known native success followed by Notion failure repairs its projection, not the
native mutation. Notion is not an atomic execution lock.

## Start

1. Read actual setup, saved state, complete native list including inactive
   tasks and owned task details. Resolve previous unknown/pending attempts first.
   More than one owned match or uncertain other-host ownership blocks creation.
2. Reuse an unchanged verified approved-work task/generation. For a new or
   changed lifecycle, advance generation and persist Starting intent/AttemptId
   before native mutation. Bind root/operator/mailbox/runtime in the full prompt;
   preserve the user's model/settings. A legacy no-send prompt needs explicit
   current start, not an automatic upgrade.
3. Create/update through the selected native runtime. Save the actual returned
   ID/result, read prompt/cadence/timezone/enabled state, and list again to prove
   one owned task. Only verified success sets Running, enabled=true,
   approved_work_enabled=true and actual_scan_minutes=15. This verifies native
   configuration, not successful future ticks or channel delivery.

## Stop

1. Persist desired_state=Stopped, approved_work_enabled=false and StopRequested
   before native deletion so observing ticks defer between steps.
2. Delete only exact proven owned IDs, including owned duplicates; preserve
   unrelated tasks and all business records. Missing delete API/confirmation or
   unknown result stays pending with the native link, not a fake Stopped state.
3. Verify complete absence including inactive tasks, then clear live IDs and
   save Stopped/disabled with original results in history. Advance generation
   once on transition; repeated stop with verified absence is a no-op. An empty
   list alone cannot settle an unresolved earlier create.

Stop prevents future ticks and requests exit at a checked boundary; it cannot
undo a provider operation already accepted. Record that limit. Public manual
run-auto remains a separate no-customer-send cycle while scheduling is stopped.

## Each tick and offline helper

Read fresh lifecycle/setup and actual native invocation metadata before work
and between dependent steps. Validate actual task ID, current generation,
runtime/executor, root/operator/mailbox and approved_work_enabled. A busy, stale,
stopped or uncertain run exits without takeover, parallel catch-up or resend.
Only a successful guard selects scheduled-approved-work. It authorizes checking
Automatic steps, not their approval; sending still needs exact current approval,
window/stop/count/channel/attempt checks. Due daily summaries, reminders and
confirmed appointments use the same cycle, original IDs and phase deduplication.

schedule_checks.py plan|verify|guard consumes normalized original native evidence.
context includes runtime=work-gpt-task|cowork-cron-task plus actual root/account/
provider/host/operator/mailbox/timezone/generation. Each task read includes runtime,
id/full prompt/read_verified/enabled/interval_minutes/timezone and provider binding.
Supply complete-list flags and actual capabilities, never guessed booleans.
A plan is not Running/Stopped, and the local helper is not native enforcement.

Stay quiet while nothing actionable changes; notify meaningful failures,
completion or required operator action with original links. Save partial coverage
and actual times. A 15-minute tick alone cannot prove a 19-minute reminder deadline.

## Platform references

[OpenAI scheduled tasks](https://learn.chatgpt.com/docs/automations) documents
Work tasks, plugins, connected tools and minute-based existing-chat schedules.
[Work cloud](https://learn.chatgpt.com/docs/get-started-with-work) distinguishes
cloud execution from connected local resources.
[Cowork scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
is the Claude target. Documentation is not this account's native readback.
