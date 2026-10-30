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
if metadata is unavailable, read the body. Manual inputs stay excluded.

Fresh approval, recipient/stop/latest-reply and attempt checks immediately before
external actions remain mandatory. Measure calls/time and disclose coverage;
do not trade safety or reuse evidence across invocations for a faster result.
