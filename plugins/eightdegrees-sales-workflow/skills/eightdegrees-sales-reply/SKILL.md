---
name: eightdegrees-sales-reply
description: "Turn a verified customer project inquiry into a reviewed, versioned HTML/EDM reply using authorized Dropbox facts, then send only the exact approved files and window."
---

# Reply to a sales inquiry

Before saving extracted/clarified customer boolean facts or persona snapshots, apply [customer fact semantics](../../references/customer-facts.md) and run the fact helper on the actual proposal. Unknown is null, never a default false.

Before dependent writes, use [execution preflight](../../references/execution-preflight.md) to generate, persist and read back this owner's affected-role plan; a failed preparation stops the phase. Apply the [owner completion contract](../../references/owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action. Before EVERY Notion page write, including the first create and progress/result properties, run [exact-call preflight](../../references/notion-mutation.md); only use its returned unchanged arguments after exit 0 and NotionMutationPrepared.

Register sales-reply as OwnerSkill for project-source tasks (ResolveProjectSources), reply-content reviews (ReviewReplyDraft) and final send approvals (SendApprovedReply), using [task routing](../../references/task-routing.md). Parent Workflow may remain communication; it is not the executor. A resumed task/action URL must validate that explicit route and continue only the unfinished step. Missing/conflicting owner/step stays pending without communication fallback or duplicate Notes. Existing draft-only/no-send invocation restrictions still apply.

Before freezing or dispatching a reply, read [mail transport experience](../../Experience/mail-delivery.md), especially automatic quote mutation; prefix equality is not exact approved-body equality.

Read [operating-contract](../../references/operating-contract.md) and [HTML approval](../../references/html-approval.md). Use [notion-model](../../references/notion-model.md) for tasks/drafts.

For step 5 preview creation/repair, read [preview evidence](../../Experience/preview-evidence.md); use [image-preview](../../references/image-preview.md) for the frozen-HTML native PNG path. Inspect both fetched reference maps and download the actual saved asset before judging preview support. Preserve existing customer stop/Pause and review-version boundaries.

1. New inquiry/draft/review/send tasks use Mode=Automatic so their submitted Notion inputs resume through public run-auto or the verified scheduled executor. Do not change existing Manual modes. Reuse the inquiry, message ID, verified customer mapping and upstream communication summary; do not recreate notes or rerun the scan. Use [task presentation](../../references/task-presentation.md) to show current source/version, unresolved differences and verified vs missing setup dependencies. Identity issues go to ClientMatching, missing project/question facts to DataCompletion, contradictory material facts to ContentReview. Unrelated optional persona fields need not block preparing a supported reply.
2. Read the approved customer persona and operator email style/templates. Use only supported preferences and facts, not inferred budget, eligibility or promises.
3. Retrieve authorized Dropbox project sources: current price list, master/release plan and Engineer paying plan as relevant. Resolve explicit version/effective date; modification time is supporting evidence only. Preserve all old files. Missing source/version goes to DataCompletion; conflicting known sources go to ContentReview. Do not guess the current price or availability.
4. Address the actual inquiry, separating sourced facts from suggestions. Quotes for dispatch, delivery commitments, signing and payments remain the operator's manual work; do not put them into an automatic send path through ordinary approval.
5. Prepare and verify the actual Gmail stored reply draft under [reply transport](../../references/reply-transport.md) before approval: create once, replace full MIME via update_draft (no new reply_message_id), retain actual returned message mapping, and read raw headers/body. Save editable subject/body in Notion and produce a matching versioned HTML file with frozen image/attachment versions. Place the uploaded HTML as an actual native embed, or verified same-file read-only image/PDF fallback, per html-approval. Follow [Notion publication](../../references/notion-publishing.md): fetch the saved page, verify the native block/source and exact asset bytes, then verify agreement with editable copy BEFORE making either content/send review actionable. Upload URI/hash/external screenshot alone is insufficient. A missing preview keeps a non-approvable draft; repair any previously invalid review through a fresh version/page without inheriting choices or releasing Pause. This is an implementation duty, not a customer technical decision.
6. Use separate dedicated [action pages](../../references/operator-actions.md) for ContentReview and SendApproval. Content input never supplies send approval. The send page displays the exact sender, recipients, subject/body, usable preview/files and window with an explicit send decision and named submission to-do; technical actor/version fields stay on the canonical task. Include the deterministic send-receipt-v1 CRM result scope and template mapping from [send receipts](../../references/send-receipts.md) in the send package; this is not a second business-facts Note. New content/asset/recipient/window versions need new review pages with blank choices. Edits or withdrawal invalidate approval; no regeneration at sending.
7. Reread the original task, registered active action-page inputs/accepted decision snapshot, approved files, target/thread, latest accessible reply/stop state, window and prior attempts. Stop for changed inputs, new replies, outdated evidence or mismatch. Verify the same approved stored draft again and submit it with send_draft(draft_id) only when invocation scope permits; never reconstruct it through direct send_email. Include phase=draft StoredReplyVerified in this owner's completion evidence. Preserve thread association; if the approved file cannot be sent, stop for implementation/manual handling, never silently downgrade. Record actual ID/result and read back when supported; acceptance is not delivery.
8. Save outcome and source/version links in Communications and GHL. Apply [send receipts](../../references/send-receipts.md): after verified Sent, append/reuse one deterministic plain-text result receipt, read it back, and preserve its provider/message/Note IDs. Failed or unknown receipt saving creates RecordSendReceipt recovery on the original owner, never another send. Apply [outcome state](../../references/outcome-state.md) to keep the original task, lightweight source index and current action result consistent before final completion. Finish each source/review/version/decision transition by synchronizing canonical task summary/binding and active action status under Notion publication. Verified Today linked views follow these fields without a duplicate queue write; only legacy queue mode replaces its one queue link in this owner invocation. Preserve old pages/history and repair missing projections without repeating a business write. After EVERY verified actual material Sent event, automatically call the registration-only phase of [SMS follow-up](../eightdegrees-sms-follow-up/SKILL.md) under [material handoff](../../references/material-handoff.md). Persist and verify the original cycle/due/draft or explicit blocked/stopped result before final owner completion. Include material-handoff evidence on the original email task in the predeclared send plan. A receipt failure does not suppress registration; save both independent recovery steps without another email. No user command, second approval question or per-email native schedule is needed. Registration never approves/sends SMS or enables its channel; unknown email results never enroll. This skill owns this reply's send; the scanner must not also send it. Unknown outcomes require reconciliation; partial log failure does not resend.

