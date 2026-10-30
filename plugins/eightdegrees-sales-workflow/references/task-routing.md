# Explicit task owner and resume step

Category describes the operator issue, not its execution owner. A parent communication run can contain a sales draft/send task. Never default every task to communication processing or infer a resume action from a human title/category alone.

## Canonical route

New tasks store OwnerSkill (text), ResumeStep (text) and ResumeContractVersion=`resume-v1`, in addition to original TaskId, RunId, StepId, SourceKey, ContentVersion, Category, State and Mode. Workflow retains the existing parent/provenance meaning; it does not override OwnerSkill. Preserve verified parent/helper relationships for downstream persona work.

[task-routes.json](task-routes.json) is the machine route inventory, consumed by [offline checks](evidence-checks.md). Important examples:

| Paused work | OwnerSkill | ResumeStep |
| --- | --- | --- |
| Customer association | eightdegrees-communication-context-process | VerifyCustomer |
| Missing required communication facts | eightdegrees-communication-context-process | CompleteCommunicationData |
| Reviewed Notes and combined append | eightdegrees-communication-context-process | ReviewCommunication |
| Downstream persona sync recovery | eightdegrees-client-persona-update | SyncApprovedPersona |
| Unreadable mail / unsaved scan checkpoint | eightdegrees-email-scanning | ReadMessageBody / SaveMailCheckpoint |
| Project facts or source-version conflict | eightdegrees-sales-reply | ResolveProjectSources |
| Inquiry reply content review | eightdegrees-sales-reply | ReviewReplyDraft |
| Inquiry reply final send approval | eightdegrees-sales-reply | SendApprovedReply |
| Setup input | eightdegrees-initialization | ValidateSetupInput |

The inventory also includes general email, SMS, reminder, Calendar and brief steps. Use the correct existing route when constructing the task, not a generic wrapper's current Skill name. Validate owner/step/category fields BEFORE making a new task actionable. In action-page bindings, include OwnerSkill, ResumeStep and ResumeContractVersion; operators never fill these fields.

## Resume without conversational memory

1. Fetch the original task/current source, route fields and previous attempts. Validate the route under the actual invocation policy before accepting an action-page submission or dispatching a helper. Missing/inconsistent route stays pending; no fallback to a Notes append.
2. Read the named owner's Skill and run only the recorded unfinished step. If already inside that owner (for example a checkpoint in the current scanner), perform the step inline; do not recursively start the scanner or restart the whole workflow. A verified communication parent may call persona-update for its approved combined append, once.
3. Keep the original task/run/source IDs, completed steps, action page, exact approved version and all inherited restrictions. A final reply approval belongs to sales-reply; it cannot be consumed as communication Notes. Unknown external outcomes require original-attempt reconciliation before retrying that owner's step.
4. Respect command bounds. run-auto excludes Manual tasks and defers customer-send steps. add-communication continue handles its Manual communication tasks or a verified downstream persona step, not an unrelated sales send. reply-draft may resume source/draft preparation but cannot send. init upgrades/setup only; report only reads existing state and writes report/log. Return the primary action link and correct owner/next permitted entry when this invocation cannot continue. Do not rewrite Mode, cancel approvals or choose a broader policy to make a route executable.
5. Only after this routing check may the owner validate current submitted input, approval identity/version, source/preview, stop/window and completed attempts under existing contracts. Route eligibility never constitutes approval or proof that a customer message can be sent.

Separate input observation from business execution. A permitted run-auto may validate/record a submitted Automatic SendApproval choice through the verified owner in observe phase, then defer actual sending in execute phase. Pause/Cancel can be recorded without sending; valid approval may remain ApprovedPending. This overrides neither expiry/customer stop nor invocation restrictions. report-only/draft-only cannot consume send choices, and scanner exclusion of Manual tasks applies in both phases.

## Upgrade and ambiguous legacy records

During explicit init upgrade, add the fields and inspect only eligible open tasks. Recover owner/step from original source, draft/Notes payload, provider operation, parent run and existing approved scope. For example a frozen reply manifest plus the original send-review intent can establish SendApprovedReply despite an old parent Workflow value. Preserve that parent value and record route repair as metadata with its evidence.

Do not guess from Category=ContentReview or a friendly title. If original evidence is missing/conflicting, keep execution paused and surface a route-repair setup/exception task owned by initialization/ValidateSetupInput. Ask only which business action was intended, not for technical IDs. Keep the original task and successful steps; no duplication, old Notes rewrite or customer send.

Routing-only repair does not change approved bytes or manufacture approval. If it would change the action's meaning/scope, require a new decision. Existing action pages whose owner/step binding changes need a new verified binding/page before consumption; old checked choices do not transfer. In-flight legacy inputs remain on one original input authority until reconciled under operator-actions. Closed records remain historical, without forced migration.

### Communication data-completion upgrade

CompleteCommunicationData is a draft/Notion-input step, with DataCompletion/ExecutionExceptions categories, not the CRM-writing ReviewCommunication step. It validates/applies only the submitted scope and then hands off to a separate Notes ContentReview. On explicit init upgrade, repair an open legacy ReviewCommunication+DataCompletion route only when its original missing-field/source/apply evidence proves this intent. Preserve TaskId/RunId/source/Mode and existing results. Follow active-page binding migration rules; changed bindings get fresh unchecked controls, not transferred approval. In-flight legacy submissions keep one authority until reconciled. Completed historical tasks keep their actual results and failure history; a new valid route does not retroactively pass an old invalid route or justify another Note append.

## Registration versus continuation

Before enabling a new ordinary form, create its canonical task and use
`resume-task --phase register --policy <actual policy>` with its real PageId.
ValidResumeRoute checks only the owner/category/step/mode contract. It does not
consume a submission or satisfy a final completion route. Use execute/observe
with the actual continuation context later. Never change to setup-only or set
--explicit-continue merely to obtain a pre-form pass. scheduling-only cannot
resume PendingTasks, and start/stop do not need business-task routes.

## Native scheduled policy and send-result recovery

scheduled-approved-work requires the current actual schedule guard, supplied
to resume-task as --schedule-guard and bound to the configured operator. It
excludes Manual tasks in register, observe and execute phases. Route eligibility
still grants no approval. Customer sends need the named owner's full fresh checks.

RecordSendReceipt belongs to sales-reply; RecordGeneralSendReceipt belongs to
email-scanning. They reconcile an already-sent email's deterministic GHL result
and current projections under [send receipts](send-receipts.md), not another
send or Notes/persona intake. A report cannot dispatch them. Use the original
provider ID and frozen send package; expired send windows do not block an
authorized internal result backfill, and do not permit another customer send.
