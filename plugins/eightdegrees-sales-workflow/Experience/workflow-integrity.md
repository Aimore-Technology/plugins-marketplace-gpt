# Workflow integrity

Scope: route and completion evidence, independent of connector success. Evidence: B113 communication-data-route, earlier-owner-completion-contract. Status: open execution/product gaps; this card does not register a new route or enforce a runtime lock.

## Validate before making a form actionable

The tested communication DataCompletion task used ReviewCommunication. The shipped route inventory permits ContentReview/ExecutionExceptions for that step, so the original Waiting task failed resume-task. The test had already consumed inputs before checking it. Successful data saving cannot establish valid routing.

Before task/form registration, validate OwnerSkill, ResumeStep, Category, Mode and current invocation policy against the actual task-routes inventory. Repeat before input consumption and owner dispatch. A genuinely missing route is an open package defect: suspend the affected task and report the missing contract. Do not invent a step, relax its category, relabel the task to fit, fall back to Notes, or mark it Completed merely to obtain Deferred. A terminal-task check cannot retrospectively validate its original Waiting route. Retain the original source/run/approved scope and already verified business results.

Open fix: explicitly define and test communication data-completion ownership and its unfinished resume step. That implementation is separate from adding this library.

## A check must run at its dependency boundary

Some early setup/manual/scan owners checked display text but registered Completed without freezing all required checks or running completion-gate. The later report did use the new gate correctly and blocked an actual bad saved link. That does not retroactively validate earlier owners.

At each owner entry, identify its actual required dependency checks before work. Persist immutable input/attempt results before dependent mutations. Before publication completion, check every current status/result/input surface and required saved page against the same canonical version. Capture integer process exit AND structured result; missing, stale, skipped and malformed evidence blocks completion registration. Pass the full current completion input when the reporting preflight requires it. A correct header cannot excuse a stale Not submitted result or active prompt below it.

Verify the original audit order: frozen contract, actual checks, gate, then completion event. Do not reconstruct a fictional earlier contract after execution. Report existing provider success even if publication remains incomplete, repair only missing projections, and append a correction for a premature Success rather than repeat a business action.
