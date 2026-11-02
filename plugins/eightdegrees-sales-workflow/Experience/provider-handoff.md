# Successful handoff ends dispatch

Current policy from the operator, 2026-11-02: Gmail owns mail transport;
AndroidSync owns SMS transport. Our work finishes after the correct authorized
request is accepted, our result/monitor/log is saved, and required CRM writes
are read back. Do not turn delivery observation into another project.

The 0.1.31 seven-cycle simulation illustrates the wasted boundary: the SMS
request was accepted but Notion remained AwaitingPhone, while a separate
controller status read later returned SentToNetwork. The latter probe and an
Outlook receiving-mailbox inspection are not acceptance requirements going
forward. Preserve that historical report rather than rewriting its observations.

Use [provider-boundary](../references/provider-boundary.md). Freeze a single
AttemptId, original successful tool response and exact request binding; close
our task and count that one request. No post-send MIME/status lookup, handset
confirmation, receipt-only task, or repeat permission/send. Customer replies
still enter normal source/stop processing. Record internal save defects and
CRM readback errors honestly; repair our records only. This is a boundary
change, not proof that a later provider transmission or receipt occurred.
