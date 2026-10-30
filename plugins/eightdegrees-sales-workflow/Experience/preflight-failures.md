# Stop at the failed check

Evidence: controlled 0.1.18 run, F01. Fact checking rejected Undecided; the driver
created the next run before correcting it. The later valid null value did not
repair that execution-order failure. Live acceptance of the replacement is pending.

Before dependent writes, use [execution preflight](../references/execution-preflight.md).
Require exit 0 AND the documented success status. A refused prepare has no usable
plan; retain it, correct the input and rerun before proceeding. Unknown finance
stays null; canonical labels are returned only for already-valid semantics.

Verify actual call order using a deliberate invalid-value fixture. Local helper
tests do not prove the host/model cannot bypass the helper. Failure logging may
continue; task/draft/customer progress may not.
