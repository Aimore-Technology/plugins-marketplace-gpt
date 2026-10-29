---
name: eightdegrees-automation-control
description: "Create, reuse or delete the installation's native 15-minute run-auto schedule for explicit start or stop commands. Does not scan, send or manage unrelated tasks."
---

# Start or stop periodic scanning

Use `start` to set up one native task that invokes `run-auto` every 15 minutes;
use `stop` to delete that task. Follow [schedule lifecycle](../../references/scheduling.md)
and the edition's [runtime](../../references/platform-runtime.md). These commands
authorize that schedule operation, not an immediate scan or customer send.

1. Read current RunSettings and the actual native scheduler's tool schema. Require actual operator, root, mailbox label/time scope and connector setup before start. Missing setup goes back to init without creating a job. Resolve
   the installation, saved executor and previous create/delete attempt before
   mutation. For Codex, discover `automation_update` first when available. Missing
   tools or unsupported exact cadence means not configured; never create a daemon,
   use a different cadence or turn a reminder into a connector-enabled worker.
2. Establish the [owner completion contract](../../references/owner-completion.md)
   for `scheduling-only`, covering only the affected run, settings and logs.
   Inspect a complete native task listing including paused tasks and read the
   actual owned task. Use the offline schedule helper to plan the scoped action.
3. For start, reuse the exact active task or update its native settings. Create
   only when absence is verified and no previous attempt is unknown. Save intent
   before the native mutation, then read back its actual ID, 15-minute cadence,
   prompt, timezone and enabled state before recording Running. Native host
   confirmation, when required by its UI, remains a pending step.
4. For stop, save StopRequested before deleting exact owned task IDs. Read the
   complete native list again; only verified absence permits Stopped. A pause,
   local flag or unavailable deletion API is not deletion. Preserve all business
   tasks, approvals, messages, historical runs and unrelated native tasks.
5. Gate final run/log completion, show the actual schedule/result link, then exit.
   Report unknown native results for reconciliation, never retry creation blindly.
   Installation, init and run-auto still create no schedules on their own.
