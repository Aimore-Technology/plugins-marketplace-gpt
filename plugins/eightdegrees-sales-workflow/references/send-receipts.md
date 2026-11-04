# CRM send-result receipt

After Gmail accepts the exact approved draft, send_receipt.render builds the
fixed plain-text operational Note under send-receipt-v2. Keep the immutable
sender/message key, real CRM LocationId/ContactId and source/version. The single
email approval includes this result-record scope; it does not permit new facts
or persona changes. An unmatched CRM inquiry can keep recording pending.

Append/reuse once. send_receipt.verify with write_result confirms API success
and NoteId, without body readback. Existing successful receipts are reused;
unknown attempts reconcile only original existence. A CRM failure does not
replay email or suppress standing-authorized SMS registration. Recover that
one original RecordSendReceipt step when its real target/result becomes known.
