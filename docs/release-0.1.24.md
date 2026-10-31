# EightDegrees Sales Workflow 0.1.24

The operator now submits work in Notion and the shared run-auto/native queue
resumes it without a second continue command. P0-A still starts manually and
keeps Mode=Manual provenance. Current manually initiated communication review/data
can be observed; execution needs its durably saved accepted snapshot bound to
the original task/action/version/operator. Unsubmitted, superseded, paused or
ambiguous work cannot become approval. Legacy restricted invocations remain narrow.

run-auto scans configured Gmail/reply sources, available SMS replies/stops,
current Notion inputs, relevant Dropbox source versions and due follow-up/
reminder/confirmed-appointment work. It enqueues newly ready owner steps in one
bounded cycle, without scanner recursion, duplicate keys or sleeping for future
due times. Coverage/capability/budget limits remain explicit and checkpointed.

Factual notification SMS defaults to enabled notification-sms-v1 standing
authority, with no individual ContentReview/SendApproval or second chat question.
Generate/edit, freeze and send when due. The new offline helper checks current
policy, original task/body/version/target/device and allowed notification intent;
completion additionally matches the actual request body digest to its outcome.
Email/CRM review, capability, reply/stop, time/count and unknown-attempt guards
remain. Existing disable/revocation, stopped cycles and actual provider history
are preserved. Permission is separate from actual channel readiness.

ScheduledWork is an additive machine-queue Category in the existing PendingTasks
database; the five human issue views stay. Ready notifications have read-only
queued/result pages, not approval forms. Explicit init upgrade binds actual
policy/root/operator/device and adds complete machine-queue discovery without
creating a schedule. Eligible unsent factual legacy SMS can use the new route
while preserving IDs/mode/history; unknown/closed/stopped work is not reopened.

Both editions pass 316 offline tests, marketplace checks and deterministic ZIP
inspection. Added tests cover submitted Manual queue observation/execution and
binding mismatches, native guard requirements, notification standing permission,
revocation/scope/target/text/version, restricted invocations and final body-digest
consistency without a human decision. No live Notion changes, outbound messages,
native job or new runtime/end-to-end acceptance was performed for this release.
