# 0.1.10 Dedicated operator input and review pages

PendingTasks exposed a long technical-property panel before the editable task form. Operators could not readily identify what to fill or select. Keep that database as canonical execution detail and introduce ordinary task-specific action pages under Aimore/Actions. Those pages have only a title property, a short business summary, direct review/preview links, relevant native input/decision controls and a named submission to-do. Technical IDs, actor fields, version binding and execution logs stay on the original task.

Cover all five categories with different input/decision semantics. ContentReview and SendApproval use separate version-bound pages; a new content version gets blank decisions. Receipt acknowledgement closes only reminder chasing. Active ordinary-page links are the human entry from the hub, views, reports and permitted notifications; do not claim native database-card click targets changed. Closed/superseded pages show no active submission controls.

Register ActionPageURL/ActionFormVersion and original task/step/content/digest binding. Save observed input/decision snapshots before canonical projections and dependent work; reread both original records before external actions. Repeated accepted snapshots cannot duplicate provider writes. Preserve input on correction, distinguish consumed submission from withdrawal, and repair partial presentation without reexecuting business actions. Manual work still requires explicit continuation; command send/report/scheduling boundaries are unchanged.

New DataCompletion uses task-input-v2 with task-action-v1. Explicit init upgrade preserves task/page/run IDs, answers, decisions and Mode while creating eligible action pages. In-flight/unresolved legacy submissions retain one original input authority until reconciled; migration itself does not submit or execute. Do not delete old properties, create another response database, install a Portal or claim custom radio/button widgets.

Validation: both marketplace/reference/skill/package checks, shared-payload parity and archive inspection; retained helper tests run in CI. No helper runtime code changed. Live Notion visual/keyboard checks, action submission/decision consumption, stale-page rejection and migration acceptance remain in the designated test session. Current test resources are not changed by packaging.

## Design rationale


- User/job/outcome: a configured operator opens one task, supplies its few missing answers or one specific decision, and sees whether it was recorded. Consequence: only existing authorized workflows may act; no change to approval scope, execution mode or external sending permission.
- `rule/smallest-intervention`, `rule/one-primary-action`: use one ordinary input page per active task/version, retaining the existing execution database and category views.
- `rule/name-object-scope-consequence`, `rule/irreversible-action-safeguard`: separate supplied facts, content confirmation, send approval and receipt acknowledgement with explicit effects.
- `rule/preserve-user-input`, `rule/no-redundant-entry`, `rule/cover-reachable-states`: preserve answers through validation, stale versions, permission/preview failures, partial saves and completion.
- Coverage gap (proposed) `rule/notion-exclusive-todos`: the current native-page tool surface lacks radio groups; visible to-dos plus strict single-selection validation are the supported fallback. Host visual/keyboard behavior and real workflow consumption still need designated-session acceptance; package validation does not prove them.
