# Unattended approved-work operation

The operator reviews business facts and email sends in Notion. Native ticks do
all eligible continuation, source scanning, factual SMS, due internal work and
result repair without another chat command. A human decision blocks its item,
not the installation. Never replace an unknown result with a new send or turn
missing capability into a repeated permission question.

## Bounded scan and durable restart

Use local_checks operation scan.cycle with one original capture bundle. Inputs:
root_id, actual started_at/now, executor={current_id,active_ids,coverage_complete,
serialized}, current items and streams, optional checkpoint_page, results and
attempted_keys. Work items have source_key, step, version, input_digest and optional
attempt_id, unknown_attempt, waiting, stopped, due_at, priority. Source stream
observations have cutoff, complete, durable and actual next_cursor. Result
observations have key, state (completed/unknown/waiting/retry_read), receipt_ref
and original attempt_id for unknown results. Normalize these only from actual
owner evidence; the planner cannot prove results or permission.

Defaults: 480 seconds, 60 seconds reserved for persistence, 12 owner steps.
Recheck actual clock and the plan before every discovery page/body, owner step and external effect. Stop
admitting work at 7 minutes; save coverage and remaining identities. Never sleep
for future work or spin on unchanged human input. Do not interrupt an in-flight
write to fit the budget: finish its result recording, admit no more work and
let the next tick resume. A single long provider call can overrun this soft
budget; record that actual overrun rather than inventing a hard timeout.

Persist the returned scan-checkpoint-v1 on the original scan before advancing
source labels/watermarks. Keep an installation pointer to this actual scan.
Read that capture next cycle. Persist provider AttemptId before dispatch and its
raw result immediately after; publish result/projections separately. A crash
between dispatch and result saving is Unknown, even if the old item looks ready.
Reconcile the same provider/request ID or exact stored email before deciding any
retry. Saved completion receipts suppress already finished step keys. Rebuilt
candidate rows cannot override durable unknown/completed evidence. A changed
approved version has a distinct key but never bypasses an old unresolved attempt.

Store only work identities, due/wait states and receipt pointers in checkpoint;
no HTML/base64, customer body copies or cached authority. Fresh original
approvals, stop/replies, sources, versions, counts and attempts still gate each
external action. Incomplete/unsaved source pages cannot advance a watermark.
Resume actual pagination cursors where supported, otherwise repeat the same
scope with source-ID deduplication; do not mark partial coverage complete. Use
a small overlap when providers round timestamps, and scan scoped reply/stop
changes separately from a new-mail watermark. Previously scanned messages can
still receive new replies. Check current submitted action pages even when their
database row was unchanged.

## One executor, not an expiring Notion lock

Keep one native task per customer root. At start verify actual host serialization
or equivalent non-overlap evidence and save the method/provider evidence. At each
tick read actual executor activity, including prior native and manual runs.
Supply those observations to scan.cycle. ScanDeferred has no executable work;
do not treat its successful local validation as permission to run an owner.
Missing activity coverage, another active executor or an unverified serialized
host blocks new business effects. Read-only diagnosis and stop observation may
continue. A lease timestamp or old WaitingForOperator business child is not
proof of a live scan, nor proof that a prior scan has terminated.

Never expire a lease and silently take over an unresolved external attempt.
Confirm the actual previous executor is stopped/finished, reconcile its attempts,
then resume original steps. Native retries use the same durable attempts. Check
schedule generation/revocation before effects under the existing lifecycle.
Notion has no atomic compare-and-swap; these offline plans are not a distributed
lock. If the host cannot establish single ownership, mark unattended readiness
incomplete instead of enabling two workers. Manual run-auto while a native cycle
is active defers; it must not create a second worker.

## Short idle ticks and notification policy

Reuse registered view IDs and known quota fallback. Read each affected page once
per unchanged phase; local checks use capture references and --output. Do not
copy raw captures into many command arguments or repeat full owner plans for
progress writes. Do not read all completed history, regenerate unchanged previews,
write unchanged results, or rebuild the daily brief on every tick. Scan ready
work first, then targeted presentation repair and due daily brief. Save missed
work for the next tick without another native job or chat prompt.

An unchanged empty scan may save one compact checkpoint/heartbeat needed for
health; do not notify the operator. Notify only newly actionable decisions,
meaningful completion/failure, new capability loss or configured important
reminders. Reuse the original task/action link and deduplicate the reason/version.
Pending gateway execution is machine waiting, not an approval task. Unknown
send results are reconciled read-only on later ticks; do not repeatedly prompt
for approval. An actual unresolvable failure stays one linked exception while
unrelated eligible work continues.

## Restriction and SMS projection maintenance

Observe customer stop before draft/fact review. Stop the current affected cycle
immediately, then use contact.restriction-plan and contact.restriction-verify to
insert an append-only restriction overlay above the approved persona. Use actual
cycle_page, send_task, persona_page, message, stop_quote, explicit_stop=true,
scope_confirmed=current_enquiry and observed_at. The helper binds the direct
source sender/thread to the original inquiry package and customer. Ambiguous
scope blocks affected sending and produces one matching/clarification task;
it cannot authorize global DND or an automatic re-enable. Existing approved
persona bytes remain history. stop-<source-message-id> is the maintenance version.
Use contact.dispatch-gate with actual current cycle/restrictions/client/context
before SMS, in addition to standing authority and other send checks. No customer
reply may auto-enable a previously stopped cycle. CRM Notes still need review.

RefreshSmsOutcome is Notion-only maintenance under the original SMS owner.
Supply sms.presentation-plan all original pages under roles notification,
result, data_task, data_action, data_run, send_run, cycle, plus raw provider_status
and observed_at; maintenance_task_id must be a distinct registered task. This
binds original payload, request receipt, cycle, task/actions and parent run IDs.
Update current results on all seven pages, not a new reconciliation run alone.
Pending stays machine InProgress; network-send closes the original dispatch
operation, not the overall follow-up cycle or delivery. Failed is Error, unknown
reserves its slot, and stopped cycles remain stopped. Never reset counts or
invent actual network-send timestamps from query time.

Every planned write passes ordinary exact-call and owner scope preflight. Read
back the affected originals and run sms.presentation-verify. Freeze kind
sms-presentation on the maintenance task, and contact-restriction for persona
maintenance; missing saved projections prevent maintenance completion. These
helpers have no connector, approval, send or CRM capability. Native SMS reply
visibility and host task uptime remain actual capability constraints.

## Required acceptance

Exercise five scheduled-equivalent cycles with completed receipts, a restart
before result publication, an unknown provider request, future due work, a human
wait, a customer scope-specific stop, a long cycle and a concurrent tick. Assert
one original request/CRM append, no re-enable, no second worker, no lost cursor,
no unchanged projection writes and zero business writes from report. Then test
actual native start/ticks/stop/restart with real host run IDs, phone/network and
cloud connector access. Local replay cannot certify host serialization, timing,
message delivery or Claude Cowork runtime.
