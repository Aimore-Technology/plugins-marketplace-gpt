# Connector contracts

Scope: observed connector execution, last confirmed 2026-10-29. Current schemas take precedence. Evidence: B113 orchestration-parameter-errors, sms-connector-validation, crm-transient-read; earlier source-enum refusals.

## Copy the actual contract before constructing a call

- Notion insert_content uses content, not new_str. update_content uses actual old_str/new_str pairs. These operations are not interchangeable.
- The observed Dropbox metadata tool uses path_or_file_id, not path. Discover the current signature rather than repair a guessed call after rejection.
- LeadConnector operation IDs come from operation discovery. Describe the exact returned operation ID before execution; do not invent a similarly named read operation.
- Select/status values come from the target's actual data-source-state. Run schema-values on each proposed row. A missing-data task does not justify inventing a new source Status. A rejected request is not proof that its other properties saved.

Verify: keep the effective schema snapshot/request and check actual returned envelopes. Reconcile original IDs after a rejection/unknown result; never assume partial success or create a duplicate source.

## AndroidSync request constraints observed in this connection

The live connector rejected a body longer than 70 characters and an idempotencyKey outside the pattern `^[A-Za-z0-9_-]{8,100}$`, even though these constraints were absent from its discovered signature. Treat these as conservative preflight limits for this connector until current effective limits are verified, not universal SMS/GSM segment rules.

Fit the draft BEFORE approval; validate the stable provider key BEFORE dispatch. A stable digest of the original AttemptId can produce a valid key, with its mapping persisted once. Do not silently trim approved text, change approved recipients or generate a fresh key on an unknown attempt. A clearly documented pre-dispatch schema refusal with no request/provider ID may be corrected; changed message text requires a fresh reviewed version. Acceptance, AwaitingPhone, SentToNetwork and delivery are separate evidence states. No inbound tool means two-way acceptance remains untested.

## Read failure versus write uncertainty

A transient contact read failed once, then a later bounded read succeeded without a business retry. Retain both observations. Follow connector-io's bounded read policy; this is not permission to retry unknown writes or sends. Capability-specific failures, such as a location without Workflow API support, do not imply that contact/Notes access failed or that the account contains no automation.
