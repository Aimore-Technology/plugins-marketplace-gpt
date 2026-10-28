# Customer Notion model

## Installation and settings

Create or select `Aimore/` in the authorized customer workspace. Register actual page/database IDs in `Aimore/Dashboard` under `RunSettings`; subsequent runs use these IDs rather than global title searches. Never use developer workspace IDs.

```text
Aimore/
  Inbox
  Clients/{ClientDisplayName}/Communications
  Clients/{ClientDisplayName}/ClientPersona
  UserPersona/{UserId}/Email
  Templates/ClientPersona
  Templates/CRMNotes
  Actions
  PendingTasks
  DailyBriefs
  Dashboard/WorkflowRuns
  Dashboard/OperationLogs
  Dashboard/HealthStatus
```

Inbox can be a database with customer, unmatched and internal views; internal stakeholders use this same Inbox. Communications contains source-linked records/drafts. Move the original Inbox page when tools support it; otherwise retain it and link the canonical communication record. Do not create disconnected copies. Communication titles: local timestamp + summary + unique suffix; store timezone explicitly. SourceKey = account + direction + immutable provider message ID. Read [source identity](source-identity.md) before lookups or deduplication; use exact stored properties, not rendered Markdown or an empty moved-from Inbox view. ClientId maps to verified LocationId + ContactId, never just a name/email. UserId is separate.

ClientDisplayName is a human-readable customer page title, normally the verified CRM name; it is not ClientId. Follow [customer pages](client-pages.md) for same-name disambiguation, identity metadata, page-ID registration and in-place legacy-title migration. Full CRM IDs belong in metadata, not the primary navigation title. These are logical Notion paths; resolve actual pages by registered IDs rather than title/path text.

Register saved-view IDs and dated brief IDs as they are created, alongside the actual source/page references. Reuse them under [Notion I/O](notion-io.md) when SQL is limited; identity or full-coverage checks that cannot be verified remain incomplete.

RunSettings contains settings_schema_version 2, the pilot defaults, configured operator_id/operator_name/operator_email/operator_sms_number and actual authorized account references, allowed Gmail label IDs/exclusions/time range, reminder-email scope, Dropbox work folders, CRM entry/LocationId/Notes capability, root/database IDs, sender/signature, customer_setup.workspace_language (zh-CN or en), own SMS number, verified tool capabilities, no-send dates, schedule IDs/actual cadence, configuration version and check results. Keep credentials in connector authentication, never in settings.

## PendingTasks: ONE database, FIVE filtered views

| View / Category | Issue | Resume rule |
| --- | --- | --- |
| ClientMatching | Missing/ambiguous/conflicting identity | The operator supplies exact candidate or matching data; validate CRM account and contact. |
| DataCompletion | Missing business facts, configuration, project source/version | Submit the registered action-page input form, then validate required facts; submission is not approval. Legacy routes follow [pending input](pending-input.md). |
| ContentReview | Notes/persona/draft review or conflicting business facts | Explicit confirm/reject for the relevant version; not send approval. |
| SendApproval | Final customer send decision | Exact payload and send window approved; changed/expired approval is invalid. |
| ExecutionExceptions | Tool errors, unknown writes/sends or conflicting execution state | Reconcile actual outcome before continuing unfinished steps. |

Fields: `Name` (title), `TaskId` (text), `OperatorId` (text), `Category` (select above), `State` (select: WaitingForOperator, NeedsCorrection, ReadyToValidate, InProgress, Completed, Cancelled), `Mode` (Manual/Automatic), `RunId`, `Workflow`, `StepId`, `SourceKey`, `SourceURL`, `ClientId`, `LocationId`, `ContactId`, `Reason`, `RequiredInputs`, `OperatorInput` (short plain-text summary; structured answers belong in the body), `InputSubmitted` (checkbox), `InputTemplateVersion` (text), `ContentVersion`, `Decision` (Confirm/Approve/Return/Cancel/Pause/Postpone), `DecisionVersion`, `Approver`, `ApproverId`, `DecisionTime`, `ObservedAt`, `SendNotBefore`, `SendNotAfter`, `Result`, `LastVerifiedAt`, `ResumeStep`, `ReminderKey`, `ReminderAcknowledgedAt`. Use text/URL/date/relation properties as appropriate; structured input and full approval/history may live in the task body.

Add ActionPageURL (URL) and ActionFormVersion (text) to the canonical task and keep the exact page/task/step/content/digest binding in workflow-owned history per [operator actions](operator-actions.md). Register the ordinary Actions hub's page ID in RunSettings. It is not a second database. New action pages have only a title property and relevant business fields/choices; technical fields remain on PendingTasks. On migrated tasks canonical input/decision properties are projections, not another submission route.

