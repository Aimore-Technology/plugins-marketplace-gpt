# Testing and evidence

Current policy: [provider handoff](provider-handoff.md). Historical delivery/receipt probes below are observations, not instructions to repeat them or completion requirements.

Evidence: directed batches 0.1.12 and 0.1.13. Purpose: assess workflow reliability without counting helper tests as live acceptance.

| Batch | Scope | Passed | Failed | Waiting | Untested |
| --- | --- | --- | --- | --- | --- |
| 0.1.12 | 36 cases; publication regression; no new mail/send | 25 | 3 | 1 | 7 |
| 0.1.13 | 50 cases; adds actual inbound, HTML reply and SMS | 33 | 11 | 1 | 5 |

These are historical observations, not this installation's readiness. Different case inventories and grouping prevent a direct reliability trend from raw Failed totals. Broader scope found new transport behavior, while parameter/anchor/gate mistakes also recurred. Do not dismiss the increase as simply stricter testing.

## Classify a failure before prescribing a fix

Keep one primary category and secondary causes for each case family: package contract gap, connector behavior/limit, execution orchestration, or test assertion/artifact bug. Mark new, recurrent and known degraded capability separately. Preserve failed observations after recovery; successful recovery is another result, not removal of the original failure. Avoid deriving unique-defect counts from aggregate cases that group several requests together.

Record the case inventory and stable failure-family IDs before the next focused regression. Compare the same prior-failure set separately from newly added channel cases. Use explicit expected assertions and distinguish expected negative cases from accidental real refusals. Record count, invocation, actual request/result, affected version and whether anything was externally submitted. The B113 classification is 5 orchestration families, 3 connector/known-behavior families, 2 newly exposed channel-adapter families and 1 route-inventory family. Mixed causes remain visible; this is triage, not 11 isolated new product bugs or a declaration that any group is harmless.

## Passing a helper is narrower than executing a workflow

Offline unit/capture tests establish only the tested helper behavior. Check actual runtime call order, use of the helper before its dependent step and the saved record. A model may omit a correct helper or construct a bad call outside it. Track instruction-following failures explicitly; a tips library is not code enforcement.

Separate business result, publication quality, provider acceptance, recipient receipt, host visual, SMS network state and actual inbound replies. In B113 email receipt passed, full sent-body equality failed, and the SMS reached SentToNetwork with delivery still waiting. A report's publication Success is not a green business acceptance result. No inbound SMS tool means no MCP two-way proof. Prior stop/Pause, unknown-result reconciliation, current command restrictions and actual operator authorization remain in force.

After verification, record the actual actor/simulation label and result time. Preserve old Note objects, contact fields, task IDs, source mapping and earlier error/correction events. Do not clean the workspace or resend a real message to produce an easier passing report.

Current SMS acceptance uses SentToNetwork as sent/completed. Earlier test logs
mentioning delivery still waiting do not establish a required workflow step.
Do not repeat physical phone checks or mark sending partial solely because
Delivered/human receipt is absent. Keep original observations as history.
