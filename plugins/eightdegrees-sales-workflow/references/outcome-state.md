# Current state and send-result projections

Use after a known external result or when candidate queries disagree with an
original task. `outcome_checks.py task|project|verify|counts` is an offline check over
normalized actual observations; retain the original tool responses and mapping.
It never reads tools, repairs pages, grants approval or repeats an operation.

## Task reads

Lists/views locate candidates; the registered original task/action carries the
current decision. If state differs, save both observations, stop that item's
execution and reconcile the original source. Never turn Completed into InProgress
from a query row or treat missing query results as absent work. Report-only may
show original/candidate states and incomplete coverage without repairing either.
Other independent items may continue. A source conflict is not proof of a cache
bug or another person's edit.

Normalize original={id,state,read_verified:true} and optional candidate={id,state}
for the task check. The result is only state eligibility; approval, ownership,
version, source, stop conditions and provider attempts still need their checks.
Terminal tasks return Deferred. Conflicts return NeedsReconciliation.

## One verified result, several current views

Keep the immutable provider outcome on the original attempt/task. Normalize
task_id, content_version and provider={operation:email|sms,message_id,status,
read_verified:true}. Accepted/AwaitingPhone/PendingApproval/Unknown reserves an
attempt; it is not a sent count. Actual Gmail Sent, SMS SentToNetwork or Delivered
counts the unique message once. Deduplicate counts by immutable provider message
and attempt, never by number of logs or pages.

Optional human_receipt={message_id,received:true,source,sender_display} records
an actual operator observation separately. It must match this message. It does
not upgrade provider_status to Delivered or prove inbound SMS support.

`project` derives the exact current fields: message_id, provider_status, sent,
reserved, provider_delivered, human_received and sender_display. Apply them to
the original task result, its lightweight source/cycle index and current action
result; normalize saved index.reply_sent to sent explicitly, retaining the mapping.
`verify` requires saved.task/index/action_result readbacks, each read_verified,
with task_id/content_version bound to the original and these current fields matching. Bind its successful
outcome result to the owner's completion contract.

For the action page, keep approved configuration as a labeled immutable
"At approval" snapshot, and put current result/count/receipt/next action in a
separate current-result section. A pre-send unknown value may remain historical;
it must not appear as the current sender/receipt status after new evidence.
Do not change approved bytes, add active controls to a closed task, or fabricate
provider delivery from an operator's phone observation.

Summaries derive from these current canonical results; avoid a second manually
maintained zero-filled counter in RunSettings.internal_audit. Preserve old
internal_audit values only as labeled historical snapshots. Update service
Health at the end of the owner invocation from its real latest observation;
report generation is not a new probe. Coalesce each service update and reuse
unchanged captures to reduce Notion reads. Required fresh pre-action checks stay.

Projection saving failure leaves a partial-publication exception with the known
provider ID. The next permitted owner repairs only missing projections. A report
records the issue without repair. Never resend to make a display consistent.

The counts command takes current normalized outcome events plus account and an
explicit coverage_complete flag. It deduplicates by operation/account/message,
rejects conflicting current records, separates reserved/unknown attempts and
labels partial coverage. Feed those derived known totals to current summaries;
never count operation-log rows or infer global zero from an unavailable query.
