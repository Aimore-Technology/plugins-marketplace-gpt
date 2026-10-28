# DataCompletion input and submission

Use this contract when creating, upgrading or validating a DataCompletion task. Keep one task page in PendingTasks; do not create a separate response database or treat a new Form response as an update to the original task.

## Task page

Add `InputSubmitted` (checkbox, initially false) and `InputTemplateVersion` (text). A task with `InputTemplateVersion=task-input-v1` uses this submission contract. Keep the existing `OperatorInput` property and its original value for compatibility. Never erase operator answers or historical decisions during migration.

Put an editable **Input form** at the start of the task body. Render it in the configured `customer_setup.workspace_language`. Include:

- A short reason and a field table: requested item, Required/Optional/Conditional, answer and an example or precise guidance. Include only fields needed by this paused step. Leave unknown required answers clearly blank, not plausible defaults. State any condition explicitly.
- Separate native paragraph sections for long answers such as an email signature, explanation or multiple source links. Reference those sections from the table. Do not use a fenced code block as the primary editor or promise a custom textarea widget in a database property.
- A submission instruction: finish the fields, check the `InputSubmitted` property, then wait for the next authorized scan for Automatic tasks or explicitly continue the original task for Manual tasks. There is no separate Save button or automatic host job created by this checkbox. Keep Category, State and Mode visible.
- A **Validation result** section owned by the workflow, with missing fields, inaccessible links or version conflicts and the next action. Submission is neither content confirmation nor customer-send approval.

Prefill only values supplied by the operator or already verified, with their provenance. A reply-to mailbox is not automatically the customer sender. Style samples are optional when the operator accepts a standard business style. Permission to a Dropbox root is not evidence of a current project file/version.

Useful field sets (adapt to the actual task):

| Task | Required | Optional / conditional |
| --- | --- | --- |
| Sender setup | Actual sender mailbox, display name, final signature or explicit no-signature choice | Style preference and authorized sent examples; examples are optional for standard business style |
| Project sources | Project name, exact authorized file links/paths, current version and effective date | Price/availability, ongoing fees and completion evidence when the inquiry asks for them; an explicit unavailable fact leads to a stated omission, never an invented answer |
| Mail scope | Authorized account, allowed scope/labels, start/end rule and timezone | Exclusions; never broaden scope because a label or date is absent |

## Validation and continuation

1. For a templated task, `InputSubmitted=false` means still editing: do not consume partial answers. Legacy tasks without `InputTemplateVersion` retain the earlier save-and-validate behavior until explicitly upgraded. An operator can explicitly submit the identified task in chat; record that submission before validation. A continue request counts as submission only when the operator explicitly says the input is ready.
2. For Automatic tasks, a permitted scan can observe a submitted input and set `ReadyToValidate`. Manual tasks require explicit continuation of that exact task by its owning skill; a scanner may show the link but cannot resume it. Cancelled, completed, paused or postponed tasks do not resume merely because a checkbox is checked.
3. Read the complete input form and legacy `OperatorInput`. Compatible legacy text is supporting context; conflicting values require the operator's choice. Validate the actual required fields, authorized account/source access and current versions. Placeholders and an unchecked list of requirements are not answers. A declared unavailable fact does not satisfy a required claim without an accepted omission or narrower reply.
4. Before committing validation, reread the original input and submission flag. If the answers changed or submission was withdrawn, leave the task waiting and do not act on the stale snapshot. Persist the exact accepted input snapshot, observation time and original task/run/step under workflow-owned validation history; never invent the human's submission time. Notion is not an atomic lock.
5. Missing/invalid data: set `NeedsCorrection`, list each specific issue and how to fix it, and clear `InputSubmitted` for resubmission. Preserve all answers. Valid input: clear the consumed checkbox and continue only the recorded unfinished step under its original mode, ownership and invocation limits. Mark this DataCompletion task `Completed` only after the supplied data has been applied/registered and verified; a later content/send review or business run can remain waiting. If application is interrupted, the accepted snapshot and original run evidence allow reconciliation without asking for the same unchanged input again. Changed inputs require a fresh submission.
6. Preserve accepted snapshots/history, external attempt IDs and completed steps across reruns. Log observed submission, validation and outcome. Do not move an unexecuted task to Completed, approve facts/sends, restart a scan from a helper, or retry an unknown external result because input was submitted.

## Upgrade and display

During an explicitly requested setup/upgrade, add the properties, fetch each open DataCompletion page, and insert a task-specific input form without replacing unrelated content. Preserve any old free-text answer, prefill only unambiguous portions and mark them unvalidated. Enable `task-input-v1` on that page only after the form is saved; leave submission false unless the operator actually submits it. Keep task/page/run IDs and Mode unchanged. Completed/cancelled tasks remain historical.

Show Name, State, Mode, RequiredInputs and InputSubmitted in the DataCompletion view. Retain original filters excluding Completed/Cancelled. Use wrapped cells. Keep OperatorInput accessible as legacy input; put long answers in the page body. When supported, pin Category/State/Mode/InputSubmitted and move technical IDs into a secondary property section so the body is easy to reach. If a view/layout capability is unavailable, report it without creating a second tracker.
