---
name: eightdegrees-daily-brief-and-handover
description: "Build the EightDegrees daily Notion action list, track important reminders and confirmed appointments, and record staged acceptance and handover without executing unapproved customer actions."
---

# Daily brief, reminders and handover

Read [operating-contract](../../references/operating-contract.md), [reminders](../../references/reminders.md) and [platform-runtime](../../references/platform-runtime.md). Use [pilot acceptance](../../references/pilot-acceptance.md) for rehearsal/handover.

1. Read authorized communication, PendingTasks, follow-up, CRM and run results. Distinguish waiting for John, approved/pending, completed, failed and unknown. Show Manual P0-A as "manual continue required"; do not execute it. Missing tool access is unverified, not healthy.
2. At daily 08:30 Australia/Adelaide, including weekends, upsert one dated DailyBrief and send John one available-channel summary. Include pending confirmation/review/follow-up/errors, source links, coverage and generated time. After a missed schedule, generate one catch-up with actual time, not repeated pushes. A manual run outside that time may update the brief; do not claim it was on time.
3. Handle important events separately under reminders.md: stop applicable customer sends first, notify through verified channels, then track actual acknowledgement and escalation. Normal draft waiting belongs in the brief unless John marks it important. Acknowledgement closes the reminder only, not original work or send approval.
4. Direct John to ORIGINAL task pages to fill data, edit, approve, return, pause, postpone or cancel. Automatic tasks validate on their next authorized scan; manual tasks require explicit continue. Do not make a summary-page edit execute customer actions.
5. Create Google Calendar appointments only from John's confirmed subject, time/timezone, participants and details. Reuse the existing single calendar; store event ID to avoid duplicate creation. Do not read unrelated family entries, turn all tasks into appointments, change existing appointments without a decision, or duplicate Hub/Hux reminders.
6. Refresh operational Dashboard views from the same WorkflowRuns/OperationLogs/HealthStatus, showing actual last-observed state and overdue/unknown items. No conversion/reply-rate analytics and no claim that a silent stopped scheduler is being monitored by an independent service.
7. At handover, provide the brief/settings/task/run links, connected vs disabled capabilities, failed/untested checks, manual recovery and pause/resume instructions. Rehearse the inquiry -> material -> SMS -> email path with Vivian and John, iterate 1-2 feedback rounds and use 5-10 authorized real cases without deliberate redaction. Separate package checks, simulation, channel tests and actual business acceptance.

Finish only for the requested summary/handover action; open business tasks and unacknowledged reminders retain their own states. Do not call the scanner recursively or send customer messages from the brief.