Keep Category separate from State and delivery status. New DataCompletion uses task-input-v2; preserve task-input-v1 and untemplated legacy behavior until a verified explicit migration under [pending input](pending-input.md). Submission never completes a task; validation/application updates State. Approval needs a relevant explicit submitted choice, exact version and durable original evidence; the workflow records Decision/DecisionVersion/actor without asking the user to copy them. Manual mode still requires explicit owner continuation. ContentReview and SendApproval retain separate StepIds, histories and action pages. New content needs a new active review page with blank decisions.

Read [task presentation](task-presentation.md) when creating/updating tasks: one current state/version summary, localized next action, preserved history and reused verified dependencies. Update only workflow-owned fields/sections; reread actual operator input before transitions. Permitted notifications link the primary action page, current email/draft and reason, with a secondary original-task link. No unchanged-task notification every scan. Terminal/superseded pages show no active form.

Create the five views filtered by Category and excluding completed/cancelled items by default. If available tools cannot create views, create the single database, provide exact filters for the host/UI, and report view setup incomplete; do not create five databases or pretend views exist.

## CRM Notes and persona

Append one note per CommunicationId + approved version; do not rewrite old Notes or add custom fields. Use the complete plain-text template and pre-review/pre-write checks in [CRM Notes](crm-notes.md), registered as `Templates/CRMNotes`. Include communication time/timezone, source, verified LocationId/ContactId/customer, CommunicationId and content version. No Markdown/HTML formatting in the actual CRM body. Four dot-point sections:

- Context Background: background and confirmed facts.
- Action: actions actually performed.
- Recommendation: suggestion, operator/AI origin and whether executed.
- Next Schedule: next action, owner and time.

Use "Not provided / To confirm" for missing facts; verified identity/source cannot be placeholders. Persona proposals belong inside the reviewed standard sections, not an unreviewed extra section appended during writing. Communication processing owns the write when no persona changes exist; otherwise persona-update writes ONE combined approved note for both. Verified structured CRM mappings may additionally update fields; otherwise report "Notes synced; structured fields not enabled". Notion ClientPersona stores an approved snapshot with its source/version and actual sync status. Persona fields: property type, dwelling/bedroom preference, first buyer/investor status, age band only if supplied, budget, confirmed preferences, unresolved questions and next action. Do not infer unknown facts.

## Runs, logs and health

- WorkflowRuns: Name, RunId, ParentRunId, OperatorId, RecordType (Business/Scan/Initialization), Skill/version, Mode, customer mapping, SourceKey/URL, CurrentStep, Status (InProgress/WaitingForOperator/Paused/Completed/Error/Unknown/Cancelled), StartedAt, LastActiveAt, EndedAt, wait intervals, task/log links, approved version, external IDs, summary, LastVerifiedAt, LogBackfillRequired.
- OperationLogs: title, EventId, RunId, StepId, ActionId, AttemptId, OccurredAt, ObservedAt, RecordedAt, actor/observer evidence with actual configured operator IDs when known, action type/phase, Mode, system/object link, input/output versions, before/after state, result (Success/Failure/Waiting/Unknown/Cancelled), error, external IDs, approval link, correction/backfill reason.
- HealthStatus: one row per configured service, Enabled, check method, last attempt/success/error, expected interval for scheduled checks only, data cutoff, status (Unconfigured/Disabled/Healthy/Degraded/Error/Unknown/Stale), run/log links. Follow [monitoring](monitoring.md) to update real attempt/success times, distinguish recovery from native capability, and preserve error history.

Store message status separately: AwaitingApproval, ApprovedPending, Sending, ProviderAccepted, Delivered, Failed, Unknown, Cancelled. A completed review/run is not delivery evidence.

DailyBriefs has one dated page per operator/business timezone. Upsert it; link original tasks/runs/logs. Show coverage, generated time, actual vs planned time, pending actions, important-reminder state and failures. Do not duplicate log bodies or build business KPI charts.

Register GeneratedAt, DataCutoff, CurrentVersion, Coverage and PendingCount. Separate FailureCount (unresolved real workflow failures, including quality failures), UnknownCount and QualityIssueCount; RecoveredFailureCount and SyntheticFailureCount are separate historical/test metrics. Counts may overlap only when explicitly stated, for example quality as a subset of unresolved failures. Migrate absent fields on an explicit upgrade without resetting history; before migration show the labeled counts in the body and mark schema incomplete. Apply [monitoring](monitoring.md) to timestamps, scoped counts and existing legacy FailureCount meanings.
