# Bounded discovery and short owner handovers

This procedure addresses the seven-cycle 0.1.34 rehearsal. It adds no service,
command, notification permission or cross-invocation approval cache. Live speed
and token savings still need measurement.

## Discovery: one snapshot, not a historical audit

1. Capture RunSettings and EventIndex once. Read the current complete registered
   PendingTasks view once, preserving pagination and error envelopes. Use local
   `scan.watches` with `settings_page`, `index_page`, `tasks` (original rows) and
   `tasks_complete`. Keep input/output in the same capture bundle.
2. The generated action list includes active human forms, never completed forms
   or machine-notification result pages. Fetch those forms once and digest their
   actual input. Keep scoped mail/reply discovery, control, timers and recoveries;
   source-watch pruning NEVER removes mail labels or reply observations.
3. Source metadata watches use current dependencies/indexes for active email
   consumers. Superseded files and completed projects are retained as history,
   without recurring reads. A queue containing only a factual receipt SMS needs
   no Dropbox facts. Unknown consumer bindings, missing index or pending source
   events use conservative source watches; incomplete task discovery cannot
   establish absence. Never drop a pending event to shorten a cycle.
4. Batch independent permitted reads in the host's orchestration tool. Persist
   each returned object directly once. Print only capture name/status/digest;
   do not retype JSON, HTML/base64 or repeated shell chunks through model turns.
   Apply `connector.capture` before interpreting a failed response. For a thrown
   exception explicitly capture `name`, `message`, optional `stack` and `cause`:
   JavaScript `JSON.stringify(new Error(...))` alone loses its message.
5. Run `scan.probe` before loading any owner procedure. A complete unchanged
   ScanIdle ends here: no run/Health/Today write, CRM/source-content read or full
   result audit. Preserve changed fingerprints when needed. An omitted/incomplete
   feed is never idle. Do not stamp skipped dependency reads as new Health probes.

Where a host exposes JavaScript orchestration and structured file saving, use
this capture pattern with its actual authorized tools and file API:

```javascript
let raw;
try { raw = await readOriginal(); }
catch (e) {
  raw = {exception: {name: String(e?.name ?? "Error"),
    message: String(e?.message ?? e), stack: e?.stack ? String(e.stack) : null,
    cause: e?.cause ? String(e.cause) : null}};
}
await saveOriginalOnce(captureName, raw);
// Return a path/status, not the captured body. Run connector.capture locally.
```

`readOriginal` and `saveOriginalOnce` stand for existing host capabilities,
not new MCP tools. Without orchestration, use native file/capture facilities
and the same one-response/one-file rule. Never pass unescaped payloads to shell
commands. Failed normalization stops its dependent step and retains the raw file.

## Owner handover: finish the real result, then select the next event

- Freeze one affected-phase plan; use generated `execution_plan.run_properties`
  for the owning run. `execution.ready` checks the actual saved metadata as well
  as the frozen plan. New WorkflowRuns need their installed SkillVersion,
  current RunId and SourceKey. Scan/report keys use `scan:<current invocation>` /
  `report:<current invocation>`, never the previous checkpoint's identity.
  Other owner runs use their generated invocation key; original customer/mail
  SourceKey remains on linked task/source records. Do not replace frozen run
  metadata with formatted email links from query projections.
- Reuse unchanged original captures and schemas for local checks. Batch exact
  mutation checks with `--output` rather than serializing the same originals
  into many helper invocations. Mutations stay ordered; a changed input/result
  invalidates only its affected captures. Fresh approval, stop/window/count,
  task-state/attempt checks and actual saved readback are never skipped.
- After successful Gmail/AndroidSync acceptance, retain the original proof and
  promptly update the original task's current Result to “submitted to service;
  internal recording in progress”, with its actual message ID. Do not leave a
  current “provider not called” summary. Overall State stays InProgress until
  required CRM/material/result checks finish. No provider status queries.
- Finish and read back the current owner result, index acknowledgement and its
  successor wake-up. Select the next event immediately. Do not perform an
  installation-wide audit, repeat discovery or publish a separate monitoring
  summary between owners. Coalesce noncritical Health/counters/logs at the scan
  boundary; no recursive monitoring of monitoring. Required evidence/attempts,
  next-wake registration, accepted inputs and source checkpoints stay durable
  before any dependent action or consumption.
- New replies/stops and unknown reconciliation precede notifications. Due
  factual notifications precede ordinary reviews and optional display repairs.
  Select another fitting independent item if a nonblocking phase is too large;
  do not skip a pending stop or unknown-result barrier for conflicting work.
  Original verified customer/channel/context scopes allow independent work;
  legacy missing scope remains conservative. Unknown recovery needs a new
  evidence revision or bounded timer, never just another scan tick.
- 900s total and the nominal 120s publication reserve remain. Each admission
  rechecks the actual clock, and admission still stops at minute 13. Estimates
  may use up to 15s of the nominal reserve (at least 30s retained), only when
  at least 30s of business time remains. Thus remaining179/estimate180 may
  proceed, whereas a substantial shortage still defers. Save the exact estimate
  slack/reserve-use result. This is selection, never permission to send or
  extend a customer expiry, ignore overlap, retry an unknown or reset counts.

The final dispatch gate has a separate estimate for the remaining provider call
(at most30s). It does not charge already completed preparation time again.
Both dispatch.admit and dispatch.prepare still recompute current selection,
check the exact saved admission and120s expiry, and retain current stop, due,
task state, no-send policy, unknown attempt and actual deadline checks. The owner
phase must already have obtained its ordinary scan.cycle admission. A30s call
estimate is not an exception to the customer window or a promise of API speed.

When reporting timing, retain original phase/checkpoint/turn boundaries and
historical overruns separately. Do not rewrite the four old overrun records or
old missing-version/SourceKey evidence to make the release pass.

Current native execution and backlog/metrics rules: [scheduled entry](scheduled-entry.md). Always restore pending source-to-owner handoffs from original captures; unchanged inputs do not remove executable backlog. Native configuration acceptance and guard pass never imply business progress. Legacy unknown scope blocks its original source/effect, not every unrelated customer/channel.

Use scan.watches.ready_task_records/ready_task_blocks as scan.probe supplementation before claiming idle. After saved discovery, scan.queue constructs the full work set from the original EventIndex and current task/source captures; pass its full result as queue_plan to every scan.cycle. The planner adds omitted fitting work without another scheduler/identity requirement. Keep all remaining pointers across owners and restarts. A subset containing only current draft preparation cannot represent all pending mail/due work. No send or factual approval is synthesized by queue construction.
