# Complete the current step before admitting its successor

Apply [current API result policy](api-result-policy.md). Routine successful writes need only acknowledgement and record IDs, including CRM; older body/readback comparisons below apply only to frozen history or explicit diagnostics.


Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

An owner plan is a completion contract for one current ResumeStep, not an entire
customer journey. Never put a future send or maintenance task in the executable
task roles of a content-review plan. A shared owner or parent run does not make
those steps one completion unit.

New preparation produces execution-v2. Each task resource declares its actual
resume_step and content_version. The helper checks the route owner, rejects mixed
steps and derives phase-specific evidence. Route checks must match the frozen
step and current policy. Final owner-write rejects mixed legacy routes too;
it does not reinterpret a future task as already executed. Legacy multi-task
plans lack frozen step bindings and are refused at ready before dependent work;
single-task legacy readback stays compatible.

| Current phase | Complete using | Successor |
| --- | --- | --- |
| ReviewReplyDraft | Accepted exact content/version, current stored draft, canonical task summary and action consistency | Complete and read back this review before preparing the independent send phase |
| SendApprovedReply | Fresh original review completion and exact send approval, window/stop/attempt checks before dispatch; verified draft and original provider acceptance, outcome, CRM receipt, material handoff and linked presentation for final completion | Register the SMS cycle after successful material-email handoff; SMS has its own owner plan |
| SendGeneralReply | Exact approved draft and original provider acceptance, outcome and CRM receipt | Any further work has its own step |
| PrepareSmsFollowUp | Verified material Sent and its saved cycle/due/blocked result; no SMS request proof yet | SendNotificationSms under standing permission when eligible |
| SendNotificationSms | Standing authority and the matching actual request outcome; SentToNetwork completes sending | Maintenance/next due work remains separate |
| RecordSendReceipt / RecordMaterialHandoff / RefreshEmailOutcome | The named original unfinished result projections and their current verified readbacks | Never replay the provider action |

ReviewReplyDraft must not require reply-sent, CRM send receipt, material-handoff
or email-presentation. Those results cannot exist before sending. It still
requires the actual stored draft and the existing original approval checks.
Preparation generates all minimum send/recovery evidence even when omitted by
the caller; final owner-write rejects deleted or wrong-phase obligations.

After a review succeeds, save its final state, read back the original review and
its accepted decision, then persist/read back a separate send-phase plan. Reuse
the original send task/action if already registered; do not create a duplicate
approval. Completed review/action pages are publication dependencies of the
send phase, never executable review tasks in that phase. SMS cycle registration
does not require a later SMS to be sent before the email can finish.

Each transition updates both the canonical task's plain current summary and its
active action/result. Run notion.task-summary on the original task properties
and body, and notion.task-display on its registered action. An accepted decision
must say accepted/next step/actual blocker, not awaiting the same approval.
Keep submitted answers, historical approval and frozen content unchanged. A
workflow fault identifies the maintenance action; it does not ask the operator
to submit the same decision again. A no-change scan retains that blocker instead
of retrying the same failed completion request.

## Recover a pre-upgrade mixed plan

Keep the original failed plan, refusal, task IDs, approved bytes and accepted
decisions. Record the phase-scope defect and a correction link on the original
owning run/log. Before unfinished work, generate and persist a new execution-v2
phase run linked to that incident and the same original current task/version.
This is prospective repair of an invalid phase boundary, not a replacement of
past evidence or retrospective proof of success. Preserve all checks relevant
to that step and all future checks in the successor's separate plan. Never edit
the old plan, delete its refusal or mark its full journey complete after only
review recovery. Leave a parent journey waiting until its actual remaining work
finishes; a phase run may complete independently.

Reread original decisions, edits/withdrawals, exact current draft, stops, prior
attempts and window. Reuse an unchanged valid accepted confirmation; request a
new decision only when its actual content/recipient/window or authority changed.
If Sent already exists, recover only the named original receipt/handoff/display
work. No new send repairs a phase contract. The helpers are offline preflights;
live model/tool ordering and the recovered original workflow still need testing.

Use [prospective action gates](pre-action-order.md) before opening new email
review controls or emitting outgoing call arguments. A post-action check cannot
repair missing historical order. Run these only on the affected event phase.
