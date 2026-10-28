# Exact source identity in Notion

Use when persisting, finding or deduplicating a source/task. Notion can render text properties as mailto links or escape punctuation in fetch/view Markdown. Display strings are not canonical identifiers.

- Construct Gmail SourceKey from verified account + direction + immutable Gmail message ID. Store a plain text property, without Markdown links, code formatting or added escapes. Retain the separate source URL. Do not change account casing/aliases or a source ID based on a display name.
- Fetch the data source schema first. Prefer parameterized SQL or a typed exact property filter against the actual SourceKey. With the schema below as an example only, bind the key as a parameter instead of interpolating it:

```sql
SELECT url, "RunId", "SourceKey", "Status"
FROM "collection://<registered-workflow-runs-source-id>"
WHERE "SourceKey" = ? AND "RecordType" = 'Business'
```

- Resolve the real registered collection and schema before querying; the example is not an executable customer ID. If SQL is unavailable, use typed exact property filters or raw property values returned by a supported tool. Never compare a constructed key directly with rendered view/page Markdown, and never globally remove slashes, punctuation or backslashes from identifiers. If only display output is available, pause ambiguous creation for reconciliation rather than assume no match.
- Search the canonical business runs/communication records as well as Inbox when needed. A source page moved from Inbox to Communications may no longer appear as an Inbox row; its disappearance is not evidence that it was never processed. Link the existing original page/run and preserve its source key.
- Task identity adds paused step + issue (and review version where applicable) to the original source. Reuse the recorded TaskId and page ID; do not create another task because its state, view or presentation changed. Exclude scan/initialization records when counting canonical business items.
- On zero exact matches, create only after validating scope and single execution ownership. On one, continue only unfinished eligible steps. Multiple canonical matches go to ExecutionExceptions; do not merge or delete records automatically. Notion lookups are not atomic locks and serial reruns do not prove concurrent exactly-once behavior.

When a tool reports escaped values, verify the stored property through its typed/query interface before trying to repair it. Preserve existing correct values and history; do not rewrite them merely because the display looks different.
