# Local task means a verified computer and directory

Trigger: start/stop, a periodic tick or migration from an older cloud schedule.

0.1.39 changes the intended scheduler to a host-owned local task. A runtime name,
prompt mentioning local files or a successful recurrence create is not proof of
local execution. Verify actual execution_location, owner_host and absolute
working_directory, installed skills/connectors and exact20/30-minute cadence.
Missing local mode remains unconfigured, with no cloud or OS-cron fallback.

Keep the old task ID/runtime and pending attempts until its original scheduler
proves deletion/absence. An empty local list does not clear a cloud owner.
Only explicit start creates/enables the local lifecycle; init/install does not.
stop can clean proven legacy runtime IDs, but they cannot start or pass a tick.

The selected computer/app/local runner must remain available. Restart performs
one discovery from current saved state, not a run for each missed interval.
Preserve accepted messages, unknown attempts, original expiry/counts and budget.

Management-tool discovery is only for explicit start/stop. In 0.1.38 the old
blanket chat/runtime setup refusal could be misapplied to an existing tick.
Use the installed schedule-execution.md for ticks: they need actual execution
evidence and business connections, not scheduler management APIs. Do not clear
Running or relaunch setup solely because management tools are absent. Real
stops, stale IDs/generation, wrong host/directory, unknown attempts and missing
execution evidence still defer; never turn a tick into a manual bypass.

Read scheduling.md for management and schedule-execution.md for execution;
use the actual platform-runtime.md only for the relevant section. Offline normalized-evidence
tests cover locality/migration guards; they do not certify a live local host,
native connector access, availability or start/stop execution.
