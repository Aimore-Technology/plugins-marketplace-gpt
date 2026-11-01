# Owner completion contract

Apply to all eight workflow owners, including initialization, communication, persona, scanning, sales reply, SMS, daily brief and automation control. This is a local evidence/preflight contract, not an independent backend or host-enforced interceptor. The command policy and ordinary approval/attempt rules remain in force.

Every proposed Notion page call also passes [exact-call preflight](notion-mutation.md)
before execution, including initial creation and nonfinal metadata. Completion
evidence and a correct target do not replace current body/property checks.

## Begin, bind, check, then finish

At owner entry, use [execution preflight](execution-preflight.md) prepare/ready instead of hand-building the required checks. Persist an invocation-specific completion plan in its own WorkflowRuns body/log BEFORE dependent business work. Use [owner-completion-profiles.json](owner-completion-profiles.json) for minimum check kinds. Record intended resource roles and known IDs, immutable task/content versions, invocation policy and required checks. Bind newly returned page IDs by an appended creation/result event before input consumption; do not drop required roles or fabricate a previously frozen plan after completion. The contract is workflow-owned evidence, not new operator form properties.

1. Verify planned task owner/category/resume metadata, create the canonical task, then run resume-task --phase register against that ORIGINAL record with the actual policy and PageId before enabling its form. ValidResumeRoute checks metadata only and does not require a fictitious Manual continuation. Run the normal execute/observe phase again before consuming input; add --explicit-continue only for a genuine requested Manual continuation. CompleteCommunicationData is distinct from ReviewCommunication. Retain the pre-execution route evidence; terminal Deferred is not a replacement. Only named unfinished work proceeds.
2. Persist accepted input/AttemptId and actual provider result/readback as already required. Missing publication evidence never repeats that external action. Keep canonical task/run/source identifiers, inherited mode/scope and approval history.
3. Prepare and verify current task/action/result/hub publication against the same version. Use typed page-links for original run/task/publication pages, task-display for each changed active action and its actual canonical task, and original route results for the named tasks. Include exact stored reply-draft verification for an email send. Required manual business predicates/provider reconciliation remain separately recorded, not manufactured helper successes.
4. Run completion-gate with actual integer exits/results and the frozen current contract. Before any final Completed or final Success write, run notion_checks.py owner-write with that SAME registry, proposed actual Notion call and full completion input. It recomputes the gate, checks profile and target coverage, task versions, action-to-task bindings, route owner/policy and email transport evidence. Missing/stale/failed evidence yields Deferred. report-only uses report-write instead; do not choose another owner/policy to obtain a pass.
5. Write only the allowed original final state/event and read back the affected result. Finish final projections/consistency checks before returning links; preserve a partial-publication finding if saving fails. Step-level completion may precede a waiting next review, but does not complete that next task or prove delivery. Final run/publication Success needs its own current post-transition evidence. Read-only repeat returns prior provider/results; it does not fabricate a new completion contract for the old business attempt.

## owner-write inputs

`registry` contains owner_skill, actual policy, invocation_id, publication_version, run_page_ids, task_page_ids, action_page_ids, publication_page_ids and operation_log_source_ids. Record only this owner's affected records; a parent wrapper does not own every child completion. task_versions maps each actual task page ID to its current ContentVersion. action_bindings maps each current action page ID to that original task page ID. required_checks is the same named kind/target mapping used by completion-gate. The supplied completion object must match that frozen mapping exactly.

Use `call` with the actual tool name and args. This helper supports final property updates on registered records and final log appends under the registered OperationLogs source. It is not a general provider/Notion action dispatcher. Plain in-progress writes still use actual schema/connector checks; Supported target alone is not approval. The helper never sends or mutates anything.

Required coverage: page-links on original owner runs, tasks and publication pages; task-display on registered actions; route on each named task, matching owner/policy/ContentVersion; the profile's minimum kinds. task-display input includes the canonical task's PageId and ActionPageURL. Email send routes additionally require phase=draft StoredReplyVerified bound to that task/version AND phase=sent raw MIME proof before final send completion. A provider acceptance with missing/mismatched sent proof remains a partial/quality result, never a resend. Existing route observations and sent-message checks cannot replace an executing route or pre-send draft proof. A no-send command's Deferred send route cannot satisfy final send-completion evidence.

For normal downstream persona work, return per-step evidence to the communication owner, which owns the parent completion; do not mark its parent run complete from a child. A persona exception can close only its own registered task with its own evidence. Scanner completion applies to one scan, not waiting child tasks; SMS network acceptance is distinct from delivery/cycle completion. Initialization has only setup/readiness checks and never uses this contract to run business acceptance.

