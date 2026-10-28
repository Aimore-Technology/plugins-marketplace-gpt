# Connector requests, results and retry boundaries

Use the tool schemas available in the current host. Similar tool names or an earlier test script do not establish the current argument contract. Inspect the relevant schema before first use and after a schema error; do not trial multiple write signatures. For Notion-specific updates, read [Notion I/O](notion-io.md).

## Interpret results before recovery

Inspect MCP `isError` and documented error envelopes at each wrapper level. Use a non-null structuredContent when available, otherwise inspect text blocks. Parse text as JSON only if it is valid JSON; preserve ordinary success text such as `Action completed.` as text. A null structuredContent is not a reason to discard useful text. JSON parse failure is a local interpretation problem, not evidence that a send failed.

Classify separately: explicit rejection with no known effect, known provider acceptance, unknown provider result, result interpretation failure and later log/presentation failure. A successful send tool without a message ID is acceptance evidence, not delivery or a fabricated ID. Persist that evidence and reconcile Sent Items/recipient receipt before considering any retry. A missing search hit does not prove the send never occurred. Prefer returned stable message IDs; otherwise use an exact quoted subject, sender/recipient and time range, recording each query's coverage limitations. Do not resend because a compound or non-ASCII subject search omitted an item.

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
