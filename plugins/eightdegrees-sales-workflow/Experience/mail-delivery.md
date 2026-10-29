# Mail reading, frozen bytes and reply transport

Scope: observed Gmail/Outlook behavior, last confirmed 2026-10-29. Evidence: B113 native-chinese-body, same-source-mime-recovery, preview-hash-orchestration, gmail-exact-MIME, outlook-actual-receipt.

## Native garbling is distinct from successful same-source recovery

The actual Chinese gb2312 message was garbled in the connector's full representation. Raw MIME from that SAME authorized message ID decoded successfully using the packaged strict helper, without reading attachments. Keep native capability degraded and record recovery separately. Do not use invented clean text, a different message or a guessed charset as evidence. An unrecoverable body stays pending and cannot supply customer facts or approval.

## Hash the bytes actually submitted

The local artifact writer appended one newline: 614 local bytes versus 613 uploaded bytes. The preview gate correctly refused the mismatch. Preserve one canonical byte source for upload, digest, preview mapping and send payload; write copies in binary mode or explicitly preserve UTF-8 bytes with no automatic newline normalization. Do not recompute a convenient digest over a changed approved artifact. Before approval, compare the actual upload input, upload download and saved embed download, then version any content change. The observed mismatch was corrected before review; it was not an approved-payload repair after sending.

## Gmail reply transport can add unapproved content

The observed Gmail send_email call with reply_message_id accepted the exact frozen HTML but automatically appended the original inquiry quote. The approved 613-byte HTML remained an exact prefix; the actual decoded sent HTML was 1172 bytes. The same-thread reply arrived in Outlook, so transport/receipt passed while full approved-body equality failed. This is an open adapter issue, not permission to mark prefix equality as exact equality.

Before final SendApproval, establish whether the current supported reply mechanism can suppress automatic quoting or deterministically expose the complete final quoted body for review. Only use an actually documented/verified capability; do not invent a no-quote flag, bypass the connector through hidden APIs or silently use a new unrelated message. If neither exact approved transport nor a frozen final quote can be verified, retain the draft with a specific capability limitation. A new consented, bounded TEST may verify a candidate adapter; older acceptance does not authorize another send.

After an already accepted send, compare actual decoded MIME, thread headers and receipt separately. A mismatch creates a quality finding while retaining the real provider ID. Repeated continuation reconciles that same attempt; it never resends to hide the mismatch. Outlook normalized body or provider acceptance alone does not prove original MIME, pixel rendering or delivery on another channel.
