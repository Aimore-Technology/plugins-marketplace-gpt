# Notion reads, writes and limited coverage

Use for Notion-dependent decisions, updates and reports. Tool errors and stale query results must not become business actions.

## Read what the action depends on

Use registered original page/database/view IDs. Read settings once per invocation, collect one candidate-task snapshot and reuse it; do not rescan every database before each helper. A query/search/view locates candidates, not final approval evidence. Immediately before applying input, appending CRM Notes or sending, fetch the original task and the actual current content/version and check Mode, State, operator/approval identity, DecisionVersion, cancellation/stop state and prior attempts. A stale query showing an empty decision after a successful page update is not proof of rejection or a reason to create a new task. If original evidence is unavailable or conflicting, pause the affected action.

For new/migrated action-page tasks, also fetch the registered original action page and validate its bound submission/current input under [operator actions](operator-actions.md). PendingTasks properties are workflow projections; a new decision must have original action/chat evidence. Candidate discovery still uses one PendingTasks source, not a second response tracker.

Discover saved views from the registered database and use their paginated view mode for ordinary lists when supported. Preserve category/completion filters and process every page before claiming complete coverage. Prefer exact known page IDs for subsequent reads. Use SQL sparingly for schema-backed exact identity/aggregation that is actually needed, not repeated status polling. See [source identity](source-identity.md) for exact comparisons; formatted view text still is not a canonical identifier.

On `usage_limit_reached` or another entitlement error, stop repeating that restricted operation for the invocation. Disclose the actual limit even when fallback succeeds. Use an available saved-view/typed-row interface and registered original-page fetches for remaining permitted work; neither assumes a new permission nor bypasses a denial. If an alternative is also denied, stop that operation. A Notion access/security denial is not a quota error to route around.

Record source, cutoff, pagination completeness and unavailable sources. Known-page reads can support that page's version check, but cannot establish a global pending count, absence of duplicates, a new daily brief's uniqueness or overall health. Without complete candidate coverage, keep new identity-dependent creation and aggregate claims paused or explicitly incomplete; do not infer absence from a failed/partial query. Reuse a registered daily brief ID; do not create another because SQL was unavailable. For a genuinely new operator/date with complete discovery proving no matching brief exists, create once and register its page ID for later calls. If discovery is incomplete, keep first creation pending rather than claim uniqueness.

Before row writes, validate enum/property values against the fetched data-source-state with schema-values under [publication validation](publication-validation.md). Missing-data reasons belong in their pending tasks, not invented source status options.

## Check actual tool success

Apply the current-schema and targeted-patch checks in [Notion publication](notion-publishing.md). Do not guess docs URIs or DDL type names: discover the current contract (logical text is currently RICH_TEXT for Notion DDL). Short error properties contain plain text; full error JSON belongs in the body. Dropbox metadata arguments must also match the discovered schema. Reuse snapshots within an invocation and batch independent permitted reads/updates without weakening final decision checks.

Before any dependent step, inspect `isError` and documented structured error envelopes, including nested MCP result wrappers and JSON error content. An object returned by a tool is not itself success. Follow [connector I/O](connector-io.md) for non-JSON success text, actual request schemas and bounded service retries. Do not classify ordinary customer text containing the word "error" as a tool failure. Preserve the operation's actual error code and whether a side effect is known.

After a rejected input/property write, fetch the same original page before correcting the request. Do not assume another field such as InputSubmitted was set by that request, and never process the intended value as if it had been saved. Correct only the rejected representation using the documented tool contract. An unknown write requires reconciliation before retry; known external success with only a failed Notion log needs log repair, not another CRM write or send. Use separate targeted updates when needed and verify relevant saved state before a dependent action.

For targeted content updates, match a unique workflow-owned plain-text heading/sentence from the latest fetch. Do not use a whole rendered paragraph containing native mentions as old_str: Notion may serialize it differently. If no stable unique match exists, keep presentation repair pending and use a supported block update; never replace the whole page, drop history/children or reexecute the external action to fix a summary.

Use an exact unique plain heading plus a short adjacent workflow-owned line from the latest fetched representation; include enough context to distinguish current from history. Do not reuse an invented CURRENT_BRIEF marker, a broad repeated heading prefix or pre-serialization text with different escaping. On zero/multiple matches, stop and reread once; do not brute-force variants or turn a presentation refusal into a business retry. Save its unresolved quality status if no supported exact update can be established.

