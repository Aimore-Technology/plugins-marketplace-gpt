---
name: eightdegrees-automation-control
description: "Create, reuse or delete one local 30-minute (20-minute optional) approved-work task on the selected computer. Does not immediately scan or send."
---

# Start or stop local periodic work

start establishes one local host-owned task; stop deletes it. Use
[schedule lifecycle](../../references/scheduling.md),
[scheduled work](../../references/scheduled-work.md) and the edition's
[runtime](../../references/platform-runtime.md). Default30 minutes; optionally
start interval_minutes=20. No new public command.

1. Read RunSettings, actual selected computer and absolute working directory.
   GPT uses codex-local-task; Claude uses cowork-local-task with verified
   local-folder execution. Both require execution_location=local. Discover
   automation_update first when exposed, then actual native schemas. Missing
   local support remains unconfigured; no cloud job, OS cron or backend fallback.
2. Before dependent writes persist/read back a scheduling-only plan under
   [execution preflight](../../references/execution-preflight.md) and
   [owner completion](../../references/owner-completion.md). Read complete native
   listing including paused jobs and owned prompts. Reconcile another host/
   runtime and unknown attempts first. Every Notion write uses
   [exact-call preflight](../../references/notion-mutation.md).
3. Reuse/update one exact owned local task, or create after verified absence.
   Save intent first. Verify actual ID, local mode, owner computer, directory,
   installed Skill/connector access, full prompt, selected cadence/timezone and
   enabled state before Running and approved_work_enabled=true. start grants
   no approval, enables no disabled SMS channel and runs no immediate scan.
4. stop saves StopRequested and disables approved work, deletes only proven
   owned IDs, then verifies complete absence before Stopped. Support deletion-
   only legacy cloud cleanup on its original scheduler; never relabel it local
   or discard its ID to create another worker. Preserve business history,
   approvals, attempts and unrelated tasks.
5. Return actual task/result links and host/directory, with any setup limit.
   The computer/app/local runner must remain available. Restart does one current
   discovery, never a burst of missed ticks. init/install/run-auto creates no
   schedule. No acceptance sends, CRM changes or immediate business execution.

Apply [provider completion](../../references/provider-boundary.md): successful
original Gmail/AndroidSync acknowledgement ends business dispatch; verify our
records and CRM writes without transport/delivery queries.
Use [operator experience](../../references/operator-experience.md) and
[local checks](../../references/local-check-batch.md) for concise actual results.
