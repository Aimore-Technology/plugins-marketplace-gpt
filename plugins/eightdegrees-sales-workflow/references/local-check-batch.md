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
