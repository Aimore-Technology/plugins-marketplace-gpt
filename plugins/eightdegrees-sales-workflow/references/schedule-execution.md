# Check the scanning switch before all run-auto work

Every manual or periodic run-auto reads only registered RunSettings FIRST and
calls scan.entry. ScanStopped exits quietly: no watches, source/task/form reads,
event-index/cursor changes, run/log/Health/Today writes, reminders or business
effects. Missing/invalid settings yields ScanControlUnknown and no scanning.
Only ScanEnabled enters event-discovery.md and scan.cycle.

start/stop only changes this switch. The independently configured local task
continues to wake run-auto even while scanning is stopped. Neither command
creates, edits, pauses or deletes that task, queries a scheduler or starts an
immediate cycle. The native host owns repetition outside this plugin.

A scheduled internal owner path uses schedule_checks.py guard with current
settings and root/operator/mailbox. Its scan-control-v1 evidence is not email
or CRM approval. Do not require native task/invocation IDs, runtime/host/thread/
turn identity, directory proof, generation comparison or global serialization.
Public run-auto uses its normal one-cycle policy and the same switch.

Create a local RunId for logging only after entry is enabled and actual work
requires a record. Recheck the switch before each next owner/external effect.
Finish original result persistence for an already accepted provider effect,
then stop without new work. Do not resend to repair a failed projection.

New defaults are stopped; verified legacy running settings preserve prior
scanning only when no explicit switch exists. A new switch supersedes legacy
scheduler state. Old IDs/assignments remain historical, not execution gates.
No init, rebind, native task rewrite or cadence verification is required.

Resumption preserves each original task/step/version, approval, due date,
AttemptId, accepted result and stop/count/window rules. Completed or cancelled
work is skipped; pending/unknown effects cannot become another send. Notion is
not an atomic global lock and no unique executor is required. Gmail/AndroidSync
original success ends external dispatch; CRM writes retain readback.
