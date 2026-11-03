# EightDegrees Sales Workflow 0.1.39

start/stop now targets host-owned local tasks instead of cloud schedules:
codex-local-task for GPT desktop local Automations and cowork-local-task for a
Claude task with explicitly verified local-folder execution. The default cadence
remains30 minutes, with20 optional.

- Native planning/readback and each tick bind execution_location=local, actual
  owner host and absolute working directory, alongside existing account/root/
  operator/task/generation/cadence evidence. Local Skill/connector access is
  required; a runner_ready flag alone is insufficient.
- Owner route and final publication gates also reject cloud/legacy or stripped
  schedule guards. No cloud fallback or metadata-only task relabeling.
- Old work-gpt-task/cowork-cron-task identities are deletion-only through the
  original scheduler. An empty local list cannot hide another owner/unknown job.
  Init/install adds local configuration without enabling/deleting a live task.
- Sleep, shutdown, app closure or disconnect can delay ticks. On return perform
  one current discovery from saved progress, not a replay of every missed tick.
  Existing approvals, stops, counts, expiry, provider acknowledgements and unknown
  attempts remain unchanged.

Both editions pass568 offline tests, including16 new local scheduling cases.
They cover local mode/directory/host, capabilities, Windows paths, actual native
readback, cloud/legacy rejection, migration, owner guards and restart procedure.
Native local start/ticks/stop/sleep/restart are not live-tested by this release.
No task, cloud or local, is created as part of this change.

[OpenAI local task documentation](https://learn.chatgpt.com/docs/automations)
supports desktop project-directory execution and the computer/app availability
requirement. [Claude scheduling documentation](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
distinguishes default remote tasks from local files/apps execution. Actual
account/version20/30-minute local support remains a required readback check.
The local target is an execution location, not a claim of offline inference.

Business workflow remains event-driven: run-auto is one cycle; start/stop only
manage recurrence. Successful original Gmail/AndroidSync acceptance ends dispatch;
CRM writes keep readback. No extra per-message SMS approval or continue command.
