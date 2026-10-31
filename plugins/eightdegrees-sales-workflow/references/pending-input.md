# DataCompletion input and submission

Keep one canonical task in PendingTasks. For new tasks, use the dedicated ordinary action page from [operator actions](operator-actions.md), not a database-properties editor or new Form response row. The operator fills only requested fields and checks that page's named submission to-do.

## Versioned input routes

- `InputTemplateVersion=task-input-v2` plus ActionFormVersion=`task-action-v1`: answers and submission are on the registered action page. InputSubmitted and OperatorInput on PendingTasks are workflow-owned compatibility projections, not alternative human controls. Editing either original property does not submit this form.
- `InputTemplateVersion=task-input-v1`: retain the legacy task-body form and InputSubmitted PROPERTY until an explicit, successful migration. Do not mix its submission source with the new action-page checkbox.
- Untemplated legacy tasks retain earlier save-and-validate behavior until explicitly upgraded. Preserve their original OperatorInput value and history.

Do not silently change a route when resuming a task. Register the action-page binding before setting task-input-v2; incomplete migration stays on the recorded legacy route. Structured answers belong in editable native content; accepted machine snapshots are stored separately as fenced JSON in workflow-owned task history. New OperatorInput writes remain short plain summaries. Follow [Notion I/O](notion-io.md) after rejected writes; intended state is not saved state.

## Tailored fields

Show a short reason, only currently needed fields and concrete guidance. Use a table for short answers and separate native paragraphs for a signature, explanation or multiple links. Optional fields are labeled; unknown required answers stay blank. Do not make a fenced JSON object or one long database text property the editor. Show literal file names/paths as code, not fake HTTP links.

Prefill only supplied or already verified applicable values, retaining provenance. Do not ask again for registered sender/project data. A reply-to mailbox is not automatically a sender; Dropbox root access does not establish a project version. Style samples are optional for accepted standard style.

| Task | Required | Optional / conditional |
| --- | --- | --- |
| Sender setup | Actual sender mailbox, display name, signature or explicit no-signature choice | Style preference and authorized sent examples |
| Project sources | Project, exact authorized file links/paths, current version and effective date | Requested commercial facts need evidence or an explicit accepted omission; known source conflicts require review |
| Mail scope | Authorized account, allowed labels/scope, start/end rule and timezone | Exclusions; absent labels/dates never broaden access |

## Validation and application

1. Read the recorded input route. For v2 use the original task plus its registered action page and [submission contract](operator-actions.md); for v1 use original task-body input and InputSubmitted. Unsubmitted templated input is still editing. A chat continuation counts as input submission only if the operator explicitly says the identified input is ready; persist its actual route/version/snapshot without inventing a checkbox event.
2. Automatic tasks and the narrow manually initiated communication forms in queue-execution may be validated on the shared queue. A valid current Notion submission is sufficient; do not require a continue command. Completed/cancelled/superseded tasks ignore old input edits; paused/postponed work needs a valid new resume submission, not a silent edit.
3. Validate required/conditional fields, actual source/account access, current versions and original legacy context. Placeholders are not answers. Conflicting values require the operator's choice. An unavailable fact needs an accepted omission/narrower reply rather than an invented claim.
4. Reread the original task and actual input/submission source immediately before accepting. If answers or submission changed/withdrew, do not apply the stale snapshot. Persist exact accepted answers, binding/version, observed time and original run/step before dependent work. An accepted action-page submission is durable canonical evidence; update projected properties only after that snapshot is saved.
5. Invalid input: set NeedsCorrection, show each error on the primary input surface, retain all answers and clear only the unchanged submitted flag/to-do for resubmission. Valid input: consume the submission according to its route and continue only the recorded unfinished step. Mark DataCompletion Completed only AFTER data application/registration and actual readback; downstream content/send review may still wait.
6. After interrupted application, reconcile the saved accepted snapshot and prior outcome before filling missing steps. New answers require new submission; unchanged accepted input does not require retyping. Preserve completed steps/external IDs and refresh both current task and action-page result without repeating business actions to repair presentation. Submission never approves facts/sending, starts a scanner or retries an unknown external result.

Explicit init upgrade follows [operator actions](operator-actions.md): preserve existing values, decisions and IDs; never synthesize submission during migration. Keep unresolved in-flight legacy inputs on one original route until reconciled, and report the migration exception honestly. Closed tasks are historical, not new forms.

Use [operator experience](operator-experience.md) to render verified applicable reused values once, missing/invalid fields with examples, and an explicit request/accepted/processing next step. Preserve typed drafts and all existing input-route rules. The presentation helper does not validate or apply supplied facts.
