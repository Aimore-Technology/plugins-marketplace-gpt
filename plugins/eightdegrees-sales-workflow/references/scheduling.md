# Scanning switch; native recurrence is independent

start/stop changes only RunSettings.scan_control:

```json
{"contract":"scan-control-v1","enabled":false}
```

start sets true; stop sets false. A successful change requires actual settings
readback. Repetition is a no-op. No immediate scan, approval, business effect,
workflow log creation or native scheduler mutation belongs to either command.
The legacy internal scheduling-only policy now means settings-only control.

## Entry before discovery

Every public or periodic run-auto FIRST reads only the original registered
RunSettings and calls scan.entry. This precedes watch/task queries, EventIndex,
mail IDs/bodies, CRM, Dropbox, owner plans, invocation/run records and reports.

- ScanStopped: end quietly. No discovery, source/task/form reads, watermark/label/
  EventIndex changes, logs, Health/Today updates, reminders or sends. The native
  host may still wake the task; the plugin does no further workflow operation.
- ScanEnabled: proceed to event-first discovery and affected approved work.
- ScanControlUnknown: reading/validating the setting failed; do not scan or
  mutate anything. Report the actual limitation without auto-init or retries
  across unrelated services.

Recheck the current switch before admitting another owner step/external action.
A stop after an original provider success permits only saving that effect's
original result; it never permits another send or new business work. A resumed
scan keeps original cursors, submissions, due dates, approvals, attempts and
accepted results. It does not replay each missed interval or reset expired work.

## Upgrade

New defaults are stopped. Installing/upgrading/init does not enable scanning.
With no scan_control field, derive enabled only from legacy scheduling fields
enabled=true, approved_work_enabled=true, state=Running, desired_state=Running.
Otherwise remain stopped. A malformed explicit switch is unknown, never a
fallback to legacy true. An explicit start/stop writes the new switch without
changing legacy scheduling/native job metadata. No init/rebinding is needed.

## Native task outside this plugin

The operator/host independently configures local repetition and invokes public
run-auto each time. Existing local tasks are left intact. start creates no task;
stop deletes/pauses none. Do not call automation_update or native list/read/
create/update/delete for these commands. Old cloud IDs/unknown native attempts
remain untouched metadata; cleanup is a separate explicit operator task.

30 minutes remains the suggested external cadence,20 optional. Old start
interval_minutes arguments neither change cadence nor schedule anything. No
unique executor, host/thread/turn identity, native invocation ID or global
serialization proof is required. Keep per-task approvals and original attempts.

## Deterministic helpers

scan_control.py gate/plan/verify are exposed as scan.entry, scan.control-plan and
scan.control-verify in local_checks.py. plan returns only a scan_control patch
and write_required; verify checks the saved flag and unchanged other settings.
schedule_checks.py plan/verify are compatibility aliases to the same switch;
its scheduled guard uses the switch and actual root/operator/mailbox scope.
No helper grants approval or calls any connector/scheduler.
