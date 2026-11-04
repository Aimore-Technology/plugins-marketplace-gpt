# EightDegrees Sales Workflow 0.1.54

Email has no sending window, weekday/holiday gate, date confirmation or clock
expiry. Once a scan sees the approved exact reply, it sends in that same cycle
at any hour. New v4 packages/narrative omit window metadata and clear obsolete
email date projections. SMS alone keeps configured quiet hours, delays and caps.

Existing frozen v2/v3/v4 content/recipient approvals remain valid at any hour;
legacy window bytes are history, not a reason to wait or reapprove unchanged
content. Consent accepts the exact historical narrative or its payload-identical
current timing explanation. No content, recipient, stop, withdrawal, sender or
accepted/unknown attempt protection is removed.

Recover old future email timers in discovery, queue construction and bounded
cycle selection while retaining their original keys and due-date history. Current
approved automatic email rows supplement unchanged backlog for real approval
checks; a projection is not send authority. Completed/cancelled rows, true human
waits, SMS clocks and explicit provider backoff remain unaffected. API handoff
still ends dispatch without delivery polling or duplicate sending.

Offline regressions cover nights/weekends/holidays, omitted and false date flags,
old expired/future windows, unchanged saved future timers, approved row recovery,
no-input cycles and retained SMS/backoff/stop/unknown controls. Actual target-host
timed sending and mobile display remain separate acceptance work.