## Phase order

Before accepting content or registering its successor, apply [phase ordering](../../references/phase-ordering.md).
ReviewReplyDraft owns only its original review task/action and stored draft checks;
it must complete and be read back without any Sent, receipt or SMS evidence.
Then prepare a separate SendApprovedReply phase, reusing any original existing
send task/action. Verify the completed matching review before external dispatch.
The review pages become publication dependencies, not executing task roles in
the send plan. Actual Sent, receipt, handoff and linked presentation remain send
completion requirements. Registration of a blocked SMS cycle is sufficient for
the email handoff; later SMS sending never gates email completion.

For a legacy mixed-plan refusal, preserve it and the original accepted decisions;
use the documented new linked prospective phase-run repair. Do not edit the old
plan or reopen completed tasks. Synchronize both canonical current copy and its
active action after each decision; task-summary and task-display must pass.

## Current outcome copy

For ResumeStep=RefreshEmailOutcome, perform only the scoped recovery in
[email presentation](../../references/email-presentation.md), then return. Do not
enter the inquiry/draft/send/CRM steps above. Before initial SendApprovedReply
completion, also use that check to synchronize its linked completed content
review and freeze email-presentation evidence. New explicit customer receipt is
a later presentation event; it never upgrades provider delivery or reopens sending.

Use [channel-local outcome text](../../references/outcome-state.md) for completed records. Keep other channels in their original linked records, and date receipt observations. Outcome verify requires the actual registered action-page fetch, not just normalized JSON; display repair never sends or writes another CRM Note. Preserve approved/history sections and current stop controls.

## Operator path and local checks

Apply [operator experience](../../references/operator-experience.md) for Today, short review summaries/differences, verified prefill and explicit post-submit guidance. Give concise chat progress at meaningful stages; an internal read/check does not require another Notion status write. Run [local check batches](../../references/local-check-batch.md) over unchanged original captures instead of repeatedly serializing/rereading them. Preserve every required fresh external-action and saved-result check. Verified Today linked views replace manual queue snapshots; legacy queue mode remains until explicit upgrade.

## Persist compatible send records

Use [record contracts](../../references/record-contracts.md) at content acceptance,
Sent proof saving and RecordMaterialHandoff recovery. Validate the downstream
record shape before a send; the saved original approval/bytes remain immutable.
Persist actual Sent and its registration event before optional linked-display
maintenance. Reuse unchanged captures in one local batch, not repeated plans
for each progress sentence. If post-send work does not fit, save one original
recovery pointer; next run-auto repairs it without a provider/CRM replay.
