# Durable progress and recovery

Save/reuse the original source and keep its immutable source key/message ID.
Successful API response and source ID permit immediate draft preparation. Save
one successor review/data/timer pointer before acknowledging its event. If a
crash leaves a source without a successor, recover that original source once;
never recreate it or require another user continue command. Normal mail follows
[email-flow](email-flow.md), without a separate saved intake plan/readback stage.

Keep one current status/input/result section, original bindings, user answers,
children and historical approvals. Patch only the owned affected content.
Unknown or accepted external attempts survive compaction and application restart.

## Resume this command after compaction

Pin the selected public command, effective policy, explicit user restrictions
and original start time locally. invocation.prepare accepts command, root_id,
started_at, budget_seconds, policy, restrictions and receipt_page_ids. It creates
a local run UUID when invocation_id is omitted. Save that returned record before
dependent work; the label is logging/recovery context, not a unique executor.
executor_id and native host/thread/turn IDs are optional diagnostics only. Do not
request privileged execution metadata or register a sole conversation.

After compaction read the original context_page or context_record and call
invocation.resume with the original command, root_id, started_at, now, policy/
restrictions and retained local invocation_id when available. Keep the original
run label/deadline/receipt pointers; a different executor_id is not a refusal.
Wrong command/root/local run label, changed policy/start/deadline or clock
regression still refuses. Exact page mutations preserve the pin; only receipt
pointers may be appended. No native identity proof is required.
A legacy run-auto pin without effective-restriction metadata is closeout-only
and no-send; do not reconstruct permission from commands.json after compaction.
Budget expiration permits closeout only; never reset the start, create another
public invocation, restart the rehearsal, message a peer or act as its test
controller. Resume the current owner using original receipts and fresh guards.
The pin grants no approval and caches no send permission. New invocations use
normal event discovery/reconciliation, never impersonate the old invocation.

## Short closeout

Reuse original captures in local_checks --output; print only useful summaries.
Persist actual results and next pointers once, using API acknowledgements for
Notion/CRM. Continue the next fitting event; no outgoing status or delivery polls.
