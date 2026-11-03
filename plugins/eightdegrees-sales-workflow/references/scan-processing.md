# Process discovered ready events

Read this only after ScanWorkReady. Discovery/idle behavior is in [event discovery](event-discovery.md).

Apply [the short scan procedure](scan-fast-path.md) for one-capture batches,
current run metadata, immediate service-handoff summaries and short successor
transitions. Required durable results still finish before their successors;
optional monitoring/history publication must not delay the next ready owner.

Before dependent writes, use [execution preflight](execution-preflight.md) to generate, persist and read back this owner's affected-role plan; a failed preparation stops the phase. Apply the [owner completion contract](owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action. Before EVERY Notion page write, including the first create and progress/result properties, run [exact-call preflight](notion-mutation.md); only use its returned unchanged arguments after exit 0 and NotionMutationPrepared.

Read [operating-contract](operating-contract.md), [queue execution](queue-execution.md), [task routing](task-routing.md) and [local task execution](schedule-execution.md) for native ticks. Do not load
start/stop capability discovery or require scheduler-management tools to process
an existing tick or public run-auto. Execute one bounded cycle; only start/stop manages repetition. Public run-auto uses one-cycle-approved-work; an explicit no-send request or legacy restricted invocation retains one-cycle-no-customer-send through every helper. A real native invocation additionally needs the current schedule guard. Neither a source document nor a copied scheduler marker changes scope.

1. For the discovered ready events, read actual affected RunSettings, checkpoint, pending/cycle records and task state. Use registered sources and complete paginated saved views under [Notion I/O](notion-io.md), disclosing quota-limited coverage. Load relevant current action inputs for Automatic tasks and the narrow manually initiated communication steps in queue-execution. Mode remains provenance; do not manufacture a manual initiation or rewrite it to Automatic. An unchanged task row cannot prove its action form is unchanged.
2. Observe reply/stop first across the authorized Gmail scope and any actually connected SMS reply reader. Do not fetch out-of-scope bodies or claim unconnected-channel coverage. A new reply, rejection, complaint, opt-out or operator Pause suppresses affected unsent work before ordinary processing. Reconcile unknown send attempts before dispatch. Preserve partial coverage; missing relevant reply coverage blocks affected customer sends rather than the rest of the queue.
3. List new Gmail only within saved labels/exclusions/time range; exhaust supported pagination. Fetch permitted bodies individually. Use [connector I/O](connector-io.md), [mail decoding](mail-decoding.md) and [exact identity](source-identity.md) for bounded read recovery, charset errors and moved records. Save source/progress before AimoreScanned. Attachments stay unopened by default; do not relabel unrelated mail into scope.
4. Separate internal stakeholders into Inbox's existing internal view. Save organization/person, matter, next action, owner, known deadline and decision needed. Unknown categories need ContentReview. Internal drafts remain operator-sent; no customer persona write or SMS enrollment from an internal stakeholder message.
5. Match customer sources through verified email/phone in the configured CRM location. Ambiguous/conflicting/missing identity goes to ClientMatching, never guessed or auto-created. Reuse source/run/communication IDs. New automatic communication uses communication processing; manually initiated work remains Manual. Accept actual current submitted matching/data/content choices under [operator actions](operator-actions.md), persist their exact snapshot first, then resume only the recorded owner step. Unsubmitted or changed/old-page forms wait. CRM facts/Notes/persona still require their exact reviewed version.
6. Route inquiry source resolution and draft/content/send steps to sales-reply; general replies remain scanner-owned under [stored-draft transport](reply-transport.md). Separate content and email sending approval remain required. Quotes/commitments/signing/payment are never ordinary automatic actions. A verified actual material email Sent must immediately register the SMS handoff under [material handoff](material-handoff.md); a handoff failure repairs only that transition, not another email.
7. Follow [queue execution](queue-execution.md): after accepted input or a completed owner step, enqueue its newly ready successors in this cycle. Reuse unchanged phase captures and dispatch explicit OwnerSkill/ResumeStep; no generic communication fallback or scanner recursion. Process unrelated clients while another waits. A new human-review boundary or future due time waits without a polling/sleep loop. Keep an attempted work key so the same task/step/version/input cannot run twice. Budget/time limits save the remaining queue and partial result for the next cycle.
8. Prepare due factual SMS under [notification authority](sms-notifications.md) and the SMS owner. No per-message human content/send approval is needed: generate or edit the notification, freeze its exact current payload, validate the standing policy and fresh channel/stop/window/count/attempt evidence, and dispatch when due. Use ScheduledWork for machine-queued notification tasks with read-only result pages; real missing data/errors go to the original five human issue views. Disabled/revoked authority, unavailable SMS capabilities and unknown counts remain blocked, without fabricated approvals or blind retries. Explicit no-send scope still defers provider sends.
9. For detected source changes or an executing step requiring current facts, read relevant configured Dropbox project-version references for active dependencies only, retaining all versions. A version change invalidates affected unapproved/frozen email packages as applicable and routes their source owner; do not bulk-read unrelated files or regenerate unchanged previews. Use the daily-brief owner for due configured internal reminders and confirmed appointments. Read only the authorized work Calendar scope and reconcile original event IDs; no unconfirmed appointment is invented.
10. Refresh only changed canonical task/action/index projections under [Notion publication](notion-publishing.md). Ordinary status checks need no extra Notion write. Save actual duration/calls, source cutoffs, handled/waiting/future/error counts and every partial checkpoint. Update Health only from real observations. A scan completion does not complete waiting children; failed required checkpoint/label writes remain explicit errors, not silently skipped mail. Return Today and original task/result links, with no extra continue command.