## Human input and archival links

Keep editable structured answers on the registered ordinary action page for new/migrated tasks, and preserve legacy task-body routes until upgraded. Accepted machine snapshots remain separate in canonical task history as fenced JSON. OperatorInput is only a short plain-text compatibility summary, not the main editor or serialized configuration object. Preserve legacy answers. Show literal file paths/names in code style, not fake HTTP links; real links require verified provider URLs. Code formatting is a display concern; canonical identity properties remain plain values.

Verify saved file-name/link presentation in the actual Notion output per [monitoring](monitoring.md). Keep the original source identity snapshot before moving a page out of Inbox; database properties may stop appearing after a move. Register its page/Business Run reference before moving, then fetch the original page and destination index. Recover through that canonical reference, never by copying the source or interpreting an empty Inbox as absence.

Before a verified customer's communication reaches ContentReview, move the original page to Communications when supported or link that same page in the customer's Communications index. Verify its page ID, source and client mapping and save its canonical reference. A staged Inbox page with no customer archival link is not a completed archival step. If link saving fails, keep the source/progress and suspend the dependent review setup; do not copy another source page or postpone the link until a final report.

## Property proposals and read reuse

Run schema-values on only the actual proposed property map, not a fetched row's
system url/createdTime or whole wrapper. The helper checks enums, not every host
argument constraint. The observed ExternalIds property rejected a JSON-shaped
string; use a short ordinary text ID index there and preserve the complete JSON
in owned page history or an evidence attachment. This is connector-specific,
not a claim that Notion cannot store JSON text. After refusal, read the original
before projection-only recovery; a metadata failure never replays a known send.

Reuse one paginated candidate snapshot per invocation. If a canonical database
query is supported, filter Automatic/open tasks once, then classify locally;
otherwise exhaust the supported category views. Do not scan all five views and
then repeat a full database listing for the same decision. Fetch only owned
candidates that need a current per-item check. Re-read the original task/action
immediately before acceptance/provider action and after writes as required.
Static form-result prose should say 'awaiting workflow validation; last checked
at ...', rather than asserting 'not submitted' after an unobserved native edit.

## Candidate conflicts and low-cost normal reads

Use the actual registered saved views for ordinary recurring candidate reads;
do not begin every cycle with full SQL scans. If SQL/rows quota is exhausted,
try only supported unblocked view/original-page reads and record their coverage.
If complete discovery is unavailable, pause absence-dependent creations and
aggregate claims. Exact known-task execution still needs its original approval
and state; conflicting snapshots follow [outcome state](outcome-state.md).
Reuse one unchanged capture for local checks and coalesce final owner projections;
record only affected task/action/hub sections rather than rewriting history.


## Recurring-cycle read budget

Read setup/checkpoints once, collect one paginated candidate snapshot, and run
local checks on the same capture. Use registered saved views normally. After an
actual SQL/rows usage-limit refusal, preserve its capability-specific degradation
and select supported complete view/original-page reads on subsequent cycles;
do not reprobe the blocked route without provider reset timing or an explicit
capability check. Preserve coverage/pagination evidence. No complete discovery
means no absence-dependent creation or aggregate completeness claim.

Filter out Manual inputs before fetching action bodies. Automatic waiting tasks
still need their active action input checked: editing that ordinary page may not
change the canonical PendingTasks row. Use genuinely supported action edit
metadata if available; otherwise fetch eligible action bodies. A changed input,
version, stop or provider result invalidates dependent captures. Re-read exact
approval/stop/attempt evidence before external action, and affected saved results
after writes. No cross-invocation evidence cache or skipped fresh send checks.

When no business input/source/step changed, do not regenerate copy/HTML/PNG or
rewrite unchanged task/action prose. The scan still records its actual cutoff,
coverage/checkpoint and capability observation; complete only its own run.
Combine compatible final projections, preserving input/history and existing
report-only boundaries. Record actual tool-call counts and elapsed time;
latency targets are measurement goals, not scheduling guarantees.

## Local batching and the Today entry

Use [local-check-batch](local-check-batch.md) to read one original capture bundle and run multiple local checks. Reuse snapshots in the same unchanged phase; required fresh pre-action and post-write reads remain. With verified Today linked views, a canonical task/binding update needs no duplicate Actions queue rewrite or full history read. Preserve legacy fallback until explicit setup succeeds. Measure actual calls/elapsed time; local batching alone is not a measured latency improvement.
