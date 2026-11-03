---
name: eightdegrees-automation-control
description: "Enable or disable scanning in Notion RunSettings. Never create, update, pause or delete an automation, and never run an immediate scan."
---

# Start or stop scanning

start sets scan_control.enabled=true; stop sets it false. Both use
scan-control-v1 under [scan control](../../references/scheduling.md). These are
settings-only actions; the historical internal policy name scheduling-only
does not permit any native scheduler mutation.

1. Read only the registered installation's actual RunSettings. Do not discover
   automation_update, list native tasks, require a runtime/host/session identity
   or verify cadence. Missing settings must be reported without starting init.
2. Run local scan.control-plan with operation=start|stop and original settings.
   Preserve every other setting, cursor, approval, task, due time, provider
   attempt, native task ID and legacy scheduling metadata. Patch only the
   returned scan_control. interval_minutes no longer controls anything here;
   an old argument must not modify cadence or create a task.
3. If write_required=false, return the existing switch state without another
   write. Otherwise perform one exact-call-preflighted settings update, then
   read back and run scan.control-verify. Never claim success from a plan or
   failed/unknown write. No workflow plan/run/task/action/log creation is needed
   for a flag flip. [Notion mutation](../../references/notion-mutation.md) still
   applies to the exact settings call; no other page is a permitted target.
4. Return Scanning enabled/Scanning stopped and the original settings link.
   start performs no immediate scan and supplies no business approval. stop
   leaves the externally configured periodic task intact; its next run-auto
   checks the switch and exits quietly without discovery or workflow writes.

Every run-auto, manual or periodic, reads the switch first under
[execution](../../references/schedule-execution.md). Stopped cycles perform no
mail/Dropbox/CRM/SMS/Calendar reads, task/form scans, event-index writes, run/log/
Health/Today updates or customer actions. No routine stopped notification. A
current in-flight provider effect cannot be undone; finish only its original
result persistence, then admit no next work. Re-enabling resumes original
unfinished events under fresh per-task approvals, stops, windows and attempts.

Native recurring jobs and their frequency are configured separately by the
operator/host. These commands never create, update, pause or delete them.
