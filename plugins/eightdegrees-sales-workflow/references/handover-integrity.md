# Durable intake, current publication and invocation recovery

Use only for an affected phase. These offline guards emit checks/plans, not MCP
interception or proof that a historical action happened in the right order.
Do not sweep every completed record or load this procedure on an idle tick.

## Intake is a separate completed step

Save the original source first. Finish ReadMessageBody on the original scanner
checkpoint with source_key, source-vN, state=completed and receipt_ref pointing
to that exact source page. Save and fetch that checkpoint BEFORE loading sales
preparation, resolving project facts, creating a draft or opening review.
Discovering an email, creating its Inbox row or having a ScanWorkReady result
alone is not the handoff.

Use intake.plan with root_id, current invocation_id, original source_page and checkpoint_page to generate a prospective completed receipt after reading the persisted source. Save its checkpoint on the current intake/scanner run and read it back; must_save_and_read_back is not a completion proof. Identity-less legacy checkpoints need this explicit prospective step, not a rewrite of their old run. Then run `intake.handoff` with original complete source_page and checkpoint_page,
root_id, source_key and source_version. It verifies actual source identity,
installation ancestry and the unique completed intake receipt. Keep the
unchanged source/checkpoint captures in the same local bundle. A failed check
stops the successor and preserves intake recovery; never append a retrospective
checkpoint to claim an earlier preparation passed.

New sales execution.prepare inputs for content, reply-patch and ReviewReplyDraft
include that same object as intake_handoff. Preparation checks it before facts
and freezes its result. New current-version execution.ready refuses a stripped
handoff. A fresh public reply-draft must first persist/register its supplied
source under this intake contract; it cannot fabricate an inbox/checkpoint ID.
Existing frozen pre-upgrade plans remain original evidence, not proof of new
order. Missing old intake needs a prospective intake/recovery phase.

Carry outputs.intake_handoff.source_page_id into every NEW sales-send-package
as source_page_id. This is an original-page pointer, not a replacement source or
an authorization. Exact Notion mutation rejects a new package without it.

## Preserve bindings, patch current sections once

notion.mutation now reconstructs the whole proposed body for a targeted update,
insert or replacement. Missing/ambiguous anchors, duplicate Current status,
Processing result or Your input headings (including localized equivalents),
and removed/rebound action-binding records are refused before returning a call.
Literal code/history is not a second live section. An existing duplicated page
can be repaired atomically to one current section while preserving its binding.
Do not append a second result template. Use the existing exact current anchors.

An independently verified NEW email review version may change its version-bound
binding only when review.prepare/EmailReviewReady matches the new task/version/
draft, stable task/action/owner/route identity is retained, and the old binding
is retained as `{record_type: historical-action-binding, binding: <original>}`.
Otherwise use a separate original version/task. Normal operator checkbox
submissions and closing controls do not require a new approval or release.

After Gmail acceptance, email.presentation-plan synchronizes canonical task
bodies as well as actions. Supply source_page for the exact original incoming
message/thread; new source-bound packages require it. Declare that page as a
publication resource BEFORE preparing the owner plan. Immutable original mail,
fact proposals, approval bindings and payload blocks remain untouched.
verify receives saved_source_page in addition to saved_pages/saved_index_page.
Source Result/current prose reflect the actual handoff; its nonterminal state
becomes Processing for internal closeout, never a repeated approval request.
After EmailPresentationVerified and the owner's full completion contract pass,
prepare/preflight the source_completion marker through owner-write to mark that source
Processed. This final marker is deliberately not a prerequisite of its own
presentation proof. Re-read the final source marker; never replay Gmail.

For a legacy Business run missing SkillVersion/SourceKey, use
run.legacy-projection with its original run_page and exact terminal task_page.
It emits ONLY a canonical-navigation Summary. Pass legacy_task_page to
notion.mutation for this exact generated Summary. It never invents old metadata,
changes State/CurrentStep, clears failure history or repeats an effect. Failed
identity matching remains a linked exception. report-only cannot repair it.

## Retire stale waits without releasing unknown attempts

Use checkpoint.reconcile with the original checkpoint_page, root_id and only
the affected original task_pages. A waiting receipt can become completed or
cancelled only when the same original canonical task, step, version and source/
TaskId are terminal. Preserve the old checkpoint; persist the returned value in
the current scanner checkpoint. Unknown entries, AttemptIds, provider attempts,
other versions and customer restrictions are unchanged. scan.cycle accepts the
same captures as terminal_task_pages, dropping those terminal identities from
current work rather than re-running an old approval.
An event is acknowledged only after this result and next wake-up are durable.

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

## Keep closeout short

Use one original capture per connector response and pass files/capture names to
local_checks. Do not retype CRM history or split the same JSON into dozens of
model-generated shell fragments. Persist required evidence, CRM readback,
canonical status and next-wake registration once; defer optional history/Health
presentation to the scan boundary. Select the next fitting event immediately.
No outgoing status, Sent MIME or handset confirmation is added by these fixes.
Live forward ordering, compaction recovery and cloud execution need another
target-host test; offline results cannot certify unattended operation.
