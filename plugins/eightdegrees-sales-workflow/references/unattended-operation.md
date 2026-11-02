# Unattended approved-work operation

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

The operator reviews business facts and email sends in Notion. Native ticks do
all eligible continuation, source scanning, factual SMS, due internal work and
result repair without another chat command. A human decision blocks its item,
not the installation. Never replace an unknown result with a new send or turn
missing capability into a repeated permission question.

## Bounded scan and durable restart

Use local_checks operation scan.cycle with one original capture bundle. Inputs:
root_id, actual started_at/now, executor={current_id,active_ids,coverage_complete,
serialized}, current items and streams, optional checkpoint_page, results and
attempted_keys; optional budget_seconds/reserve_seconds/max_items come from
the current saved queue_execution settings, not a host interval. Work items have source_key, step, version, input_digest and optional
attempt_id, unknown_attempt, waiting, stopped, due_at, priority. Source stream
observations have cutoff, complete, durable and actual next_cursor. Result
observations have key, state (completed/unknown/waiting/retry_read), receipt_ref
and original attempt_id for unknown results. Normalize these only from actual
owner evidence; the planner cannot prove results or permission.

Defaults: 900 seconds, 120 seconds reserved for persistence, 12 owner steps.
The nominal reserve may absorb at most15s of phase-estimate slack, retaining
at least30s; no new admission after minute13 or with less than30s work time.
Use the exact scan.cycle result; dispatch still has all fresh guards. See
[short handovers](scan-fast-path.md) for priority and fitting-item behavior.
Recheck actual clock and the plan before every discovery page/body, owner step and external effect. Stop
admitting work at 13 minutes; save coverage and remaining identities. Never sleep
for future work or spin on unchanged human input. Do not interrupt an in-flight
write to fit the budget: finish its result recording, admit no more work and
let the next tick resume. A single long provider call can overrun this soft
budget; record that actual overrun rather than inventing a hard timeout.
The 120-second reserve is inside the 900-second total, not an extra two minutes.
Supported explicit budgets remain 120-900 seconds; preserve older saved
480/60 limits until the operator deliberately adopts new defaults.
Use elapsed_seconds, budget_seconds, publication_reserve_seconds, timing_status
and soft_budget_overrun_seconds from each current scan.cycle observation.
An overrun is a performance/quality observation, not proof that a verified
email/SMS failed; retain independent business outcomes and exact historical
limits. Do not rewrite earlier 480-second overruns as passed under the new limit.
Default ticks are 30 minutes, optionally 20; the 15-minute budget leaves headroom
in both modes, but does not prove native serialization or prevent an in-flight
provider call from taking longer. Existing overlap/unknown guards still apply.

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
Supply those observations to scan.cycle. Native scheduling retains this strict host-level evidence requirement. ScanDeferred has no executable work;
do not treat its successful local validation as permission to run an owner.
For native cycles, missing activity coverage, another active executor or an unverified serialized
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

Apply [event discovery](event-discovery.md) before business plans or validation.
Use scan.probe over actual scoped changes, registered action inputs, controls,
due indexes and recovery pointers. ScanIdle ends this tick immediately. An
unchanged empty tick has no owner calls, business checks, CRM/source-content/
preview reads, full setup reconstruction, completed-history sweep or routine
Health/report/projection writes. Persist only a changed compact event index and
an optional actual discovery heartbeat; no operator notification.

ScanWorkReady selects affected owners via scan.cycle. Fresh approval/stop/
version/attempt checks apply just before actual dependent effects, rather than
revalidating all waiting tasks each tick. A changed form still needs its actual
submission; due work is input even without new mail. Preserve pending keys and
registered wake-up pointers across crashes. A missing feed is partial coverage,
not an idle result; retry only that feed within budget.

Notify only newly actionable decisions, meaningful completion/failure, new
capability loss or configured important reminders. Reuse the original task link
and deduplicate reason/version. A successful provider acknowledgement closes
our dispatch without an external status watcher. Unknown results retain their
original attempt and wake only on new evidence or a saved bounded recovery
trigger; no blind resend, repeated approval prompt or busy poll.

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
A successful original request acknowledgement completes our dispatch, including
AwaitingPhone/PendingApproval. Recover from the saved response, not another
provider query. Close our task/run and finalize its one count; raw external
status is metadata. Only an unacknowledged Unknown remains unresolved. Never
reset attempts/counts, reopen stopped cycles or infer network timestamps.

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

## Explicitly bound on-demand conversation

A public run-auto need not prove cloud scheduler serialization when no native
schedule exists and the operator has designated one current conversation for
on-demand work. This is the same manual workflow, not a native scheduling test.
Pass policy=one-cycle-approved-work or one-cycle-no-customer-send to scan.cycle.
Normalize executor.on_demand from original observations: operator_assigned,
settings_read_verified, runs_read_complete, registered_thread_id,
current_thread_id/current_thread_status, current_turn_id/current_turn_status,
root_id, scheduler_enabled, scheduler_state, schedule_ids,
schedule_pending_attempt and other_active_scan_ids. Actual thread status is
active and turn is inProgress; the current turn must equal executor.current_id.
The registered and actual thread IDs must match. Scheduling must be disabled,
Stopped, have no IDs or pending attempt. Read the complete installation Scan
view; another active Scan blocks execution. Waiting human business children and
this control/testing conversation are not additional scan executors.

Save queue_execution.on_demand_executor_thread_id only on explicit init selection
of the actual on-demand conversation; resolve it from runtime evidence, not a
customer document or guessed ID. Preserve old submitted reviews/attempts. A new
conversation cannot inherit the binding; explicit init rebind checks that the
old executor is not active and reconciles unresolved attempts first. Re-read the
same binding and scan activity before dependent effects. Do not compare all
unrelated host chats as if they were this installation's workers.

The planner reports execution_basis=BoundOnDemand and grants no send authority.
This basis never satisfies scheduled-approved-work or Work/Cowork readiness.
Unbound/mismatched turns, partial installation activity, another active scan,
a live/unknown scheduler or missing original settings still defer. The existing
approval/stop/attempt rules remain; no per-message bypass or extra continue
command is introduced. Host-wide/native serialization flags remain unverified.

## Admission and compact phase checkpoints

Each scan.cycle result admits only ONE owner. It returns
admission_required_before_next_owner and seconds_available_for_work. Supply an
estimated_seconds phase cost (default90); no phase is admitted unless it fits
budget minus reserve. This is admission control, not a hard provider timeout.
Do not skip a pending stop/reconciliation merely to fit a cheaper send.

ReadMessageBody has source priority2; optional RecordMaterialHandoff,
RefreshEmailOutcome and RefreshSmsOutcome priority4. Required immediate result
recording still belongs to the in-flight effect; later independent maintenance
must not starve source intake. Save compact pointers/check results instead of
copying HTML/MIME or the whole original plan into every progress update.
Apply one frozen owner registry per phase; run local checks in one batch over
unchanged original captures. Keep all required fresh pre-send and saved-result
reads. Record actual overrun, never raise limits to hide it.

Completion receipts retain source/step/version identities so a rebuilt stale
digest cannot requeue the same completed version. Unknown source/step attempts
block changed input/version candidates and remain reconcile-only.
