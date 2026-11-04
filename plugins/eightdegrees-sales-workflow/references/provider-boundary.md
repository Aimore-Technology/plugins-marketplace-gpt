# Dispatch completion boundary

Apply [current API result policy](api-result-policy.md). Routine successful writes need only acknowledgement and record IDs, including CRM; older body/readback comparisons below apply only to frozen history or explicit diagnostics.


Gmail and AndroidSync own transport after a successful dispatch response. Our
job is to prepare, authorize and hand off the correct request quickly, then
finish our own records. This policy is `provider-handoff-v1` and applies to both
new sends and recovery of an already acknowledged original request.

1. Before dispatch, verify our customer/recipient, approved email version and
   stored draft/preview, standing SMS authority, current stop/window/count rules,
   configured account/device and durable attempt/idempotency identity.
2. Call the sending tool once. Inspect its original success/error envelope and
   retain its actual request ID/status. A successful `send_draft` response ends
   email dispatch; an AndroidSync accepted request ends SMS dispatch, including
   AwaitingPhone or PendingApproval. Those raw states describe AndroidSync's
   responsibility, not another task or approval for our workflow.
3. Use `provider_handoff.py verify` / `provider.handoff` on the original response
   and our previously verified request. This is an offline identity check, not
   a second service call. Store `email-handoff-proof` for email. Freeze evidence
   kind `provider-handoff` in new send plans. Preserve old Sent/Delivered proof
   as history; never recreate it by probing an accepted request.
4. Record Completed/handed off once and count the request once against the send
   cap. Preserve raw external status separately. In current outcome records,
   `sent=true` means successfully submitted to the sending service, not network
   transmission or receipt. Use Submitted to Gmail/AndroidSync in current UI.
5. Finish our Notion result, source index, monitor/log and automatic material
   follow-up registration from that same response. These are our records: verify
   their original API success and returned IDs. CRM also finishes with the original successful API acknowledgement and NoteId; no body readback is required.

Do not query Gmail Sent/raw MIME after sending, search the receiving mailbox,
poll AndroidSync message status, wait for SentToNetwork/Delivered, ask a person
to check a phone, or create receipt-only follow-up work. SentToNetwork remains a
successful historical observation, but obtaining it is not required. A missing
external delivery observation creates no pending/quality/failure item.

An explicitly rejected dispatch is not a handoff. A timeout/ambiguous response
stays an unknown original attempt, never permission to resend or a reason for
automatic provider polling. A malformed/missing documented response ID is an
internal recording exception: retain the original response and attempt, do not
fabricate an ID or turn recording repair into another send.

Keep normal inbound scanning and customer reply/stop processing. It is business
input for future work, not delivery verification of a closed send. Important
reminder acknowledgement remains a separate business task; it never reopens
the dispatch. A known stale internal view may be repaired using the original
acknowledgement without external probes or changing approvals/payloads/stops.

For email handoff the helper takes operation=email, manifest, draft_verification
(the actual phase=draft StoredReplyVerified output), request={draft_id}, and the
original response. For SMS it takes operation=sms, the original frozen
notification, authority=SMSNotificationVerified, exact request and original
response. Its ProviderHandoffVerified binds task/version/request and provider ID;
it cannot replace pre-dispatch authority or CRM readback.

Use the actual acknowledgement time as accepted_at and for internal follow-up
delays. Legacy sent_at/last_sent_at fields may carry that handoff time under
this policy, explicitly labeled as submission time, never as network/delivery
time. Internal count fields with sent in their name count accepted requests
once; preserve older snapshots with their original documented definition.
