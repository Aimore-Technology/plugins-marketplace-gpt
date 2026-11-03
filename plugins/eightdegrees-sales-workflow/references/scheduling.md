# Local approved-work schedule lifecycle

start creates/reuses ONE local task for this Aimore root and selected computer/
directory. Default30 minutes;20 explicitly optional. stop deletes it. Scheduling
commands do no immediate scan, customer send, CRM/Calendar write or approval.
Installation/init creates no job.

## Runtime and ownership

GPT uses codex-local-task in the desktop local Automation environment. Claude
uses cowork-local-task explicitly configured for local-folder execution.
Require execution_location=local, absolute working_directory and actual owner_host.
Discover automation_update first when exposed, then actual native schemas and
confirmation. Verify installed Skill/authorized connector access on that runner.
Missing local capability stays unconfigured with its native local setup action;
no cloud task, Page controller, plain reminder, OS cron or independent backend.

Identity is eightdegrees-scan:<normalized Notion root UUID>, actual native ID,
full prompt and provider/account/host/runtime/directory. List paused jobs too;
titles are insufficient. Verify execution mode from native configuration, not a
prompt saying local. An SSH conversation does not automatically select its host
as the schedule computer. Use the existing chosen directory, no new worktree.

## State and upgrade

Saved scheduling fields: enabled, desired_state, state, generation, owner_key,
provider, account_id, owner_host, runtime, execution_location, working_directory,
schedule_ids, target_scan_minutes, allowed_scan_minutes, actual_scan_minutes,
prompt_sha256, approved_work_enabled, pending_attempt and last_verified_at.
Fresh installs are Stopped/disabled with execution_location=local, runtime/
directory unset and approved_work_enabled=false.

Install/init adds configuration without creating/deleting/enabling tasks.
Preserve live IDs/runtime/history/attempts; do not relabel a cloud task as local.
On explicit start, reconcile/delete the old owned task through its original
scheduler and prove absence before a local replacement. An empty local list
cannot prove a different host/cloud task is gone. Inaccessible original owner
remains one migration item, never permission for another worker.

States: Stopped -> Starting -> Running; Running/Starting -> StopRequested ->
Stopped. Unknown native effects retain one pending AttemptId and
NeedsReconciliation. Known native success plus failed Notion saving repairs
only the projection, never another native create. Notion is not an atomic lock.

## Start

1. Read actual setup/settings, selected host/directory and complete native list
   including inactive tasks. Reconcile pending/unknown attempts and another
   owner first; multiple owned matches block creation.
2. Select explicit interval_minutes=20|30, else preserve a supported saved value
   or default30. Explicit start may migrate legacy15 to30. Before mutation save
   Starting intent/AttemptId and advance generation when changing lifecycle.
   Preserve model and unrelated native settings.
3. Native create/update binds root/operator/mailbox/runtime/host/directory in
   the full [prompt](../assets/scan-schedule.md); no immediate business run.
4. Read back actual native ID, full prompt, enabled state, local execution mode,
   exact directory/host, cadence/timezone and Skill/connector access; list again
   to prove one owned job. Only then save Running/enabled/approved_work_enabled.
   Configuration success does not certify future ticks or channel delivery.

## Stop and legacy cleanup

Save desired_state=Stopped, approved_work_enabled=false and StopRequested before
deletion. Delete only proven owned IDs, including owned duplicates, then verify
complete absence including paused tasks before Stopped. A pause, local flag,
missing API/confirmation or unknown delete is not success. Keep approvals,
customer tasks, source progress, provider attempts and unrelated schedules.

work-gpt-task and cowork-cron-task are legacy names allowed ONLY for stop/delete
verification on their original scheduler. They cannot start or execute a cycle.
Do not clear their live IDs after a failed cleanup. Repeat stop with verified
absence is a no-op. Stop cannot undo an accepted provider effect. A later
deliberate run-auto remains one manual cycle, without restarting scheduling.

## Each local tick and interruption

Reread lifecycle/setup and actual native invocation before work and between
effects. Match task ID/generation/root/operator/mailbox/runtime/owner_host and
execution_location/working_directory independently against actual execution.
Stale/stopped/wrong-host/cloud/busy/uncertain ticks defer without takeover.
Verify real non-overlap; a Notion lease is not enough.

The [scheduled procedure](scheduled-work.md) calls email-scanning once after
EligibleForScheduledCycle under scheduled-approved-work. It is the same event
workflow as run-auto, with native lifecycle evidence rather than manual scope.
Email/CRM approvals, standing factual-SMS policy and fresh stop/window/count/
attempt guards remain. Due briefs/reminders/confirmed appointments share this
one cycle, never per-email timers or an extra daily task.

The selected computer must stay on, awake and connected with its required app/
local runner. Sleep, app closure, shutdown or disconnect can delay/miss ticks.
After restart perform ONE current discovery/recovery from saved cursors and due
events, not one execution for every missed interval. Keep actual last/next run,
partial coverage, original budget and unknown/accepted attempts.

## Offline helper evidence

schedule_checks.py plan|verify|guard consumes original normalized native evidence,
not guessed API fields. context includes runtime, execution_location=local,
absolute working_directory, root/account/provider/host/operator/mailbox/timezone/
generation and optional interval_minutes. capabilities.local_execution and
local_context_ready must be true along with actual list/read/runner/cadence
evidence. runner_ready alone proves no local capability.

Actual task readback contains execution_location/working_directory plus original
ID/prompt/provider/host/cadence fields. The scheduled invocation independently
supplies execution_location/working_directory/host_id. Save the same fields in
settings and prompt; matching saved state alone is insufficient.

Verify the exact selected integer20/30 cadence. No silent hourly/cloud/directory/
host fallback. A plan is not Running/Stopped and helpers grant no native access.
Stay quiet while unchanged; notify meaningful failure/completion/required action.
A20/30-minute tick does not prove a19-minute reminder deadline.

## Platform references

[OpenAI local schedules](https://learn.chatgpt.com/docs/automations) documents
desktop project-directory execution and the running-computer/app requirement.
[Claude scheduling](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
currently defaults to remote execution but documents local mode for local files/
apps. Select and verify that local setting explicitly; ordinary Cowork cron is
not proof. Actual account cadence, local tick and deletion still require testing.
