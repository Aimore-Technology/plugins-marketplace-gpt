# EightDegrees Sales Workflow 0.1.35

In the seven-cycle 0.1.34 rehearsal, an idle turn still took210.823s, the new
material-email notification missed admission by one second, and final send
admission charged the whole preparation estimate again. Report metadata omitted
SkillVersion; scan SourceKey reused the previous invocation. One thrown read
failure lost its original diagnostic. This release corrects those paths without
replaying accepted sends or rewriting historical failed checks.

## Changes

- scan.cycle uses at most15s of estimate tolerance within the nominal publication
  reserve, retaining at least30s. Actual work-admission/total deadlines, saved
  budgets, ownership and all send guards remain. New replies/stops and unknown
  reconciliation precede notifications; notifications precede ordinary reviews
  and optional display work. Another fitting independent phase can run when a
  nonblocking head item is too large. Stops/unknown barriers cannot be skipped.
- Final dispatch admission estimates the remaining provider call (at most30s),
  not preparation already completed. Exact current/saved admission,120s expiry,
  stop/version/unknown/count/window/ownership and no-send restrictions remain.
- scan.watches derives active action pages and current project dependencies from
  original settings/index and complete task rows. It retains mail/reply scope
  and pending source events. Unknown bindings use conservative watches; completed
  projects and notification-only work do not trigger historical file sweeps.
- New execution plans generate run metadata from the installed manifest and
  current invocation. Saved-plan ready checks require the actual metadata.
  Exact Notion preflight rejects missing metadata, a stale scan key, a missing
  RecordType and missing/wrong new-run version before emitting arguments.
- connector.capture preserves original returned envelopes and explicitly captured
  thrown Error messages. Failed discovery retains its diagnostic reference/hash
  through later recovery, without inventing HTTP/quota causes or retry timings.
- The packaged short scan procedure makes direct single-capture handling,
  local check batches, immediate provider-result summaries and short owner
  handovers explicit. Required durable business evidence remains mandatory;
  noncritical monitoring/history writes are coalesced at the scan boundary.

## Validation and limits

Both editions pass499 offline tests, including21 new regression methods. The
179/180 and89/90 boundaries now admit; large estimate shortages, actual deadlines,
stop/unknown/overlap/no-send and changed argument cases still refuse. A prepared
SMS can pass a fresh final call check after90s of real preparation without being
charged the full phase again; the same stop still refuses.

Offline replay of the original saved0.1.34 settings/index and complete task
captures selects5 rather than15 metadata reads while the two reviews wait, and
0 while only the machine notification remains. It preserves both human action
pages in the first state and leaves mail scope unchanged. This is an observed
read-plan reduction, not a measured live duration/token improvement.

Marketplace/reference validation and deterministic inspected archives cover both
editions. Shared business files match; platform runtime/manifests retain their
existing differences. No live email/SMS, CRM/Notion writes, schedules or customer
data changes are performed by these regressions. The existing queued live SMS
is not claimed sent; run the public workflow after upgrading to validate live
timing and completion. Claude/Cowork cloud timing remains unverified.
