# start/stop is a scanning switch, not native task management

0.1.42 replaces previous schedule create/delete semantics. Only patch the
registered RunSettings.scan_control enabled flag, verify actual readback and
return the settings link. Do not discover scheduler APIs, require native IDs/
identity, edit cadence/prompts, create/delete jobs or make a workflow log for
this settings-only command. Old interval arguments do not control scheduling.

Every manual/periodic run-auto FIRST reads this switch. Stopped means no other
source/task/form reads, cursor/index updates, run/log/Health/Today writes or
business work. Do not load owners or revive setup. Unknown switch means no
scan, not assumed enabled. Keep the external repeating task intact.

Recheck before new work; persist only an already in-flight effect's original
result after stop. start resumes original due work/cursors/approvals/attempts,
without replaying missed ticks, reopening closed work or resetting limits.
No unique executor/session identity is required. Native recurrence is configured
separately; helpers and this Skill never manage it.