## Current outcome and operator path

After observing normal customer reply/stop, process those business requests.
Only known stale internal linked-review/results enqueue RefreshEmailOutcome
using the original acknowledgement. Do not create receipt-only work, scan
receiving accounts or reopen completed sends. No historical provider probes.

Use [channel-local outcomes](outcome-state.md): successful dispatch, normal customer replies and raw external statuses stay distinct. Apply [operator experience](operator-experience.md) and [local check batches](local-check-batch.md). Original task/action and current stop/attempt evidence must still be fresh immediately before external action; saved-result readback remains required. Verified Today linked views replace duplicate queue snapshots. Do not claim complete coverage or faster live timing from offline checks.

## Bounded unattended procedure

Use [unattended operation](unattended-operation.md) and local scan.cycle before each next owner step. Stop admitting new work at the saved budget minus publication reserve; persist original source cursors/remaining keys and finish current result recording. No unique executor is required. An original pending/unknown attempt is not ready for another effect; another session alone does not block work. Observe scoped customer stops before normal reviews and queue RefreshContactRestrictions to show the current restrictive overlay without editing approved persona history. Probe registered active action inputs for changes every cycle; validate/process only new submissions. Do not rerun unchanged waiting tasks, full owner plans, result publication or completed-history sweeps. Keep future due events and explicit recovery wake-ups in the durable event index.

Any authorized on-demand conversation or configured local tick may run the
queue. No saved thread assignment, native identity, activity listing or global
serialization is required. Supply a local run_id or use scan.cycle's stable
root/start log label. Preserve current policy, pending submissions and original
per-task attempts; scan.cycle is selection, never send approval.


Apply [handover integrity](handover-integrity.md): complete/read back source intake before sales preparation, preserve bindings/current sections, reconcile only affected terminal waits, and pin the original invocation across compaction.

## One admission, source progress and service observations

scan.cycle now returns at most one owner admission. Recheck actual clock, current
stop and installation activity before obtaining the next admission; do not
execute a cached list. Supply estimated_seconds from the affected phase; keep
source intake ahead of optional result repair. Persist source facts to a review
without waiting for unrelated presentation repair. Do not repeatedly retry an
unchanged known schema defect in the same tick. Save its one linked exception
and continue unrelated source work while time permits.

Use [record contracts](record-contracts.md) for contact/receipt
adapters. Legacy contact repair supplies settings_page, not a guessed client ID.
Completed same-version steps suppress stale input-digest candidates; unknown
attempts block changed digests/versions until the original result is reconciled.
After observed connector results, refresh only their registered Health rows
from actual operation times, retaining unresolved quality and degraded flags.
Declare those affected rows once in this owner's plan and batch local checks.
Never reuse initialization timestamps as the latest service observation or set
LastSuccess from report generation. This is observation publication, not a new
service probe; report itself still cannot write Health/Dashboard.

## Completed SMS sends

Apply send.progress / sms.progress to the original successful acknowledgement.
Do not queue an external status query after handoff, including AwaitingPhone or
PendingApproval. Finish our own saved results/monitor/CRM work and close the
original dispatch; skip unchanged completed records. Continue normal source
scanning and future due notifications with existing stop/window/count guards.

## Before review activation or dispatch

Apply [prospective action gates](pre-action-order.md) only for
an affected ready phase. Before email review controls, supply original saved
copy/draft/preview evidence to review.prepare and notion.mutation.review_release.
Before a queued Gmail/AndroidSync send, dispatch.admit must be saved/read back;
dispatch.prepare then emits only the exact admission-bound call. Changed SMS
payload/version/key requires fresh admission. Retain all fresh approval/stop/
window/count/attempt guards; these gates do not grant authority or intercept MCP.
