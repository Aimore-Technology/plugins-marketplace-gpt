# 0.2.0 - Activepieces request client

The installed plugin now adapts four requests to the connected project's published Activepieces flows: init, add-communication, reply-draft and report. The identity and audience remain unchanged. Native Activepieces scheduling owns run-auto; start/stop/run-auto are no longer public client commands.

## Review path

Start with plugins/eightdegrees-sales-workflow/skills/eightdegrees-sales-workflow/SKILL.md, references/activepieces-client.md and scripts/activepieces_client.py. The active payload has five small skills. The original 0.1.58 execution package is archived under legacy and excluded from installation ZIPs. Existing deterministic helper tests point to that archive; new tests verify the active client.

## Boundary changes

The client collects and validates input, resolves enabled callable external IDs from host captures, submits one MCP action and interprets the matching run. It reads no credentials, calls no customer connectors directly and stores no queue/approval state. Transport request IDs correlate asynchronous results; they are not idempotency keys or approval. Failed/unknown dispatch is never automatically retried. Customer source text cannot select a command, bind a flow or set Consent.

Activepieces callable entry adapters now unwrap the native data envelope. Init strips client request metadata before saving business configuration. Terminal Return Response steps store structured initialization/review/report results for exact-run observation. The MCP action runner requires waitForResponse=false; the client inspects a bounded number of new runs and validates both flow ID and request ID before showing the owner's result. Wrapper acknowledgements and older successful runs are not business completion evidence.

## Validation

The full unittest suite passes: 769 tests, including 16 active-client contract tests. Packaging checks validate the four routes, five skills, contained resources and absence of runtime credentials/legacy executors. Live report submission is tested through the actual MCP action runner and observed through its correlated production child run. Additional repeat-report, local installation and backend adapter checks are recorded in the task's deployment artifacts. No real customer email/SMS or CRM write is part of this release test.

The deployment is still awaiting actual workspace initialization. Report can show missing setup; communication/reply requests are rejected by the client before dispatch until init completes. A positive real-customer Notes/draft review and approved provider action remain untested. This release does not implement the backend's outstanding SMS/persona, concurrency or historical migration features.

## Delivery

Source remains on the local codex/activepieces-plugin-client branch. Local marketplace installation is separate from shared release publication; no remote push or account/public upload is performed. Restoring the prior Git marketplace source requires the original Aimore-Technology/plugins-marketplace-gpt URL. The old package remains in repository history/archive and is not silently re-enabled as a fallback.
