# Notion reads, writes and limited coverage

Use for Notion-dependent decisions, updates and reports. Tool errors and stale query results must not become business actions.

## Read what the action depends on

Use registered original page/database/view IDs. Read settings once per invocation, collect one candidate-task snapshot and reuse it; do not rescan every database before each helper. A query/search/view locates candidates, not final approval evidence. Immediately before applying input, appending CRM Notes or sending, fetch the original task and the actual current content/version and check Mode, State, operator/approval identity, DecisionVersion, cancellation/stop state and prior attempts. A stale query showing an empty decision after a successful page update is not proof of rejection or a reason to create a new task. If original evidence is unavailable or conflicting, pause the affected action.

Discover saved views from the registered database and use their paginated view mode for ordinary lists when supported. Preserve category/completion filters and process every page before claiming complete coverage. Prefer exact known page IDs for subsequent reads. Use SQL sparingly for schema-backed exact identity/aggregation that is actually needed, not repeated status polling. See [source identity](source-identity.md) for exact comparisons; formatted view text still is not a canonical identifier.

On `usage_limit_reached` or another entitlement error, stop repeating that restricted operation for the invocation. Disclose the actual limit even when fallback succeeds. Use an available saved-view/typed-row interface and registered original-page fetches for remaining permitted work; neither assumes a new permission nor bypasses a denial. If an alternative is also denied, stop that operation. A Notion access/security denial is not a quota error to route around.

Record source, cutoff, pagination completeness and unavailable sources. Known-page reads can support that page's version check, but cannot establish a global pending count, absence of duplicates, a new daily brief's uniqueness or overall health. Without complete candidate coverage, keep new identity-dependent creation and aggregate claims paused or explicitly incomplete; do not infer absence from a failed/partial query. Reuse a registered daily brief ID; do not create another because SQL was unavailable. For a genuinely new operator/date with complete discovery proving no matching brief exists, create once and register its page ID for later calls. If discovery is incomplete, keep first creation pending rather than claim uniqueness.

## Check actual tool success

Before any dependent step, inspect `isError` and documented structured error envelopes, including nested MCP result wrappers and JSON error content. An object returned by a tool is not itself success. Follow [connector I/O](connector-io.md) for non-JSON success text, actual request schemas and bounded service retries. Do not classify ordinary customer text containing the word "error" as a tool failure. Preserve the operation's actual error code and whether a side effect is known.

After a rejected input/property write, fetch the same original page before correcting the request. Do not assume another field such as InputSubmitted was set by that request, and never process the intended value as if it had been saved. Correct only the rejected representation using the documented tool contract. An unknown write requires reconciliation before retry; known external success with only a failed Notion log needs log repair, not another CRM write or send. Use separate targeted updates when needed and verify relevant saved state before a dependent action.

For targeted content updates, match a unique workflow-owned plain-text heading/sentence from the latest fetch. Do not use a whole rendered paragraph containing native mentions as old_str: Notion may serialize it differently. If no stable unique match exists, keep presentation repair pending and use a supported block update; never replace the whole page, drop history/children or reexecute the external action to fix a summary.

## Human input and archival links

Keep editable structured answers in native body fields; store accepted machine snapshots separately as fenced JSON. OperatorInput is only a short plain-text compatibility summary, not a serialized configuration object. Do not copy a JSON object into that property as the main input. Preserve any existing legacy answer. Show literal file paths/names in code style so Notion does not create a fake HTTP link; use real hyperlinks only for verified provider URLs. Code formatting is a body/display concern; canonical identity properties remain plain values.

Verify saved file-name/link presentation in the actual Notion output per [monitoring](monitoring.md). Keep the original source identity snapshot before moving a page out of Inbox; database properties may stop appearing after a move. Register its page/Business Run reference before moving, then fetch the original page and destination index. Recover through that canonical reference, never by copying the source or interpreting an empty Inbox as absence.

Before a verified customer's communication reaches ContentReview, move the original page to Communications when supported or link that same page in the customer's Communications index. Verify its page ID, source and client mapping and save its canonical reference. A staged Inbox page with no customer archival link is not a completed archival step. If link saving fails, keep the source/progress and suspend the dependent review setup; do not copy another source page or postpone the link until a final report.
