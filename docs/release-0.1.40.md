# EightDegrees Sales Workflow 0.1.40

A scheduler management limitation must not stop an already-created local task.
The blanket chat/runtime refusal in the older 0.1.38 standalone pack could be
misapplied as a periodic execution prerequisite. Both plugin editions and the
new standalone pack now explicitly separate the two paths.

- Explicit start/stop discovers only the relevant native management capabilities.
  Unavailable list/read/create/update/delete returns an operation-scoped limit.
  No false task creation, deletion or Stopped success; no changes to existing
  Running state merely because a management API is absent. StopRequested still
  disables approved work even if native deletion needs another interface.
- An existing native tick loads schedule-execution.md and email-scanning, never
  automation-control, scheduler plan/verify or another management setup pass.
  A current execution guard uses actual trusted task/invocation identity, local
  host/directory, Notion lifecycle, generation and executor ownership without
  needing scheduler administration access in the execution conversation.
- Current approvals, CRM readback, standing factual-SMS authority, stop/version/
  window/count/attempt checks and provider handoff boundaries remain. A missing
  management tool is not evidence of a missing business connector. Real execution
  identity/connection failures remain scoped, not fabricated or silently bypassed.
- Default30-minute/optional20-minute recurrence, one bounded event-driven cycle,
  idle exit and one current recovery after interruption remain unchanged.
- Existing native prompts need no management-only rewrite for this fix; installed
  execution instructions take priority over obsolete setup wording. No tasks are
  created/recreated or live permissions changed by installation/upgrade. Only an
  explicit supported start/stop action manages a native task.

Both editions pass 580 offline tests, including 12 new execution/management
regressions. Cases include absent/unavailable management APIs with a valid tick,
owner routing and final publication, management-only failure scope, exact task
reuse, failed deletion and retained execution/stop/ownership/overlap guards.
Packages are inspected; these checks do not certify a live local scheduler or
actual mail/SMS effects. No live task or customer message is part of this release.
