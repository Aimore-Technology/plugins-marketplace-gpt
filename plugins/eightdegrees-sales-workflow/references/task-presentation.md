# Current task state and dependencies

Use whenever creating or updating a PendingTasks page or report. Render user-facing text in the saved workspace language; use the current conversation language temporarily if unset. Keep stable English schema/property/category names.

For new/migrated tasks, [operator actions](operator-actions.md) defines the primary human surface under Actions. Keep the database task as execution detail; reports, hub links and permitted notifications lead to the registered action page, with the original task as a secondary details link. Do not rely on rearranging 30 database properties to make inputs discoverable.

## One current summary

Use [operator experience](operator-experience.md) for short review/field changes
and saving/request/accepted/executing distinctions. When Today linked views are
verified, canonical row links replace manual queue copies; unchanged Today or
Actions pages are not extra per-owner publication/read targets.

Use the shared [publication transition](notion-publishing.md) for every owner state/version change, including accepted input, terminal results, Pause and new-page registration. It refreshes the task and action status, verifies changed projections and updates a manual queue only in legacy mode. Return a partial publication result when a display is stale; repair only that projection from durable canonical/provider evidence. A report can describe the stale display but cannot repair those business pages.

At the top of each task, maintain a workflow-owned **Current status** section:

- Current State, Category and Manual/Automatic mode, with a brief localized explanation.
- The exact current content/review version and one canonical source/draft/preview link. List unresolved differences before long Notes or history. For example, a change from required parking to preferred parking is an unresolved fact change, not an approved persona update.
- The required next action: use the registered action-page answers/choice and named submission to-do, then run the next authorized scan for Automatic tasks or explicitly continue the original Manual task. Legacy task-input-v1 still uses the original InputSubmitted property until migrated. Do not promise a background job when no schedule is enabled. Editing/submitting data and content/send approval remain different actions.
- Only currently missing/invalid items, or an explicit completed result. Completed data tasks explain that they are hidden from open views but remain accessible through the original inquiry/run link.

Keep editable input, validation results, current review material and historical evidence in separate named sections. When a version advances or a correction is resolved, replace the current summary and move the superseded state/version into labeled history. Never leave an old NeedsCorrection notice or v1 approval request as a second current instruction before the active v2. Do not delete original operator answers, decisions, attachments or child pages.

During a targeted update, fetch the page and reread operator input first. Patch only workflow-owned sections; do not replace the whole page just to update status. Persist state/result and refresh the summary, then verify their consistency when recovering a partial update. If only presentation saving failed, repair the presentation; do not repeat the CRM action or send. A stale summary is an implementation problem, not a request for the operator to repeat the completed business step.

Verify all current workflow-owned status, Processing result and input instructions, not only the page header. Use [publication validation](publication-validation.md): a recorded Pause must not coexist with Not submitted or choose-one prompts. Preserve original answers/quoted content and explicitly labeled history.

## Reuse dependencies

Show a small dependency table: original task/settings/source link, Verified/Waiting/NeedsCorrection/Unknown, relevant version and what remains missing. Reuse already verified applicable values from RunSettings or the original source; do not request the same file/version or sender information separately on every child task. Recheck authorization, applicability and current version before use. A changed/unknown version needs validation; a Dropbox root permission is not a project version, and a scanned mailbox is not an approved sender.

An Automatic inquiry may use already registered verified setup data. It cannot resume a waiting Manual setup task, silently copy unsubmitted answers or turn that task Automatic. Scope-specific supplied facts belong to the inquiry until explicitly registered globally. If a dependency is missing, point to its original task and list only the remaining inquiry-specific inputs. Do not create duplicate setup tasks or turn optional style samples into required blockers.

## Views and reports

Keep operator views focused on Name, State, Mode and ActionPageURL; wrap cells and keep technical properties out of the primary display when supported. Put active ordinary-page links on Actions so users can bypass database-property panels. `report` exposes current business state, missing dependency and next action with the original task as a secondary link; it does not create/edit action forms, execute dependencies, consume submissions or copy a second task/log body. Use [Notion I/O](notion-io.md) for quota-limited reads. Keep one current daily summary with observation time, source cutoff, coverage and only known counts; preserve older snapshots as history. Scoped snapshots must not inherit global counts or false zero-failure claims. Completed/cancelled tasks have no active input request; show their outcome and history only.
