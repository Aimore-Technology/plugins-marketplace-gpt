# Short scan

Read RunSettings/scan switch once. A real stop exits without other reads/writes.
Discover scoped mail IDs, current active action submissions, controls, due work
and saved recovery. Complete discovery plus no runnable demand means immediate
idle. No inference, CRM/Dropbox/preview checks or routine dashboard writes.

Use metadata/delta feeds when available. Reuse current v4 task-list
Consent/ReviewText fields; scan.watches selects only changed/demanded task pages.
Legacy forms require current original input; unchanged human waits enqueue nothing. Retain cursors and incomplete
pagination honestly. Saved pending/due work is demand even when nothing changed.
Native ticks load current rules from the installed package; no scheduler API,
unique executor or bound conversation is required. Queue/event helpers run in
code, never by manually reasoning through every old row.

For actual inquiries use [email-flow](email-flow.md): one message read, one CRM
match, warm project-cache lookup and one combined review. Coalesce own writes
at its boundary. Do not load every helper/reference or print Python/raw captures.

Batch independent reads and local capture/check work under
[phase I/O](local-check-batch.md). Never emit one save/version-observation shell
call per returned page. Keep originals once, reuse own API write projections,
and persist only changed recovery state or actual effect boundaries.
