---
name: eightdegrees-daily-brief-and-handover
description: "Build the EightDegrees daily Notion action list, track important reminders and confirmed appointments, and record staged acceptance and handover without executing unapproved customer actions."
---

# Daily brief, reminders and handover

Before dependent writes, use [execution preflight](../../references/execution-preflight.md) to generate, persist and read back this owner's affected-role plan; a failed preparation stops the phase. Apply the [owner completion contract](../../references/owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action. Before EVERY Notion page write, including the first create and progress/result properties, run [exact-call preflight](../../references/notion-mutation.md); only use its returned unchanged arguments after exit 0 and NotionMutationPrepared.

For report-only, first apply [Notion publication](../../references/notion-publishing.md): freeze the actual report/run/log target registry and preflight EACH mutation, including corrections. Execute only the reporting parts of steps 1, 2, 4, 6 and 7 below; step 6 reads existing Health/Dashboard evidence without updating those records. Do not run reminder, Calendar, handover-test or business-repair procedures. Outside-registry task/action/hub/preview defects are findings with a separate owner continuation, never child calls from report. Audit actual writes at exit against the same registry; a later clean publication does not erase an earlier violation.

Before registering Completed or final Success, apply [publication validation](../../references/publication-validation.md): freeze required page checks, validate actual entity types, capture both exit code and structured output, and pass the current completion-gate input to report-write. A nonpage exclusion, missing result or later passing revision cannot erase an earlier failure.

Use [evidence checks](../../references/evidence-checks.md) on entire actual saved Notion reports, including script/Skill paths, tables, examples and history. Code-format local paths/file names and invalid-URL examples before writing; check actual targets after targeted repair. Partial coverage or remaining findings keep quality issues open; repaired project-name cells cannot prove a global clean-link/zero-quality claim. Report route defects and specific upstream capability codes without changing tasks/health or rerunning providers under report-only scope.

Read [operating-contract](../../references/operating-contract.md), [reminders](../../references/reminders.md) and [platform-runtime](../../references/platform-runtime.md). Use [pilot acceptance](../../references/pilot-acceptance.md) for rehearsal/handover.

Use [the short daily layout](../../assets/daily-brief.md): needs a decision, recent channel-specific results, waiting/paused, coverage and original detail links. Retain full evidence/history behind these links. Do not replace a frozen approval preview with a summary.

1. Read authorized communication, PendingTasks, follow-up, CRM and run results. Distinguish waiting for the operator, approved/pending, completed, failed and unknown. Follow [task presentation](../../references/task-presentation.md) for current versions, missing dependencies and mode-specific next actions. Show Manual P0-A as "manual continue required"; do not execute it. Missing tool access is unverified, not healthy.
2. At daily 08:30 Australia/Adelaide, including weekends, upsert one dated DailyBrief, reusing its registered ID when present and registering the ID after a verified first creation; refresh one current summary (older snapshots remain labeled history), then send the operator one available-channel summary only if invocation scope permits. Apply [monitoring](../../references/monitoring.md): one GeneratedAt instant, explicit DataCutoff/coverage, timezone-derived local display and matching properties/body. Separate unresolved failures (including quality), unknown attempts, recovered history and synthetic test cases; provider writes succeeding must not hide incomplete Notes. Use native Notion mentions/external explicit links and literal file names; run whole-page link checks before writing and on actual saved output, including history. Use exact current-section patches, not a repeated waiting sentence or copied historical summary. After a missed schedule, generate one catch-up with actual time, not repeated pushes. A manual run outside that time may update the brief; do not claim it was on time.
3. Handle important events separately under reminders.md: stop applicable customer sends first, notify through verified channels, then track actual acknowledgement and escalation. Normal draft waiting belongs in the brief unless the operator marks it important. Acknowledgement closes the reminder only, not original work or send approval.
4. Direct the operator to the registered ordinary action pages for relevant answers, content/send choices and receipt acknowledgement under [operator actions](../../references/operator-actions.md), with original task details secondary. Preserve legacy-route exceptions. Automatic inputs validate on an authorized scan; Manual tasks require explicit continue. Report-only invocations link existing pages without creating/editing forms or consuming decisions; summary edits execute no customer action. Closed tasks show outcomes without active form controls.
5. Create Google Calendar appointments only from the operator's confirmed subject, time/timezone, participants and details. Reuse the existing single calendar; store event ID to avoid duplicate creation. Do not read unrelated family entries, turn all tasks into appointments, change existing appointments without a decision, or duplicate Hub/Hux reminders.
6. Refresh operational Dashboard views from the same WorkflowRuns/OperationLogs/HealthStatus, showing actual last-observed state, unresolved quality issues and overdue/unknown items. A report reads original attempt times; it must not stamp itself as a successful service probe or leave init times after later observed operations. Degraded capabilities remain visible after recovery. No conversion/reply-rate analytics and no claim that a silent stopped scheduler is being monitored by an independent service.
7. At handover, provide the brief/settings/task/run links, connected vs disabled capabilities, failed/untested checks, manual recovery and pause/resume instructions. Rehearse the inquiry -> material -> SMS -> email path with a designated test contact and the operator, iterate 1-2 feedback rounds and use 5-10 authorized real cases without deliberate redaction. Separate package checks, simulation, channel tests and actual business acceptance.

Finish only for the requested summary/handover action; open business tasks and unacknowledged reminders retain their own states. Do not call the scanner recursively or send customer messages from the brief.

## Scheduled entry and current evidence

The native approved-work cycle calls due daily/reminder/confirmed-appointment
steps under [scheduled work](../../references/scheduled-work.md). It is not the
report-only shortcut: public report still sends no notifications and changes no
Calendar/business state. Use one saved business-day summary/notification marker
and actual event IDs; missed runs catch up once with observed time. Use current
canonical outcome evidence from [outcome state](../../references/outcome-state.md),
not historical init counters. Conflicting candidate/original states are disclosed
with scoped counts; do not repair business tasks from reporting.

## Operator path and local checks

Apply [operator experience](../../references/operator-experience.md) for Today, short review summaries/differences, verified prefill and explicit post-submit guidance. Give concise chat progress at meaningful stages; an internal read/check does not require another Notion status write. Run [local check batches](../../references/local-check-batch.md) over unchanged original captures instead of repeatedly serializing/rereading them. Preserve every required fresh external-action and saved-result check. Verified Today linked views replace manual queue snapshots; legacy queue mode remains until explicit upgrade.
