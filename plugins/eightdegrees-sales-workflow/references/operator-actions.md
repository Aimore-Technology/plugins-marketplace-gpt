# Dedicated operator action pages

## Purpose and entry point

The operator needs to find this task's answers and decision without scrolling past technical database properties. Keep ONE PendingTasks database as the canonical execution record, and use ordinary pages under `Aimore/Actions` for non-email human input. New
email uses native Consent on the original task in one view, without an ordinary
action page. These are not another tracker or new Form response rows. Ordinary pages have only the title property; IDs, actors, versions and execution fields stay in PendingTasks and its workflow-owned history.

Use the packaged [action page layout](../assets/task-action.md), rendered in the saved workspace language. [Today](operator-experience.md) is the primary entry after verified setup: its native linked views group original records into review, information, attention and waiting. Actions stores ordinary action pages/history; an unupgraded installation retains its verified legacy queue. Direct notifications still open the registered action page, with task details secondary.

Keep active links ahead of historical child-page listings; do not turn a long list of superseded pages into the new primary queue. Preserve history and native child-page tags when updating the hub. If page creation/registration is uncertain, retain any returned page ID and reconcile the original parent/task before retrying; a failed URL projection must not create another action page.

Apply [publication transitions](notion-publishing.md) in the same owner invocation after every state/version/action-binding change: refresh canonical task summary and action status/result. Verified Today linked views follow canonical changes and need no duplicate queue write; legacy queue mode still refreshes its one entry. Do not defer canonical synchronization to init/report. Historical queues and old Current operation headings become historical; preserve children and input. A failed projection is quality repair, never another external action.

PendingTasks views may show Name, State, Category, Mode and ActionPageURL, hiding technical IDs when supported. A native database card/title may still open the database record: do not claim that its click target was changed. The visible action link and ordinary-page hub provide the direct route. Views/hiding are presentation, not access control. If tools cannot create/register an ordinary page, report action-page setup incomplete and offer the original task or an explicit chat reply; do not claim the clutter is fixed or invent widgets.

## One page for one task step and review version

Register ActionPageURL and the current ActionFormVersion (`email-review-v4` for new mail; `task-action-v1` for other forms) on the canonical task. In workflow-owned task history, bind the actual action page ID to TaskId, StepId, Category, Mode, ContentVersion and exact review payload/manifest digest when relevant. This binding is system-owned; never ask the operator to copy an ID/version, type ApproverId or choose their own authority. Resolve actor from existing configured/authenticated evidence, distinguishing observation from actual decision time.

Include verified OwnerSkill, ResumeStep and ResumeContractVersion from [task routing](task-routing.md) in that binding. Route observed submissions to their named owner, not the parent communication workflow. An unclear route is not an actionable form. Owner/step repairs preserve existing approved scope and follow explicit upgrade rules; operators do not edit routing fields.

Reuse the registered page while task/step/content is unchanged. For new review content or a new approval step, create and register a new action page, preserve old input/decisions, mark the old page superseded and remove its active link from the hub. Never transfer checked choices to the new page. A copied/unregistered page or a superseded page cannot approve the active task. Customer-readable titles may include topic/short date to distinguish multiple tasks; matching still uses the registered IDs.

## Only relevant inputs

New email uses the email-review-v4 native Consent view over its original task.
Follow [consent view](consent-view.md); other forms below apply to non-email and legacy work. Show exact subject/readable body, recipients and window in ReviewText. Consent
is the only checkbox and checking it submits; no separate form, Submit,
Return/Pause/Cancel group or date checkbox. Uncheck before dispatch to withdraw.
Task-only technical history and exact-version safeguards remain.

DataCompletion uses short fields/native multiline paragraphs and a named
submission. Names are resolved automatically for inquiries; unknown project/lot
or missing required material uses this input. Manual CRM facts still use their
own exact-version Notes review. Factual SMS notifications have no human form.
A reminder acknowledgement closes only its reminder. Operators never fill IDs,
version hashes or actor metadata. All new choices start unchecked.

## Observe, validate and record

Validate explicit owner/step routing for input observation under [task routing](task-routing.md) before consuming a form. A permitted scan may record an Automatic send choice in observe phase while actual sending remains deferred in execute phase. Only eligible manually initiated communication forms join the shared queue; report-only/draft-only send consumption remains excluded; an invalid route stays pending. Do not broaden the policy to obtain an eligible result.

