# Discover events before running business work

FIRST read only RunSettings and call scan.entry. ScanStopped exits quietly
without discovery/task/source reads, indexes, run/log/Health/Today writes or
notifications. ScanControlUnknown also permits no work. Only ScanEnabled enters
the procedure below. Exclude scan_control and legacy scheduler lifecycle flags
from the authorized scope digest so stop/start preserves existing cursors.

run-auto has two stages: lightweight discovery, then affected owner work. A native
30-minute tick (20 optional) discovers inputs; it is not itself a business event.
There is no new service, webhook deployment, public command or busy-wait loop.

Follow [the short scan procedure](scan-fast-path.md) for active dependency/form
watches, original error capture and bounded handover. No owner procedure loads
until scan.probe actually returns ScanWorkReady.

## Discovery first

Read the registered installation/settings binding, compact scan-event-index-v1,
source cursors and active dependency/action/due indexes. Resolve the compact
Dashboard/EventIndex by queue_execution.event_index_page_id. Do this BEFORE loading
owner procedures, creating full execution plans, reading CRM, opening Dropbox
files, decoding mail bodies, validating previews or rebuilding dashboards.
Use actual connector capabilities: scoped Gmail message/thread ID changes;
registered action-page input changes; Pause/Cancel/settings changes; due work,
reminders and confirmed appointment changes; explicitly pending recovery.
Add project/Calendar/SMS-reply feeds only where configured and relevant. An
unconnected optional channel is not covered and cannot be claimed as monitored.

Reuse native v4 Consent/ReviewText row projections through scan.watches and
its consent_row_records; fetch only changed/demanded task details. Do not emit
duplicate row/full-page triggers. Legacy forms still need their current input.
Prefer supported incremental queries and metadata/version observations. If a
connector cannot list action-page revisions, fetch only registered active forms
once and locally digest binding, answers, intent and submission state. A task
row timestamp or InputSubmitted projection cannot substitute for that check.
Unsubmitted edits update the discovery fingerprint but enqueue no execution.
Workflow status/log edits are not human input. A newly submitted choice or
withdrawal is an event; a timestamp alone is not approval. After discovery the
owner still validates exact input and persists its accepted snapshot.

Mailbox discovery must include new replies to existing threads, with the saved
scope/exclusions and a timestamp overlap where needed. A label count alone does
not prove no input. Do not fetch every old message or closed outgoing status.
Dropbox discovery uses metadata/version changes for registered active project
dependencies; read content only when changed or required by actual execution.
Future due items stay indexed: the clock reaching due_at is an event even when
no source revision changed. Waiting human tasks are not periodically re-inferred.
Unknown attempts wake on actual new evidence, an operator submission or a saved
bounded recovery time; never treat every tick as a new send/retry opportunity.
Successful Gmail/AndroidSync handoffs have no external status/delivery watcher.

## Local scan.probe contract

Use local_checks.py operation scan.probe with root_id, now, scope_sha256,
required_feeds, observations and optional index_page/acknowledgements. The scope
digest binds stable authorized scope and registered feed definitions (accounts,
labels, views, work folders and configuration), excluding cursors, timestamps,
results and changing task lists. index_page is the original saved page containing exactly one
scan-event-index-v1 fenced JSON record; never fabricate a prior empty index.
No index requires complete initial snapshots of registered feeds. An absent
index is not evidence that the mailbox or human queue is empty.

Always declare mail, actions, control, scheduled and recovery. An empty feed
means its actual registered set was checked, not that its query was omitted.
Each observation has mode=snapshot|delta, complete, observed_at, records and
optional from_cursor/next_cursor/page_cursor. Deltas require the exact saved cursor; an
expired/mismatched cursor requests targeted feed recovery, not an empty result.
Incomplete pagination cannot advance the committed cursor or justify idle.
The proposal retains resume_cursor separately; continue it as page_cursor in the
next request. Complete snapshots retain fingerprints from all saved pages.

