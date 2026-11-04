# Exceptions are not automatically operator tasks

Keep one original PendingTasks record, Category=ExecutionExceptions, and its true
state, attempts and provider results. Add ResolutionOwner (text: System or
Operator). RequiredInputs holds the specific business question only when the
operator actually needs to decide or supply something.

System covers connector failures, missing internal checkpoints, search coverage,
association/cycle bugs, stale system metadata and projection errors. Show these
in Dashboard / System Recovery, never Needs my attention or a human waiting list.
Unclassified/incomplete requests remain visible in maintenance until classified;
do not invent a user question, silently complete them, retry an accepted send or
poll unchanged failures every cycle. Preserve metrics and deduplicated failure
tracking; only relevant dependency/version changes or an authorized repair resume
that original work.

Operator requires a specific, answerable question and the original working input
route: for example, which recipient to use, a missing project document, or a real
reauthorization action. Say what happened, what is affected, exactly what to
fill/select and what happens after submission. Never ask users to diagnose an
exception code, find a TaskId, prove a search complete or repair internal state.

## Business display and evidence

Use local exception.presentation with original task, optional registered read-only
action page, resolution_owner, problem, impact, next_step, language and optional
question. It returns presentation writes only; it never sends or closes failed
business work. An Operator form is preserved. A System result has a plain summary
and explicit No action required; existing machine payloads/history remain in one
closed native toggle labelled System maintenance records. Bindings and original
recovery payload bytes remain readable to helpers. Preserve child records and
all operator controls; adapt them explicitly instead of hiding a real form.

Do not place JSON, internal IDs, hashes, stack traces or raw helper results before
the user's controls or in their routine status text. New ordinary action pages
contain business text/inputs only; machine evidence belongs to the canonical
workflow record or Dashboard diagnostics. Legacy frozen bindings may stay in a
closed maintenance toggle until a supported migration; do not break old approval
or restart evidence to beautify a page. Collapse is presentation, not access control.

## Setup and publication

operator.system-view plans only missing ResolutionOwner DDL and one linked view
over the original PendingTasks on the registered Dashboard. Reuse the registered
operator_experience.system_recovery_view_id; discover/reconcile it before create.
Register exception_contract=operator-exceptions-v1. The view includes system and
unclassified exceptions. Today attention requires ResolutionOwner=Operator,
nonempty RequiredInputs and ActionPageURL; the generic waiting list excludes
system exceptions. Never replace the scanner's complete execution-discovery views.

Apply this classification/display on a new failure or changed repair outcome,
using already captured data and original API acknowledgements. Unchanged copy
produces no writes. Resolving a display issue does not resolve its business fault.
Keep email's Today -> read reply -> Consent -> next scan journey unchanged.
