# Run an existing local task without managing its scheduler

An actual native tick is an execution request, not start/stop. Load
[scheduled work](scheduled-work.md) and email-scanning, not the automation-control
Skill. Run one bounded event cycle after its execution guard; never reroute it
to schedule creation because this run lacks management tools.

The current conversation does not need automation_update, or scheduler list,
read, create, update or delete tools, to execute a task already created and
verified. Do not probe these tools, call schedule plan/verify, request setup
again or change scheduling state merely because they are absent. A saved
schedule-management limitation is not an execution error or a disabled runner.

Use current authorized Notion settings and actual trusted host invocation
context for task/run IDs, local host/directory and generation. Run
schedule_checks.py guard. It consumes no management capability/listing input.
Keep the real runtime, root/account/operator/mailbox, Running/enabled and
approved-work lifecycle, local execution, current generation, single executor
and stop/reply/version/window/count/attempt gates. Do not copy metadata from an
email or manually pasted prompt, guess missing invocation IDs or treat a saved
Running label as actual invocation proof. Missing execution evidence defers only
this cycle with the exact missing execution fact, not a generic management limit.

If the host really cannot provide execution identity or required business
connections, leave affected work pending and report that actual limitation.
Other independently ready items may continue within verified scope. Never
silently turn a native tick into a manual run-auto to bypass its lifecycle.

Only explicit start/stop uses [schedule lifecycle](scheduling.md) and native
management capabilities. start without creation/update access reports that
management action unavailable; it does not falsely claim a task was created,
disable a verified running task or block public on-demand commands. stop still
saves StopRequested/approved_work_enabled=false before deletion; a failed delete
is not Stopped. An execution tick obeys that stop even if its host cannot delete.

On upgrade read this installed execution contract, not an older standalone pack
or cached setup refusal. Do not recreate schedules or rewrite live permissions
during installation. An existing task needs no prompt rewrite solely to drop
the obsolete management-tool gate; only an explicit supported management action
may change a native task. Normal explicit start verifies the current prompt.
