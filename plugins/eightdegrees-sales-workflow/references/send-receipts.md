# Record actual email sending in CRM

Sales replies and general customer emails save their actual result in both
Communications and GHL Notes/activity log. This is a distinct system-result
receipt, not the earlier customer-facts Note and not a new persona proposal.

For the [unmatched inquiry path](inquiry-intake.md), an actual no-match has no
CRM target yet. Preserve the original accepted email and own Notion outcome;
leave RecordSendReceipt pending separately until target and receipt scope are
confirmed. Do not block an otherwise exact-approved source-bound inquiry send
solely for this no-match, render placeholder CRM IDs, claim CRMReceiptVerified
or repeat Gmail dispatch. Existing verified CRM targets retain the full receipt
requirements below. Actual multi-candidate/conflicting identities remain blocked.

Before final send approval, show that sending includes one internal CRM receipt
using send-receipt-v2: approved content/source reference, actual sender/recipient,
verified provider message/status/time and verified CRM customer. Freeze the
template version and field mapping in that send package. It adds no business
claims, recommendations, delivery promise or structured customer-field change.
Approval of this scope permits those deterministic observed values to be filled
after the send; no second approval is needed for unchanged system facts.

After the original successful Gmail dispatch response, use `send_receipt.py render` with the original
task_id, timezone, source_url, verified customer (location_id/contact_id/name),
approved (content_version/sender/recipient/subject/payload_sha256/receipt_template/location_id/contact_id)
and sent (same fields plus message_id/sent_at/status=Sent/read_verified=true).
The helper reuses the complete plain-text four-section CRM Notes template.
It rejects mismatched approval or unverified provider facts. Store the rendered
payload/hash on the original send attempt before appending.

The receipt_key is a stable digest of sender account plus immutable message ID;
it is independent of retry, report version or Notion page. Run `reconcile` using
complete scoped existing Notes and any pending receipt append attempt. An exact
existing receipt is reused; incomplete discovery, duplicate/conflicting receipts
or an unknown append stays NeedsReconciliation. Missing receipt is not permission
to send again. Save the CRM append AttemptId before one append, then `verify`
the actual note ID, target and exact body readback. Bind CRMReceiptVerified to
that task/content version before final email business completion.

If the email was sent but receipt/projection saving failed, retain provider Sent
and expose CRMReceiptPending/Unknown separately. Create/reuse ExecutionExceptions
owned by the original email owner at RecordSendReceipt. Resume only that step;
never call send_draft again. A paused customer stays paused: internal result
backfill does not send another customer message or start a follow-up cycle.
This step can complete with the original immutable receipt scope even after a
send window expires because it sends nothing.

For legacy unsent approvals without this receipt scope, prepare a new explicit
send package before using the expanded behavior. For already-sent legacy mail,
retain its successful result; get only the missing receipt scope confirmed if
needed, never reapprove/reopen the send. A test's artificial Note-count cap
must be raised for this designed receipt or reported as receipt-pending, not
used to claim full post-send CRM acceptance.

Preserve already-approved send-receipt-v1 and existing CRM Note bytes. The
helper still renders that legacy template from its original saved Sent response;
it does not query Gmail to obtain evidence. New approvals declare v2, which
records ProviderAccepted or Sent exactly and says handed to Gmail. Never edit
a past approval or append a second Note merely to upgrade its wording.
