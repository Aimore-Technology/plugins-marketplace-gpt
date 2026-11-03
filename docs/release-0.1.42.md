# EightDegrees Sales Workflow 0.1.42

start/stop controls whether scanning runs, not whether a native task exists.
start patches RunSettings.scan_control.enabled=true; stop sets false. Both
verify settings readback, preserve all other state and perform no immediate
scan, workflow run/log creation or scheduler management operation. Old interval
arguments do not change recurrence. Native tasks remain configured separately.

- Every manual/periodic run-auto reads only registered RunSettings FIRST. A
  stopped result ends quietly before event discovery, watches/task/form reads,
  source queries, EventIndex/cursors, run/log/Health/Today writes or effects.
  A missing/invalid switch permits no work; no automatic setup rebuild.
- Deterministic switch plan/readback/entry helpers are packaged and integrated
  before watch planning, event probing and queue admission. A stop after a send
  admission blocks release. In-flight accepted results may finish original
  persistence; no new work is admitted after stop.
- New installs are stopped. With no switch, preserve only verified legacy
  enabled/approved Running state. An explicit switch supersedes native scheduler
  metadata. Explicit start/stop creates the new field without modifying old
  job IDs, lifecycle/unknown attempts, cadence, approvals or cursors.
- Re-enable resumes original pending/due events with original versions,
  approvals, expiry, counts and attempts. No missed-tick replay, no new customer
  permission and no unique executor/native identity requirement. Provider
  handoff and CRM readback rules remain.
- Removed obsolete native create/delete planning and its old acceptance tests.
  Replaced them with switch-only regressions and 17 new early-stop/resumption/
  admission tests. Both editions pass 580 offline tests. A lower suite count
  reflects retired scheduler-management features, not dropped business guards.

Both packages and standalone Skill Pack are inspected. Native/local task
creation, deletion or live channel effects are not exercised by this release.
No live task, scanning flag or customer account is changed during packaging.
An existing externally configured task still wakes; stop makes its workflow
return after the settings read, rather than cancelling the task itself.