Each record has original id, stable revision and events. Normalize these only
from original captures. Each event has kind (mail/stop/submission/control/source/
timer/recovery), evidence_ref, source_key, step, version, input_digest and optional
due_at. These are work pointers, never content copies or cached permissions.
Timer events require due_at and a business occurrence identity (such as the
dated brief or original due-notification task), not just a template version. Include waiting forms with events=[] until actually
submitted, and future clock events with their due time. Revision changes may
enqueue several affected work keys; owner routing still uses the saved route.

For a failed feed call, normalize its original response captured in the phase batch or
explicit exception with connector.capture. Supply that exact result in the
observation's failure field and complete=false. scan.probe rejects a fabricated
diagnostic or failure declared complete; candidate_index retains last_failure's
capture reference/digest/inspection. A later complete observation adds one
recovered_at without erasing the original failure. Pagination without a call
failure remains distinct; never invent HTTP status, quota cause or retry time.

Results:

- ScanIdle: all declared discovery coverage is complete, no ready events. END
  this invocation immediately after necessary compact index persistence. No
  business inference, owner preflight, CRM/source/preview revalidation, result
  sweep, routine report/Health rewrite or operator notification. A tiny optional
  heartbeat records actual probe duration/coverage only. Existing Today links
  can be returned without rereading/rebuilding the page.
- ScanWorkReady: persist candidate_index and confirm its API response if changed, retain current task state
  and a local log label, then use scan.cycle for affected events only. Process stop
  events first; unfinished related successors may run in the same bounded cycle.
  Missing discovery coverage still blocks affected sends through fresh guards.
- ScanDiscoveryRequired: coverage/configuration/cursor needs attention. Retry
  only the missing feed within budget; otherwise save partial coverage and the
  original backlog. Do not call this idle, loop through owners or rebuild setup.

The helper never performs I/O or grants send authority. Pass exit 0 AND the
explicit status; LocalChecksPassed alone is not ScanIdle or a dispatch permit.
Persist candidate_index and confirm its successful API response BEFORE committing source
labels/cursors. The proposal is not a saved checkpoint. Pending events survive
even if the source later vanishes or a discovery cursor advances.

After a durable owner result, acknowledge its event key with state=completed or
waiting and receipt_ref. waiting additionally needs wake_ref pointing to the
registered next form/timer/recovery item. Mere discovery is not completion.
Never acknowledge an unknown effect as completed, or drop an unfinished event
to obtain a quiet scan. A crash before index save replays discovery safely; a
crash after save retains pending keys. Existing step/attempt deduplication still
prevents replaying a successful effect. Commit next-step wake-up registration
with the owner result before consuming its trigger.

This reduces repeated reasoning and business checks. Connector reads and the
model invocation still have costs; polling is not push and offline tests do not
prove a specific live time/token saving. Record discovery vs processing time,
event count and owner steps separately in the next live test.

## Baseline and durable backlog recovery

scan.probe computes baseline Complete/NeedsBaseline from actual current coverage. Persist that projection with its index only when changed and update a changed corresponding settings projection without clearing queues, cursors or attempts. A scope change retains pending/handled identities and requires real snapshots; a failed feed gets exact recovery_actions. Even unchanged snapshots must return original pending ready events. Use backlog.recover before interpreting an already saved ReadMessageBody as a completed source-to-owner handoff. Missing source handoff uses RecoverSourceHandoff, not a repeated source creation. See [scheduled entry](scheduled-entry.md) for the ordered continuation and metrics.

Use scan.watches.ready_task_records/ready_task_blocks as scan.probe supplementation before claiming idle. After saved discovery, scan.queue constructs the full work set from the original EventIndex and current task/source captures; pass its full result as queue_plan to every scan.cycle. The planner adds omitted fitting work without another scheduler/identity requirement. Keep all remaining pointers across owners and restarts. A subset containing only current draft preparation cannot represent all pending mail/due work. No send or factual approval is synthesized by queue construction.
