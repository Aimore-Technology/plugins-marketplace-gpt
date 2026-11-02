# Exact stored-draft reply transport

Use for Gmail customer replies before ContentReview/SendApproval and again before a permitted send. The observed direct send_email(reply_message_id, payload) appends a quote, so it is not the default exact-body reply adapter. The current supported update_draft contract replaces the MIME tree without appending quotes; send_draft sends the stored draft. Verify those actual capabilities in the current host. No raw API/SMTP workaround or invented no-quote flag is authorized.

## Prepare before approval

1. Freeze the intended UTF-8 HTML bytes from authorized facts, with their SHA-256 and content version. Preserve exact trailing newlines. Resolve original Gmail message ID, thread ID and RFC Message-ID plus exact sender/To/Cc/Bcc/Reply-To/subject. No model regeneration during send.
2. Create ONE unsent Gmail reply draft with the actual reply_message_id and source context; register the returned draft ID and its underlying message ID immediately. Creation may add a quote. It is not yet review-ready. Unknown creation preserves returned IDs and requires reconciliation; do not create another draft to obtain cleaner evidence.
3. Call update_draft on that actual draft ID with the complete frozen MIME tree, exact headers and body bytes. OMIT reply_message_id to preserve the existing reply context. The current sparse patch contract explicitly says replacing payload does not append quotes. Update the binding from its returned draft/message IDs: replacing a draft may change its underlying message ID. This setup occurs before any approval. Clear unwanted Cc/Bcc/Reply-To explicitly rather than retaining unapproved recipients.
4. Fetch the current underlying message with read_email(format=raw). Verify the stored draft ID-to-message mapping, DRAFT label, thread, In-Reply-To/References, headers and transfer-decoded body bytes. Existing [reply_transport.py](../scripts/reply_transport.py) prepare/verify operations generate the exact HTML-only update arguments and check original captures. If mapping/readback or exact bytes cannot be verified, leave the draft pending; do not ask the operator to approve an unverified transport.
5. Build the Notion editable copy/native preview from these same frozen bytes. Bind draft_id, current message_id, original reply_message_id/thread/RFC ID, recipients, subject, HTML digest, asset manifest and draft_binding_sha256 to the actual review version. Show the exact stored contents and preview in separate content/send action pages. A draft created before content approval is an unsent preparation artifact, not customer delivery. User edits require a new review version; preserve already approved prior drafts/history without silent edits or auto-deletion.

Here content_version is the canonical task ContentVersion/send-package version; retain a separate HTML file version if different. The digest still binds the exact frozen HTML bytes.

The offline helper takes `manifest` fields task_page_id, content_version, draft_id, message_id, thread_id, reply_message_id, parent_rfc_message_id, from_address, to, subject, html_base64url and html_sha256; cc/bcc/reply_to default empty. `prepare` prints update_draft args only. `verify` also takes the original `draft` response containing its current message mapping, and original raw `message` fetch. It returns StoredReplyVerified or NeedsCorrection, with an immutable binding digest. It grants no approval or send authority.

## Send the approved object

Immediately before permitted dispatch, fetch the original Notion task/active action and current raw draft again. Recheck exact stored draft binding/version, payload/headers/thread, approval/window, latest replies/stop and original attempts. Include this phase=draft StoredReplyVerified evidence in the send owner's frozen completion contract. A changed/vanished draft or added quote suspends execution; do not repair an approved draft and send it under old approval.

Persist AttemptId and that exact draft ID/digest before dispatch. Use send_draft with ONLY the approved draft_id, not send_email with reconstructed HTML. Apply invocation restrictions: reply-draft/report and explicitly restricted no-send scans do not send; public one-cycle-approved-work may execute only independently approved Automatic sends after the same fresh checks. Unknown send results reserve the attempt; a missing draft after send may mean it was consumed, not that sending failed. Record the original ambiguous attempt for operator handling; do not automatically query the provider or retry. Do not call send_draft again to test deduplication.

After the single successful send_draft response, retain its actual ID/status and
use [provider handoff](provider-boundary.md). Freeze provider-handoff evidence
from provider_handoff.py, the original response and pre-dispatch draft check.
Persist email-handoff-proof, finish our Notion outcome/CRM receipt/material
registration and stop. Do not fetch sent MIME or inspect a receiving mailbox.
The older phase=sent adapter is for reading existing legacy evidence only, not
an instruction to obtain new external verification. Never repeat dispatch to
repair a missing internal field.

## Assets and limitations

The packaged helper verifies a single text/html part with no assets/attachments, covering the observed acceptance reply. It refuses a nonempty asset manifest or unexpected MIME tree instead of dropping files. For image/CID/attachment EDM, use the SAME create/update/readback/send-stored-draft mechanism with a separately verified complete frozen MIME tree and asset mapping under html-approval. If that verification is unavailable, disclose the narrower supported capability and keep the affected package pending. Never silently downgrade or mark all EDM transport accepted from an HTML-only fixture. Connector-contract review and offline fixtures do not establish a live provider-handoff pass.

## Deterministic parameter preparation

Use [execution preflight](execution-preflight.md) with operation reply-patch and
the actual reply manifest. From/To/Cc/Bcc/Reply-To/Subject are header strings
under this adapter, never lists or null. An invalid type returns no patch plan;
do not guess a conversion or change approved recipients. Use the returned
reply_args with the current tool schema, then retain raw stored-draft verification.

Use [prospective action gates](pre-action-order.md) before opening new email
review controls or emitting outgoing call arguments. A post-action check cannot
repair missing historical order. Run these only on the affected event phase.
