# Connector requests, results and retry boundaries

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

Use the tool schemas available in the current host. Similar tool names or an earlier test script do not establish the current argument contract. Inspect the relevant schema before first use and after a schema error; do not trial multiple write signatures. For Notion-specific updates, read [Notion I/O](notion-io.md).

## Interpret results before recovery

Inspect MCP `isError` and documented error envelopes at every wrapper level. Read BOTH structuredContent and text JSON when present: a non-null generic structured error must not discard a more specific upstream status/code in text. Parse text as JSON only if valid; preserve ordinary success text such as `Action completed.`. Keep wrapper and upstream diagnostics separately using [offline evidence checks](evidence-checks.md) when available. A null structuredContent is not a reason to discard text. Local parsing failure is not evidence that a send failed.

For GHL WORKFLOW_API_NOT_ENABLED_FOR_LOCATION, record the original 403 and that this location lacks the Workflow API, even if the connector wraps it as INVALID_ARGUMENT. Do not retry parameter/token/scope changes to resolve that capability absence. Keep verified contact/Notes capability separate. A failed workflow listing is not proof that no outbound automations exist; test fixture creation stays unverified/disabled until safe independently. Preserve more specific nested Gmail quota diagnostics rather than collapsing every 403 into a permission problem.

Classify explicit rejection, successful original service acceptance, ambiguous
handoff, parsing failure and internal publication failure separately. Known
Gmail/AndroidSync acceptance completes dispatch. Retain original response and
attempt IDs, and repair only our missing records. Do not search Sent Items or
recipient mailboxes or poll external status. Missing metadata is not permission
to resend. CRM write/readback is the explicit exception under provider-boundary.

These are known contract differences to check against the live schema:

- Notion `insert_content` uses `content`; `replace_content` uses `new_str`; `update_content` uses `content_updates` with minimal unique `old_str`/`new_str` pairs. An old schema may differ; do not copy fields between commands.
- Notion search uses `page_size`, not `limit`; use a supported small page such as 20, never assume a 100-item limit. Read actual pagination/cap notices before claiming completeness.
- Dropbox search needs a non-empty query on first search. Browse an empty/new folder with the supported folder-list tool instead. Search pagination sends the returned cursor alone; no query/filters. Use authorized folder paths, not web URLs/file IDs in its path argument.
- Outlook send results may be text-only with no message ID. Its current plain-text-only sender is not an HTML/EDM transport. Preserve the separately verified Gmail HTML send requirement.

## Bounded rate-limit recovery

Recognize explicit retryable service quota errors such as Gmail 403 RATE_LIMIT_EXCEEDED separately from authorization/security denials. Save the affected run, actual error/retry timing, observed coverage and original source/step. Never relabel a permission denial as a transient quota problem.

For idempotent authorized reads, allow at most one retry per service per invocation after the provider's retry time, only when that wait is short enough for the host (at most 60 seconds). If timing is absent, longer, or quota recurs, record NextEligibleAt when known and exit the affected service phase. Do not immediately repeat full/raw/search calls into the same service quota. The next separately authorized scan uses normal source deduplication and resumes unfinished reads; do not create a schedule or loop to recover.

Continue independent work on already verified sources only when it does not need unavailable current evidence. Incomplete mailbox discovery/latest-reply coverage blocks affected customer sends and global completeness claims. Known original tasks may still be read or validated if their own required evidence is available; Manual tasks remain Manual. Preserve failed scan history after a later full rescan succeeds. Checkpoints represent saved progress/pending outcomes, never evidence that all mail was read successfully. Unknown writes/sends follow reconciliation, not read-retry rules.

Update per-service [monitoring](monitoring.md) from the actual attempt and result. Recovery does not repair the connector's native charset behavior or erase failure observations.

## Known IDs, cached discovery and limited read retries

Reuse actual connector schemas and operation IDs within an invocation unless a
schema/capability error invalidates them. A recorded Dropbox file ID plus revision
and current version index is the first lookup path; don't rediscover a known
source by folder search on each step. An empty folder-search result does not
prove the registered file is missing. Read the actual registered metadata/content
within scope, retain the search observation, and check current index revisions.

An explicit Internal error on an idempotent read may receive one bounded read
retry, keeping the failed response. Apply the existing rate/access rules for
quota and permission failures. This is not an unknown-write retry permission.
Desktop bridge failure belongs to runtime connectivity, not a customer workflow
assertion. Check available tools again after a host update; a deprecated dynamic
tool may require the codex_app MCP server. Do not replace an unavailable bridge
with session-file edits, hidden endpoints or CLI resume. Save the current task,
actual input/approval and undelivered command for the operator to resume.

For recurring Notion reads, preserve the capability-specific quota observation
and use [Notion I/O](notion-io.md) saved-view discovery; the ordinary bounded
transient retry rule is not a reason to reprobe a known exhausted SQL/rows quota
every invocation. A successful view read does not clear the SQL degradation.
