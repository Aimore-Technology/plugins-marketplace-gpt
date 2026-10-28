---
name: eightdegrees-sales-reply
description: "Turn a verified customer project inquiry into a reviewed, versioned HTML/EDM reply using authorized Dropbox facts, then send only the exact approved files and window."
---

# Reply to a sales inquiry

Read [operating-contract](../../references/operating-contract.md) and [HTML approval](../../references/html-approval.md). Use [notion-model](../../references/notion-model.md) for tasks/drafts.

1. Reuse the inquiry, message ID, verified customer mapping and upstream communication summary; do not recreate notes or rerun the scan. Use [task presentation](../../references/task-presentation.md) to show current source/version, unresolved differences and verified vs missing setup dependencies. Identity issues go to ClientMatching, missing project/question facts to DataCompletion, contradictory material facts to ContentReview. Unrelated optional persona fields need not block preparing a supported reply.
2. Read the approved customer persona and operator email style/templates. Use only supported preferences and facts, not inferred budget, eligibility or promises.
3. Retrieve authorized Dropbox project sources: current price list, master/release plan and Engineer paying plan as relevant. Resolve explicit version/effective date; modification time is supporting evidence only. Preserve all old files. Missing source/version goes to DataCompletion; conflicting known sources go to ContentReview. Do not guess the current price or availability.
4. Address the actual inquiry, separating sourced facts from suggestions. Quotes for dispatch, delivery commitments, signing and payments remain the operator's manual work; do not put them into an automatic send path through ordinary approval.
5. Save editable subject/body in Notion and produce a matching versioned HTML file with frozen image/attachment versions. Create the Notion HTML-attachment preview, or same-file read-only image/PDF fallback, per html-approval. This is an implementation duty, not a customer technical decision. No approval before preview and editable copy agree.
6. Use ContentReview for edits/facts; SendApproval displays sender, To/Cc/Bcc, subject, rendered preview, files/version manifest and earliest/latest send window. The operator approves that exact version. Edits, asset/recipient changes or withdrawal invalidate approval; changed/expired window requires approval again. No regeneration at sending.
7. Reread the final decision, approved files, target/thread, latest accessible reply/stop state, time window and prior attempts. Stop for new replies, outdated evidence or mismatch. Submit the exact approved HTML/attachments through a verified Gmail send capability, preserving thread association. If that capability cannot send the approved file, stop for implementation/manual handling, never silently downgrade content. Record actual message ID/result and read back when supported; do not claim delivery from acceptance.
8. Save outcome and source/version links. Only a verified actual material-send event may start [SMS follow-up](../eightdegrees-sms-follow-up/SKILL.md). This skill owns this reply's send; the scanner must not also send it. Unknown outcomes require reconciliation; partial log failure does not resend.
