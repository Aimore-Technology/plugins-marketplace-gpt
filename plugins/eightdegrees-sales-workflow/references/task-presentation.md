# Current task state and dependencies

Use whenever creating or updating a PendingTasks page or report. Render user-facing text in the saved workspace language; use the current conversation language temporarily if unset. Keep stable English schema/property/category names.

## One current summary

At the top of each task, maintain a workflow-owned **Current status** section:

- Current State, Category and Manual/Automatic mode, with a brief localized explanation.
- The exact current content/review version and one canonical source/draft/preview link. List unresolved differences before long Notes or history. For example, a change from required parking to preferred parking is an unresolved fact change, not an approved persona update.
- The required next action: fill the body form, check InputSubmitted, then run the next authorized scan for Automatic tasks or explicitly continue the original Manual task. Do not promise a background job when no schedule is enabled. Editing/submitting data and content/send approval remain different actions.
- Only currently missing/invalid items, or an explicit completed result. Completed data tasks explain that they are hidden from open views but remain accessible through the original inquiry/run link.

Keep editable input, validation results, current review material and historical evidence in separate named sections. When a version advances or a correction is resolved, replace the current summary and move the superseded state/version into labeled history. Never leave an old NeedsCorrection notice or v1 approval request as a second current instruction before the active v2. Do not delete original operator answers, decisions, attachments or child pages.

During a targeted update, fetch the page and reread operator input first. Patch only workflow-owned sections; do not replace the whole page just to update status. Persist state/result and refresh the summary, then verify their consistency when recovering a partial update. If only presentation saving failed, repair the presentation; do not repeat the CRM action or send. A stale summary is an implementation problem, not a request for the operator to repeat the completed business step.

## Reuse dependencies

Show a small dependency table: original task/settings/source link, Verified/Waiting/NeedsCorrection/Unknown, relevant version and what remains missing. Reuse already verified applicable values from RunSettings or the original source; do not request the same file/version or sender information separately on every child task. Recheck authorization, applicability and current version before use. A changed/unknown version needs validation; a Dropbox root permission is not a project version, and a scanned mailbox is not an approved sender.

An Automatic inquiry may use already registered verified setup data. It cannot resume a waiting Manual setup task, silently copy unsubmitted answers or turn that task Automatic. Scope-specific supplied facts belong to the inquiry until explicitly registered globally. If a dependency is missing, point to its original task and list only the remaining inquiry-specific inputs. Do not create duplicate setup tasks or turn optional style samples into required blockers.

## Views and reports

Keep the DataCompletion view focused on Name, State, Mode, InputSubmitted, RequiredInputs, Result and original source link; wrap cells. Keep technical IDs/history available on the page without crowding primary actions. `report` links the original task and exposes its current state/version, missing dependencies and next action; it does not execute the dependency, create approvals or copy a second task/log body. Use [Notion I/O](notion-io.md) for quota-limited reads. Keep one current daily summary at the top with observation time, source cutoff, coverage and only known counts; move earlier generated summaries beneath labeled history instead of appending a new "current" section below stale headlines. A scoped snapshot must not inherit global counts or a false zero-failure claim. Report generation time and incomplete coverage honestly.
