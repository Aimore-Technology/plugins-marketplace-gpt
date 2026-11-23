---
name: eightdegrees-email-scanning
description: "Discover changed and due inputs; reuse captured data, resume original backlog and route inquiries through one cached-material draft/review/send flow."
---

# Discover demand, then process it once

FIRST read only registered RunSettings and run scan.entry. ScanStopped exits
quietly before any other reads, indexes, logs or business writes. Invalid scope
permits no scan or auto-init. Native wakes load current_rules.py from the actual
installed package and follow [scheduled entry](../../references/scheduled-entry.md)
under scheduled-approved-work. Public run-auto uses one-cycle-approved-work;
explicit no-send restrictions remain. No native management API, unique executor,
bound chat or extra lifecycle proof is required.

Batch phase inputs/checks using [local batches](../../references/local-check-batch.md);
the one result artifact already saves originals, so no separate save/capture.commit
call or unchanged local write. Reuse current task rows to select only changed
or recovery-demanded v4 task details; do not fetch every unchanged consent task.
Use [event discovery](../../references/event-discovery.md) and scan.probe over
current scoped mail, active action submissions, controls, due and recovery.
Complete discovery without executable input exits immediately. Do not load
business procedures or query CRM/Dropbox while idle. Unchanged waits do not
create work; pending source handoffs and due events remain demand even when
no new email is found. Retain complete pagination and partial-coverage reasons.

For actually submitted ordinary/legacy action forms, use local task.submission
once over the current task/action captures to save the request and ReadyToValidate
projection before continuing the owning skill. Do not leave checked submissions
in a needs-input view because the compatibility InputSubmitted field is false.
This is observation only; preserve original approval scope. Same queued input
needs no writes. Close successful original steps in the same outcome phase with
State=Completed and Result, even if the successor awaits review or SMS timing.
Today task_results follows PendingTasks, not WorkflowRuns; never rerun a business
action to fix a stale classification. See [operator experience](../../references/operator-experience.md).

Pass the full saved queue to scan.queue/scan.cycle and apply stops first. New
inquiries use [email-flow](../../references/email-flow.md): read each email once,
match CRM once, resolve cached project material, draft a text/plain message and publish one readable combined
consent view over the original task. Observe v4 Consent/ReviewText changes
with email.consent-observe, without fetching another action page. No HTML/image preview. Ordinary name resolution creates no human task. Add AimoreInquiry after
classification within the saved read scope; it is not an admission requirement.
Reuse original captures across helpers and all newly ready successors. Do not
restart scans, refetch unchanged sources or create plans per logical step.

Process submitted combined approvals and standing-authorized due SMS under
current source/channel/stop/count/attempt controls and SMS-only timing. One customer's block
is scoped to that work. Accepted/pending/unknown effects never replay. Coalesce
own writes and save actual event/backlog/step/wait/block/duration metrics once
at the cycle boundary. No routine Health/report/history sweeps or delivery polls.

Approved mail sends immediately in this cycle. Do not defer to business hours,
weekdays, holidays or legacy email due dates. Recover approved backlog with no
new mail input. Never bypass provider backoff or replay unknown/accepted sends.


Before treating an incomplete SendApprovedReply as waiting/idle, process only
review_publication_task_urls from scan.watches with email.review-repair over
those original captures. A review_publication_only recovery event repairs the
native review, never dispatches. The normal email operator path is exclusively
Today -> read ReviewText -> check Consent -> next scan sends. No Actions or
additional confirmation. Publish the whole review projection at one boundary;
canonical native reviews do not belong in generic waiting/action-link lists.

On an actual failure or changed repair outcome, apply [exception handling](../../references/exception-handling.md). Internal registration, connector and state bugs belong to System Recovery, not an invented human task. Only a specific Operator question/input route enters Today attention. Keep business summaries plain and existing machine evidence in closed maintenance details. Reuse this phase captures; do not rewrite unchanged failures or replay external actions to repair their display.
