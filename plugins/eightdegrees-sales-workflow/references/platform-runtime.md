# GPT local host: scan switch and independent recurrence

The operator/host independently configures local periodic calls to run-auto.
Use the installed plugin/Skill Pack and authorized connectors.30 minutes is
suggested,20 optional; the plugin does not create/configure a task or certify
that cadence. The selected computer/app must be available for local execution.

start enables RunSettings.scan_control; stop disables it. Neither command
queries, creates, updates, pauses or deletes native tasks or edits their prompt,
cadence, directory or host. Do not discover automation_update or scheduler APIs
for these commands. Existing jobs and IDs remain untouched.

Every manual/periodic run-auto FIRST reads only RunSettings and scan.entry.
ScanStopped exits quietly with no other workflow reads/writes, logs or effects.
ScanControlUnknown permits no work; only ScanEnabled enters event discovery.
Missing management tools or native host/thread/turn/invocation identity is no
execution blocker. A local RunId is just a log/recovery label.

Use [scan control](scheduling.md) and [execution](schedule-execution.md). Stop
before new admissions/effects; persist only an already accepted original result
after a stop. Keep approvals, scoped customer stops, windows, counts, cursors
and attempts. Gmail/AndroidSync success ends external dispatch; CRM retains
readback. New installs are stopped. Legacy verified scanning can be preserved
without init/rebinding or touching the native scheduler.
