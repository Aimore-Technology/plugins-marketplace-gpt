# Customer Notion model

## Installation and settings

Create or select `Aimore/` in the authorized customer workspace. Register actual page/database IDs in `Aimore/Dashboard` under `RunSettings`; subsequent runs use these IDs rather than global title searches. Never use developer workspace IDs.

```text
Aimore/
  Inbox
  Clients/{ClientId}/Communications
  Clients/{ClientId}/ClientPersona
  UserPersona/{UserId}/Email
  Templates/ClientPersona
  PendingTasks
  DailyBriefs
  Dashboard/WorkflowRuns
  Dashboard/OperationLogs
  Dashboard/HealthStatus
```

Inbox can be a database with customer, unmatched and internal views; internal stakeholders use this same Inbox. Communications contains source-linked records/drafts. Move the original Inbox page when tools support it; otherwise retain it and link the canonical communication record. Do not create disconnected copies. Titles: local timestamp + summary + unique suffix; store timezone explicitly. SourceKey = account + direction + immutable provider message ID. Read [source identity](source-identity.md) before lookups or deduplication; use exact stored properties, not rendered Markdown or an empty moved-from Inbox view. ClientId maps to verified LocationId + ContactId, never just a name/email. UserId is separate.

Register saved-view IDs and dated brief IDs as they are created, alongside the actual source/page references. Reuse them under [Notion I/O](notion-io.md) when SQL is limited; identity or full-coverage checks that cannot be verified remain incomplete.

RunSettings contains settings_schema_version 2, the pilot defaults, configured operator_id/operator_name/operator_email/operator_sms_number and actual authorized account references, allowed Gmail label IDs/exclusions/time range, reminder-email scope, Dropbox work folders, CRM entry/LocationId/Notes capability, root/database IDs, sender/signature, customer_setup.workspace_language (zh-CN or en), own SMS number, verified tool capabilities, no-send dates, schedule IDs/actual cadence, configuration version and check results. Keep credentials in connector authentication, never in settings.

## PendingTasks: ONE database, FIVE filtered views

| View / Category | Issue | Resume rule |
| --- | --- | --- |
| ClientMatching | Missing/ambiguous/conflicting identity | The operator supplies exact candidate or matching data; validate CRM account and contact. |
| DataCompletion | Missing business facts, configuration, project source/version | Submit the task-body input form, then validate required facts; submission is not approval. See [pending input](pending-input.md). |
| ContentReview | Notes/persona/draft review or conflicting business facts | Explicit confirm/reject for the relevant version; not send approval. |
| SendApproval | Final customer send decision | Exact payload and send window approved; changed/expired approval is invalid. |
| ExecutionExceptions | Tool errors, unknown writes/sends or conflicting execution state | Reconcile actual outcome before continuing unfinished steps. |

Fields: `Name` (title), `TaskId` (text), `OperatorId` (text), `Category` (select above), `State` (select: WaitingForOperator, NeedsCorrection, ReadyToValidate, InProgress, Completed, Cancelled), `Mode` (Manual/Automatic), `RunId`, `Workflow`, `StepId`, `SourceKey`, `SourceURL`, `ClientId`, `LocationId`, `ContactId`, `Reason`, `RequiredInputs`, `OperatorInput` (short plain-text summary; structured answers belong in the body), `InputSubmitted` (checkbox), `InputTemplateVersion` (text), `ContentVersion`, `Decision` (Confirm/Approve/Return/Cancel/Pause/Postpone), `DecisionVersion`, `Approver`, `ApproverId`, `DecisionTime`, `ObservedAt`, `SendNotBefore`, `SendNotAfter`, `Result`, `LastVerifiedAt`, `ResumeStep`, `ReminderKey`, `ReminderAcknowledgedAt`. Use text/URL/date/relation properties as appropriate; structured input and full approval/history may live in the task body.

Keep Category separate from State and delivery status. For DataCompletion pages using task-input-v1, only submitted inputs are validated; follow [pending input](pending-input.md) for forms, submission, migration and accepted snapshots. Untemplated legacy tasks retain save-and-validate behavior until explicitly upgraded. Submission never completes a task; validation/application updates State. Approval always needs the relevant explicit Decision and version. Manual mode additionally waits for an explicit continue request. Preserve decision history when advancing a task from ContentReview to SendApproval. Different approval steps retain separate StepIds/history.

Read [task presentation](task-presentation.md) when creating/updating tasks: one current state/version summary, localized next action, preserved history and reused verified dependencies. Only workflow-owned fields are updated by the model; reread the operator's input before each transition. Include the exact email/draft link, required action and reason in every notification. No unchanged-task notification every scan.

Create the five views filtered by Category and excluding completed/cancelled items by default. If available tools cannot create views, create the single database, provide exact filters for the host/UI, and report view setup incomplete; do not create five databases or pretend views exist.

## CRM Notes and persona

Append one note per CommunicationId + approved version; do not rewrite old Notes or add custom fields. Header: communication time/timezone, source, verified customer, CommunicationId and approved version for reconciliation. Four dot-point sections:

- Context Background: background and confirmed facts.
- Action: actions actually performed.
- Recommendation: suggestion, operator/AI origin and whether executed.
- Next Schedule: next action, owner and time.

Use "Not provided / To confirm" for missing facts. Communication processing owns the write when no persona changes exist; otherwise persona-update writes ONE combined note for both. Verified structured CRM mappings may additionally update fields; otherwise report "Notes synced; structured fields not enabled". Notion ClientPersona stores an approved snapshot with its source/version and actual sync status. Persona fields: property type, dwelling/bedroom preference, first buyer/investor status, age band only if supplied, budget, confirmed preferences, unresolved questions and next action. Do not infer unknown facts.

## Runs, logs and health

- WorkflowRuns: Name, RunId, ParentRunId, OperatorId, RecordType (Business/Scan/Initialization), Skill/version, Mode, customer mapping, SourceKey/URL, CurrentStep, Status (InProgress/WaitingForOperator/Paused/Completed/Error/Unknown/Cancelled), StartedAt, LastActiveAt, EndedAt, wait intervals, task/log links, approved version, external IDs, summary, LastVerifiedAt, LogBackfillRequired.
- OperationLogs: title, EventId, RunId, StepId, ActionId, AttemptId, OccurredAt, ObservedAt, RecordedAt, actor/observer evidence with actual configured operator IDs when known, action type/phase, Mode, system/object link, input/output versions, before/after state, result (Success/Failure/Waiting/Unknown/Cancelled), error, external IDs, approval link, correction/backfill reason.
- HealthStatus: one row per configured service, Enabled, check method, last attempt/success/error, expected interval for scheduled checks only, data cutoff, status (Unconfigured/Disabled/Healthy/Error/Unknown/Stale), run/log links.

Store message status separately: AwaitingApproval, ApprovedPending, Sending, ProviderAccepted, Delivered, Failed, Unknown, Cancelled. A completed review/run is not delivery evidence.

DailyBriefs has one dated page per operator/business timezone. Upsert it; link original tasks/runs/logs. Show coverage, generated time, actual vs planned time, pending actions, important-reminder state and failures. Do not duplicate log bodies or build business KPI charts.
