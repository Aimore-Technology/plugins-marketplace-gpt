# One shared scan and continuation queue

run-auto performs one bounded cycle; start's native job repeats that procedure.
There is no extra continue command in the normal operator journey. The operator
initiates P0-A manually and submits matching/data/content decisions in Notion;
the queue validates those submissions and performs only their approved next step.
Mode=Manual remains provenance and does not itself require a second chat action.
It never authorizes intake of a communication the operator did not initiate.

## Sources and order

1. Read configured scope, actual ownership, checkpoints and pending attempts.
2. Observe current scoped Gmail and available SMS replies/stop, plus Notion
   Pause/Cancel/revocation, before due outbound work. Missing relevant reply
   coverage blocks affected sends; unrelated clients can continue.
3. Scan new authorized mail and current action inputs, including manually
   initiated communication review/data tasks. Read relevant configured Dropbox
   source/version references for active dependencies, not all files. Calendar
   scanning is confined to authorized work events and confirmed appointments.
4. Enqueue newly ready owner steps: verified matching -> source/data application
   -> reviewed Notes/persona sync -> inquiry draft -> email content review ->
   separate email send approval -> actual Sent -> SMS registration -> due factual
   notification dispatch. A stage only proceeds when its own evidence is ready.
   Waiting for a human stops that item; other ready work continues.
5. Process due follow-ups, configured reminders, acknowledged reminder state,
   daily summaries and confirmed appointment sync under their original owners.
   SMS uses standing notification authority; email/CRM business facts retain
   exact-version human review. No owner reenters the whole scanner.

## Manually initiated communication submissions

Only VerifyCustomer, CompleteCommunicationData, ReviewCommunication and
SyncApprovedPersona on the communication/persona owners are eligible Manual
queue steps. Eligible unsent factual SMS may migrate to SendNotificationSms while preserving Manual intake provenance; that notification route uses standing authority rather than a human submission. Other legacy unrelated Manual sales/send tasks are not silently adopted.
Registration/observe routes may inspect their current registered form. Execute
requires the durably saved accepted input, not a page timestamp or old checkbox.

Normalize the actual original task plus AcceptedSubmission for the offline
resume-task check. AcceptedSubmission contains read_verified=true, task_id,
action_page_id, content_version, operator_id and the actual input_sha256 from the
saved version-bound snapshot. The original task supplies actual PageId,
ActionPageURL and OperatorId. Do not add these as human form fields or create
this evidence from the run-auto invocation. The owner still rechecks original
binding, current answers/decision, review payload and prior attempts before
CRM changes. Unsubmitted/changed/superseded forms stay waiting. A submitted
Return, Pause or Cancel is handled as that choice, never as fact confirmation.

No new human permission is needed after a valid submission. The old explicit
continuation syntax may remain compatible for an old client, but help, action
pages and tests must not require or recommend it. report remains read/report
only; init/start/stop are not business execution shortcuts.

## Bounded progression, not busy polling

Verified customer receipt or a known stale project-email result can enqueue
RefreshEmailOutcome as a Notion-only maintenance item. Its key and affected
originals follow [email presentation](email-presentation.md). Terminal business
tasks remain terminal; do not change their State to make them executable. New
receipt observation does not wait for CRM fact review, while CRM updates still do.
No repeated history sweep, new native job or extra user command is required.

Maintain a worklist and an attempted key of original task/source, ResumeStep,
ContentVersion and accepted-input/attempt digest. Process a ready key at most
once per cycle. After a verified transition enqueue its newly ready successors;
do not restart the mailbox scan or recreate prior tasks/Notes/drafts.

Use queue_execution.bounded_work_items (default 100) and the host's actual
execution deadline. On exhaustion, persist remaining work/cutoffs and mark
partial coverage for the next cycle. A future due time is saved, not slept on.
An unchanged wait, unsubmitted review, unknown external result or stopped item
cannot cause another loop. Do not claim all sources were scanned when capability,
pagination, quota or the time budget left gaps.

Fresh original approval/policy/stop/attempt checks remain mandatory immediately
before each external effect. Native invocations also recheck their actual
schedule lifecycle/generation/operator between dependent operations. A future-due or human-waiting business child is not an active scan executor; derive busy ownership only from the current actual scan/native invocation. Notion is not an atomic lock; uncertain ownership waits for reconciliation.

## Unattended continuation

Apply [bounded restart operation](unattended-operation.md) each cycle. Defaults are 12 owner steps and a 480-second soft budget with 60 seconds for persistence. Actual saved customer limits remain explicit; init upgrade adds missing budget/checkpoint settings without changing approval or enabling a scheduler. Persist remaining source/work identities, unknown attempts and exact partial coverage. Long in-flight calls are recorded, not aborted/replayed. RefreshSmsOutcome and RefreshContactRestrictions repair only implicated originals after stop-first observation; no extra public commands.
