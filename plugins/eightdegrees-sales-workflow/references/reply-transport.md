# Prepare once and send the stored reply

Create the reply draft once. If the connector adds quoted text, replace the
complete MIME on that draft once with reply_transport.prepare, preserving its
thread and returned message mapping; omit a new reply_message_id on update.
Use verify with write_result from the original successful write. No raw MIME
fetch or stored-body comparison is required. Preserve all approved parts/assets;
the packaged adapter handles one HTML part and refuses unsupported multipart
rather than dropping it. Unsupported transport is a scoped implementation issue.

The single [email review](email-flow.md) approves this exact draft, recipients,
materials and window. One email.dispatch checks current controls/attempts and
emits send_draft with the approved draft_id only. The original Gmail send response
ends dispatch. Never query Sent or delivery, regenerate approved content or send
again because logging/CRM/follow-up registration failed.
