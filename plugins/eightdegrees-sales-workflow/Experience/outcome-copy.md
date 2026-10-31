# Completed pages must not freeze other-channel state

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
