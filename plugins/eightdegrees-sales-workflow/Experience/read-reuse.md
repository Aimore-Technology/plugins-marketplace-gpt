# Reuse captures within a phase

Evidence: controlled 0.1.18 run. Scan turns took roughly 2–14 minutes; real-thread
draft continuation took about 20 minutes. These are observed turn durations,
not measured speed gains or a 15-minute scheduling guarantee.

Use one candidate snapshot and one current capture per unchanged entity/version
in a verification phase. Run all local checks on that capture. Invalidate after
a relevant write, input/decision/version change, then fetch affected results.
Unchanged content does not need new HTML/PNG or repeated state writes.

Human input is on the action page: an unchanged canonical database row cannot
prove its input is unchanged. Read eligible Automatic action inputs, or first
use genuinely supported action-page edit metadata and fetch changed bodies;
if metadata is unavailable, read the body. Eligible submitted Manual communication inputs follow the shared queue; unrelated Manual work stays excluded.

Fresh approval, recipient/stop/latest-reply and attempt checks immediately before
external actions remain mandatory. Measure calls/time and disclose coverage;
do not trade safety or reuse evidence across invocations for a faster result.

Before repeat local checks, use [one capture bundle](../references/local-check-batch.md) rather than serializing full original responses into many shell calls. Verified Today linked views follow canonical task updates, so no duplicate queue history is needed per transition. This implementation reduces local process/serialization operations; no new live elapsed-time gain is claimed without measurement.

The 0.1.22 live review again found slow multi-owner steps and repeated large capture/plan serialization. Keep one original response per phase, and use local named references instead of embedding the full response into each command or model-visible output. Persist compact progress/results plus artifact paths/digests, not a new complete plan history on every read. Re-fetch only changed surfaces; preserve all mandatory fresh send and saved-result checks. Offline check reuse is not measured live speed or a 15-minute completion guarantee.

Evidence: 0.1.24 completed seven controlled cycles in 8.38-22.00 minutes; four exceeded 15 minutes. Original captures were repeatedly serialized for exact-call, owner/report guards and result checks. Use local_checks with named captures for all these operations and --output for full results/exact calls. Do not print/retype large captures or repeat a full plan per log. A refused batch yields no executable call. A 200 KB exact-call regression retains the call locally with a console summary below 2 KB; this is an offline output-size result, not measured live speed.
