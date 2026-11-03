# EightDegrees Sales Workflow 0.1.41

Local scheduled sessions may not expose native execution identity. Global
unique-executor requirements blocked otherwise ready business work. This release
removes those requirements from instructions and all affected helper gates.

- task-state-v2 scheduled guard reads current authorized root/operator/mailbox,
  local runtime/mode and enabled Running/desired Running/approved-work state.
  Native task/invocation IDs, generation proof, host/thread/turn identity, working
  directory metadata and global activity/serialization are not execution gates.
- scan.cycle no longer requires executor observations or sole-conversation
  assignment. Legacy executor_mode, single_owner_required and assigned-thread
  values are ignored without an init/rebind requirement. New defaults omit them.
- Local run labels are generated for logs/recovery, not global authorization.
  Repeated admissions keep the same root/start-derived label or explicit UUID.
  Dispatch and owner publication no longer reintroduce native identity gates.
  Compaction recovery keeps command/root/policy/original budget/receipts while
  executor_id becomes optional diagnostics.
- Each task/step/version still checks approvals, stop/window/count and original
  attempts. Completed/cancelled effects are skipped; pending/unknown attempts
  cannot become a new send. Successful Gmail/AndroidSync acceptance closes
  dispatch; CRM readback remains. Another active session alone is no global block.
- Explicit start/stop still targets the actual owned native job so unrelated
  schedules cannot be changed. One configured scanner per root avoids unnecessary
  duplicate polling; this is not a sole-worker identity check. No schedule is
  created, live approval broadened or prior attempt reset by installation.

Both editions pass 596 offline tests, including 16 new task-state regressions.
Older exclusivity expectations were updated to the requested behavior; tests for
wrong installation scope, stop/revocation, changed payload, unknown attempts,
completed effects, original budget and command policy remain. The new cases
exercise scheduled routing/final publication, scanning/dispatch without native
identity and generated local recovery IDs. Packaged artifacts are inspected.

Notion is not an atomic distributed lock. This release removes global
exclusivity; it does not promise exactly-once concurrent execution. Use provider
idempotency where available and original task attempts. Live local scheduler
execution and simultaneous providers were not exercised by this release.
