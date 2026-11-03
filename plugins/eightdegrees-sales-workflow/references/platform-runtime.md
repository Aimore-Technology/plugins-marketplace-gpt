# GPT runtime: local desktop Automation

## Existing task execution

A configured local tick uses [task-state execution](schedule-execution.md).
No unique executor, native task/invocation ID, host/thread/turn identity, current
directory proof, generation comparison or activity/serialization listing is
required. Read current authorized installation settings and exact task/attempt
state. Generate a local RunId for logging only. Legacy executor assignment
fields are inert; no rebind/setup loop. Missing management APIs do not block
execution. Stop/disabled authority, approvals and unknown attempts still apply.

## Explicit start/stop management

Periodic work uses a Codex/ChatGPT desktop local Automation on the operator's
selected computer and existing working directory: runtime=codex-local-task,
execution_location=local, actual owner_host and absolute working_directory.
Use the locally installed Skill Pack/plugin and authorized connectors.

Discover automation_update first when available and inspect its actual schema
for local environment/directory, recurrence, IDs and deletion. Preserve model
settings and required native confirmation. Never invent API fields or edit
hidden task files. An SSH chat is not proof of the intended execution computer.

Use [schedule lifecycle](scheduling.md). For an explicit start without an
existing verified task, missing local management tools/access/cadence leaves
that management action unconfigured with a native local setup action, never a
cloud Work task, Page controller, reminder, OS cron, daemon or new backend. Do not create a worktree;
use the selected existing local directory.

Keep the computer on, awake and connected with its required app/local runner.
Sleep, shutdown, app closure or disconnect can delay ticks. On restart use one
current discovery/recovery cycle from Notion, not a replay per missed interval.
Local scheduling does not imply offline model inference or local-only services.

A tick calls email-scanning once under a fresh scheduled-approved-work guard,
using current configured task state, without native executor identity. Public run-auto
remains one on-demand cycle. Preserve email/CRM approvals, standing factual-SMS
policy, stop/window/count/attempt guards and per-task attempt checks.

Install/init creates no task. Actual local start/ticks/stop, connector access and
native management require target-host evidence.
[Official local scheduling](https://learn.chatgpt.com/docs/automations) documents
desktop project-directory execution and the available computer/app requirement.
