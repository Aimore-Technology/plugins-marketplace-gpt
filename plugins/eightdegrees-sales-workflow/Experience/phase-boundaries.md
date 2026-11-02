# Future results cannot complete a present review

Trigger: a content confirmation is accepted, but final review completion asks
for Sent/result projections; sending then waits for that completed review.

Observed in the 0.1.30 seven-cycle simulation: one plan listed both the review
and its future send as executable tasks. Owner-write collected send obligations
from every route, blocking review completion and consequently email/SMS work.
No actual customer email or SMS was sent in that batch. Approval was not missing.

Action: use [phase ordering](../references/phase-ordering.md). Freeze only the
current ResumeStep as executable task roles. Finish/read back the review before
the independent send phase, then register the SMS handoff after verified Sent.
Keep original decisions and failed plans; repair old scope with a new linked
prospective phase run, never by deleting obligations or fabricating Sent.

Verification: execution-v2 rejects mixed phases before dependent work, binds
actual route steps, generates minimum evidence and checks canonical/action copy.
Offline regressions reproduce the deadlock topology, complete a review with an
unsent exact draft, retain strict send/receipt/handoff checks and complete the
separate notification phase at SentToNetwork. They do not prove a live resend,
native recurrence or recovery of customer records.
