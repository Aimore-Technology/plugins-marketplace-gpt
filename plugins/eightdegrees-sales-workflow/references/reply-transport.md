# Prepare one plain-text draft and send it once

New inquiry replies use mime_type=text/plain, text_base64url and text_sha256
with the existing scalar original source/thread/draft/header binding. Create
one reply draft; if automatic quotes need removal, reply_transport.prepare
replaces that draft's body once. It returns text/plain UTF-8 payload and omits
new reply_message_id on update to preserve the original reply context. Keep the
returned actual message mapping before freezing the approval package.

Use verify with the original write_result. API acknowledgement and draft ID
are sufficient; no raw MIME or saved-body comparison. Plain text needs no HTML,
rendering, preview, image, attachment or full brochure copy. A real existing
brochure link can be included when appropriate, without inventing a public URL.

The single [email review](email-flow.md) approves the exact text, recipients
and window. email.dispatch emits only send_draft(draft_id), never reconstructed
text. Successful Gmail acknowledgement ends dispatch; CRM/follow-up failures
recover independently and cannot resend the email.

One HTML part remains supported only for original legacy frozen approvals.
Never silently convert an approved HTML message or omit its approved assets;
unsupported multipart repair is scoped to that legacy item.
