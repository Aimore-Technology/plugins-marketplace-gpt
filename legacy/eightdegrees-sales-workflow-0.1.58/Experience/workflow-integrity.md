# Workflow integrity

Scope: route and completion evidence, independent of connector success. Evidence: B113 communication-data-route, earlier-owner-completion-contract. Status: historical failures; route and completion adapters implemented in 0.1.15, live owner acceptance still pending. This card enforces no runtime lock.

## Validate before making a form actionable

The tested communication DataCompletion task used ReviewCommunication. The shipped route inventory permits ContentReview/ExecutionExceptions for that step, so the original Waiting task failed resume-task. The test had already consumed inputs before checking it. Successful data saving cannot establish valid routing.

Before task/form registration, validate OwnerSkill, ResumeStep, Category, Mode and current invocation policy against the actual task-routes inventory. Repeat before input consumption and owner dispatch. A genuinely missing route is an open package defect: suspend the affected task and report the missing contract. Do not invent a step, relax its category, relabel the task to fit, fall back to Notes, or mark it Completed merely to obtain Deferred. A terminal-task check cannot retrospectively validate its original Waiting route. Retain the original source/run/approved scope and already verified business results.

Implemented in 0.1.15: CompleteCommunicationData owns only communication data application/Notion readback, followed by separate ReviewCommunication approval. Existing malformed routes still fail until a verified explicit upgrade; completed history is not rewritten.

## A check must run at its dependency boundary

Some early setup/manual/scan owners checked display text but registered Completed without freezing all required checks or running completion-gate. The later report did use the new gate correctly and blocked an actual bad saved link. That does not retroactively validate earlier owners.

At each owner entry, identify its actual required dependency checks before work. Persist immutable input/attempt results before dependent mutations. Before publication completion, check every current status/result/input surface and required saved page against the same canonical version. Capture integer process exit AND structured result; missing, stale, skipped and malformed evidence blocks completion registration. Pass the full current completion input when the reporting preflight requires it. A correct header cannot excuse a stale Not submitted result or active prompt below it.

The 0.1.15 owner-write helper applies owner-specific minimum checks, current bindings and frozen contracts across all seven owners; every owner Skill now directs its use. It does not prevent a model bypass at the host layer. Verify the original audit order: frozen contract, actual checks, gate, then completion event. Do not reconstruct a fictional earlier contract after execution. Report existing provider success even if publication remains incomplete, repair only missing projections, and append a correction for a premature Success rather than repeat a business action.

## Realistic-business run lessons

Evidence: the 0.1.15 realistic-business run. 'Finance not confirmed' was first
projected as false, then corrected to null before review. Apply the customer-fact
helper BEFORE any projection write. Notes business sections briefly narrated
Manual continuation and settings; keep those details in Notion logs and use the
business-prose renderer guard before review. For new form metadata use register
phase with the actual policy/PageId; don't invent Manual continuation or use a
setup policy. These offline safeguards still need live owner-order verification.
For read cost, freeze affected targets and reuse unchanged captures only within
the same invocation/phase; mandatory fresh approval/attempt checks remain.

## Approved-cycle and outcome lessons

Keep public manual scans and native approved-work invocations distinct.
Do not run a no-send shortcut from a task intended to execute approved work.
Never broaden scope from a customer message or an old lifecycle after upgrade.
The 0.1.16 run also exposed stale reply_sent/counters and conflicting candidate
query/original states. Follow outcome-state for per-item reconciliation and
verified projections; never rerun a provider action to make a summary green.
Current result text and historical approval-time unknowns need distinct labels.

After verified material Sent, enforce [persisted handoff](../references/material-handoff.md) before final email-owner completion. Readiness may block SMS dispatch but must not suppress cycle/draft/task registration. Reconcile a missing handoff with original provider/cycle IDs; do not resend the email or start a new per-email schedule. The 0.1.22 test used manual glue and did not verify this automatic transition.
