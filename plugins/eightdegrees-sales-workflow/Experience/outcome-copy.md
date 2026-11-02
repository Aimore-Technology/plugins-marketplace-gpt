# Completed pages must not freeze other-channel state

Current policy: [provider handoff](provider-handoff.md). Historical delivery/receipt probes below are observations, not instructions to repeat them or completion requirements.

Evidence: controlled 0.1.19 run, Q19-03. An email completion page still said
"SMS not sent" after its separate SMS reached SentToNetwork and a customer
reply confirmed email receipt. Per-message normalized fields had passed.

Keep current copy channel-local. Link SMS/receipt/stop evidence to its original
record instead of copying an undated negative into every completed email page.
Unknown receipt observations need their actual evidence time; preserve approval
and send-time snapshots as history. New receipt evidence never implies SMS
delivery or a right to send again.

Before send-result completion, outcome verify checks the actual registered
action page's two current sections as well as task/index JSON. A stale-copy
refusal repairs presentation only, preserving provider IDs, exact payloads,
approvals and stop controls. The offline patterns do not prove arbitrary prose
correct or intercept a model's tool call; live acceptance remains necessary.

Evidence: the 0.1.24 single-customer controlled run on 2026-11-01 kept a completed content review saying unsent after actual Sent, and the original email outcome missed a later explicit customer receipt. Terminal task filtering prevented those pages from becoming normal queue work. The initial send now requires linked email-presentation evidence; later receipts/stale results use a distinct RefreshEmailOutcome maintenance item. Originals remain terminal, approvals/provider proof stay intact and no CRM/send replay is allowed. Offline plan/patch/readback regressions cover this path; live model behavior still needs acceptance.

## SMS completion policy

SentToNetwork is sent. Avoid primary copy such as delivery unconfirmed or handset
receipt pending after successful sending. Do not create a phone-confirmation
request or keep polling for Delivered. Preserve optional delivery evidence as
detail; the send result is complete without it. Email receipt, channel setup and
inbound reply capability remain independent.
