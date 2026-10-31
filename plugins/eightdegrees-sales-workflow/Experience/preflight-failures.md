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

Evidence: controlled 0.1.19, Q19-01/Q19-02. Initial page-link checking happened
after publication; a later send-result property call omitted its exact schema
check. Use [notion-mutation](../references/notion-mutation.md) BEFORE every page
call, including initial and nonfinal writes. It combines the two checks and
returns exact args only on success. Reuse captured schemas, not old approvals
of different argument objects. Failed metadata publication never repeats a send.
