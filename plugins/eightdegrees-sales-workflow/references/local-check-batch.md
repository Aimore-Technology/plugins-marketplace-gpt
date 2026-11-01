# One capture bundle, several local checks

Keep each original tool response once in a local capture bundle outside the plugin
source. Do not repeatedly paste the whole workspace or serialize that same fetch
inside every helper input. The bundle preserves original error, warning,
reference and completeness layers, including both original MCP payload forms.
Do not reduce it to a reconstructed Markdown string or delete a refusal.

Run `python3 <plugin>/scripts/local_checks.py --captures <captures.json> --input <plan.json>`.
The small plan contains checks with unique name, operation and input. Supported
operations are listed in that script: existing Notion publication/schema/gate,
execution-plan, fact, outcome and operator-presentation checks. It has no dynamic
imports, shell commands, providers or connector calls.

Use {"$capture":"original-page"} for an exact original bundle entry, and
{"$result":"earlier-check"} for an earlier successful local result. References
are resolved locally; hashes identify the captures actually used. Helpers receive
isolated inputs, and failures stop later checks. The output contains check
results/actual exits, not captured bodies. Require exit 0 AND LocalChecksPassed.
Retain each item's actual exit/result in the frozen completion contract with
the correct invocation/publication version; batch success is not completion or
an approval and cannot replace the original named check kind.

Reuse only unchanged captures within the same owner phase. A write, edited input,
new version, new stop/reply or result invalidates affected captures. Always do
the existing fresh task/action/approval/stop/attempt checks before external work,
and actual saved readback after writes. There is no cross-invocation cache.

Only affected records belong in the plan. Native Today views need no manual queue
copy after task state/binding updates. Preserve complete paginated candidate
coverage and capability degradation. This reduces local process/serialization
work; elapsed-time and provider-call improvements still require live measurement.

## Compact mutation and completion checks

Use `--output <checked.json>` for large batches. The file retains exact results
and calls; stdout contains statuses, actual exits, digests and its path rather
than bodies or executable arguments. Load the exact checked call locally for
MCP execution without printing/retyping the full body. Require whole-batch exit
0 and LocalChecksPassed. A refused batch removes executable calls, including
ones prepared before a later failure.

The bundle also supports notion.mutation, notion.owner-write, notion.report-write,
operator.response and email presentation operations. Store a proposed exact call
once as a capture; use call={"$capture":"proposed-call"}, target/schema references
and small scalars. Check owner/report scope before exact mutation. Preserve all
MCP error/completeness layers. Reuse checks only for the unchanged call/evidence.

Freeze one owner-phase plan and retain result IDs/artifact digests. Do not repeat
the full plan on every progress/log write or copy base64 HTML/image data into
RunSettings indexes. New lightweight indexes contain IDs, versions, outcome IDs
and pointers; packages stay on originals. Preserve legacy evidence, migrating
only through explicit upgrade and verified original archive. Coalesce noncritical
Health/counter/log writes at owner boundaries; never recursively monitor logging.

Unattended operations add scan.cycle, sms.presentation-plan/verify, contact.restriction-plan/verify and contact.dispatch-gate. Plans select work or propose patches; only verified saved readback can supply completion evidence. ScanDeferred and ContactDispatchChecked do not authorize an external effect. See [unattended operation](unattended-operation.md).

When the host exposes programmatic tool orchestration, persist each original response once directly from that returned object, and print only path/status/digest. Do not retype the response through many model-generated shell chunks or repeatedly include it in helper arguments. Use the available native file/capture facility with correct argument quoting, outside the plugin repository; do not add another service or send customer captures elsewhere. Compact output does not remove original error/completeness evidence.
