# Preserve restrictions at every restart and context boundary

Trigger: a no-send invocation resumes after compaction, a second project shares
one customer's active SMS cycle, or an unknown old attempt blocks another client.

0.1.37 offline flow review reproduced lost no-send policy, a one-message context
becoming a two-message registration, ordinary returning inquiries requiring
another initiation and an unrelated review hidden behind an unknown barrier.
0.1.38 regressions cover these paths; live host acceptance remains separate.

Use invocation.prepare/resume with actual effective policy and exact restriction
strings, never only the command default. A legacy pin without restriction
metadata is closeout-only. Keep all original start/attempt identities.

Use material.plan/verify and preserve notification_limits for every inquiry.
sms.prepare/verify takes original material_handoff evidence; dispatch admission
and release check fresh original cycle counts and the frozen inquiry limits.
Do not replace an old shared cycle cap with a child's cap or reset counts/expiry.
Ordinary verified inquiries inherit current standing authority; only explicit
exceptions/manual policy need additional recorded scope.

Queue items retain original scope. Unknown related attempts remain blocked until
new evidence or a bounded recovery timer; a new tick is not a trigger. Persist
consumed wake-up markers with the result and keep the original AttemptId.
Unrelated proven customers may proceed; missing legacy scope stays conservative.
An unavailable SMS reply reader is uncovered input, not a notification-send gate.

See handover-integrity, material-handoff and queue-execution for input contracts.
No offline guard certifies host ownership, live timing or external delivery.