1. Discover eligible canonical Automatic tasks and the narrow Manual communication steps in queue-execution. For v4 email read the original task once, observe Consent/ReviewText and use email.accept; no action-page fetch or Submit. For other forms fetch each registered active action page once for candidate input, reusing that snapshot for acceptance and imminent dispatch; refresh only after an intervening change or delay. Do not filter new-route candidates solely by the old InputSubmitted projection: non-email/legacy forms use a body to-do and v4 uses native Consent. Do not scan historical forms or unrelated Manual sends; current manually initiated communication forms are eligible. Verify binding/current payload and actual saved checkbox/answers; a view row, page edit time or legacy Decision edit is not new submission. Leave unsubmitted drafts untouched. A page open/save is not a decision. Any unexamined eligible forms mean partial input coverage, not a zero-pending claim.
2. Preserve existing Mode and invocation limits. The shared queue may validate the narrow manually initiated communication forms and continue their approved step. A valid submitted review is sufficient; do not ask for another continue command or rewrite Mode. Other Manual sends remain excluded. Resolve the page's original-task backlink, then verify that the task's active ActionPageURL and binding match; a copied page backlink alone is insufficient. No notification, customer send or schedule is enabled by submission.
3. On a submitted form, validate exactly one applicable choice in each required choice group, required answers, conditional fields and any postponement date/timezone. Return for revision requires useful revision instructions. No applicable choice/multiple choices/missing fields means NeedsCorrection. Explain each field error next to the input, preserve every answer/selection/comment, and clear only the submission to-do if the input still matches the rejected snapshot. Do not make a decision for the operator.
4. Validate the current task, active binding and action inputs once before accepting. If input/submission is changed or withdrawn, do not consume stale data. Persist the exact observed submission snapshot, action-page ID, binding/version, actor evidence and observation time in the original task/log BEFORE any dependent business mutation. Key a submission by action-page ID plus a stable digest of its binding, answers, selected intent and comments. Exclude workflow-owned status text, observation times and the consumed submission checkbox from that input digest; retain checkbox evidence separately in the snapshot. Serial re-observation of an already applied snapshot cannot duplicate an action. Notion is not an atomic lock.
5. Copy an applicable validated decision/version/actor and a short input summary to canonical properties as workflow-owned projections. Candidate/data submission never creates Confirm/Approve. Request reconciliation stays a snapshot intent, not a new select option or permission to repeat an unknown external attempt; leave unrelated Decision fields unset. Receipt updates only reminder evidence. Failed canonical evidence saving blocks dependent writes. Record accepted input and confirm dependent writes from their original API responses.
6. After durable acceptance, clear the consumed submission to-do only if the action page still matches the accepted snapshot. Keep the selected choice and answers visible with a status such as Decision recorded; execution pending. A cleared checkbox after documented consumption does not erase the recorded decision. Later answer/choice/payload edits invalidate pending use of that snapshot and need fresh submission/review as applicable. A new submitted Cancel/Pause or explicit withdrawal is checked before the dependent action. Use the same current original-record snapshot for imminent dispatch; a later-cycle send or intervening edit needs a fresh targeted observation.
7. Show the actual outcome and next step at the top. On success retain answers/history; on partial saving repair only the missing projection. Never repeat a provider write to repair this page. New content after Return uses a new page/version with blank choices. Paused/postponed work does not resume just because data was edited; require an actual new resume decision/current submission and any renewed email approval/window; the shared queue then observes it without a separate command. Completed/cancelled/superseded pages show No action required and no active submission controls. Old checkbox edits on those pages do not reopen tasks.

If page access is denied or input is ambiguous, keep that task waiting with a recovery explanation. Present an unavailable draft/expired approval as such, retaining draft/comments and a clear request for a fresh review. Do not present unverified application as complete.

## Existing workspaces

An explicit init upgrade creates/reuses Actions and action pages for eligible open tasks, registers bindings/links and preserves task/page/run IDs, input, history and Mode. Do not delete/convert technical properties or move business records out of PendingTasks. Show old details behind a link.

Copy only unambiguous existing answers as unsubmitted draft input, retaining the original answer/provenance. Never manufacture a new human submission or decision. Existing approved snapshots remain historical valid evidence within their original scope; migration alone neither approves nor revokes them. An in-flight/unconsumed legacy submission, unresolved projection or unclear decision binding stays on its legacy input route until reconciled by the owning workflow; mark that task's action migration pending rather than introducing two editable authorities. For successfully migrated tasks the action page is the sole new-input surface; original properties are projections. Closed tasks remain historical without generating new action forms.

At the boundary validate the proposed current status/result and prompts once before saving, then confirm API success. Inactive controls become historical answers; remove the workflow-owned choose-one instruction for that inactive step. A correct top summary does not excuse a stale Not submitted result below it.