## Recovery and audit

If an earlier run skipped its contract/gate, retain that failure and append a correction. Existing actual Notes/sent messages remain real results; do not rewind/reexecute them or invent earlier check timestamps. Recover only unfinished projections/new authorized work with current contracts. In acceptance, verify actual tool order and the original persisted plan, not merely an eventual EligibleForCompletion JSON object. These guards improve the executable preflight available to the model; actual live owner behavior remains a separate test.

## Focused evidence and read cost

Freeze only affected dependency roles. Unchanged installation roots, templates,
other clients, unrelated Health rows and other owners' action pages are not
publication targets just because their IDs are in settings. Reuse one successful
capture per unchanged page/version within the same verification phase; run local
checks over that capture instead of refetching for each helper. Invalidate it
when a relevant write, human edit, version change or new decision is observed.
The original task/active approval and latest stop/attempt/source evidence still
need the required fresh read immediately before external action. After writing,
read affected saved results before completion; after a final transition, refresh
only changed surfaces and their dependent evidence. Keep actual tool order and
preserve failures. Never reuse evidence across invocations or omit a required
check to reduce latency. Record actual duration/calls; no unmeasured speed claim.

Automation control owns only its schedule/settings/run/log projections, with no
business task dispatch. Verify native schedule results separately under
[scheduling](scheduling.md); local completion checks are not native task evidence.

## Scheduled scope and actual send-result completion

For scheduled-approved-work, bind registry.operator_id and the current actual
registry.schedule_guard. Pass that same guard to route checks. A textual policy
name cannot supply native lifecycle evidence. Every dependent mutation still needs fresh owner/stop/attempt checks and the relevant email approval or standing SMS authority.

SendApprovedReply/SendGeneralReply require an outcome check from outcome_checks.py
verify and a crm-receipt check from send_receipt.py verify, bound to the original
task and content version, in addition to pre-send draft and actual Sent MIME.
Legacy SendApprovedSms requires the outcome check; new SendNotificationSms requires standing sms-authority plus the matching actual request outcome, without per-message review. RecordSendReceipt/RecordGeneralSendReceipt
require receipt and current outcome readback but never reruns sending. Freeze
these kinds in the original required_checks mapping. Missing result projections
or CRM receipt keeps overall publication partial while provider Sent remains
durable. Repair that scope only. These helpers are offline checks, not a server
interceptor, native scheduler or permission source.

With [Today linked views](operator-experience.md) verified, only changed task/action/source projections belong in this owner plan; unchanged Today/Actions pages and view discovery are not repeated publication targets. Use [local check batches](local-check-batch.md) over original captures, keeping each named result/exit in the same frozen completion evidence.

## Material send downstream evidence

A sales-reply actual material send plan must include evidence=material-handoff on its original email task, in addition to reply-draft/reply-sent/outcome/CRM receipt evidence. Verify the persisted original email and cycle through [material handoff](material-handoff.md); freeze MaterialHandoffVerified before final send-owner completion. Notion registration may be Blocked/Stopped without SMS dispatch; that is an honest handoff result. A verified nonmaterial reply records NotApplicable on its email task without creating a cycle. Missing registration leaves the email Sent but downstream handoff pending, recovered through RecordMaterialHandoff without another send. The owner-write guard rejects a sales send completion with reply-sent evidence but no material-handoff check.

## Linked email presentation completion

SendApprovedReply and RefreshEmailOutcome additionally require
email-presentation=EmailPresentationVerified on their own task/version; all four
linked projection pages must be registered in the owner scope, plus the settings
index when it embeds this outcome. Initial sending
binds the presentation to the same actual sent message. Maintenance uses a distinct
task and keeps the original completed send/review immutable except current Result
text/outcome sections. See [email presentation](email-presentation.md). It never
supplies a provider/CRM replay, new approval or SMS permission.

## Standing-authorized notification completion

SendNotificationSms requires kind=sms-authority (SMSNotificationVerified) on the original task/version, plus the current channel-local outcome with the SHA-256 of the actual provider request body. They must match. It does not require per-message ContentReview/SendApproval. Preserve provider IDs and unknown reservations on failure. Use a read-only result page for the existing action-result projection, without any decision controls. See [SMS notifications](sms-notifications.md).

RefreshSmsOutcome requires kind=sms-presentation with all seven saved related page IDs in the owner scope, matched notification version and original message. RefreshContactRestrictions requires kind=contact-restriction with the saved persona page and stop-<source-message-id> version. Use [unattended operation](unattended-operation.md). Their original SMS run status may be an owned publication projection; only one current maintenance run is the executor. Never substitute a successful plan for saved readback verification.
