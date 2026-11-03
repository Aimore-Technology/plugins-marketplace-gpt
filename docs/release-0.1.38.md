# EightDegrees Sales Workflow 0.1.38

The 0.1.37 flow review found narrower invocation permissions lost on restart,
inquiry SMS limits lost on active-cycle reuse, returning inquiries blocked by
legacy manual initiation, installation-wide unknown barriers and conflicting
SMS capability requirements.

- Invocation pins retain command default, actual effective policy and explicit
  restriction strings. Restart rejects changed restrictions; an unverifiable
  legacy run-auto pin is no-send/closeout-only.
- Material handoff preserves per-inquiry recipient, delay, expiry and message
  limit on active reuse, separately from immutable customer-cycle caps/counts.
  Material notification freeze requires original saved handoff evidence.
  Queue admission and final release check both sets of limits against the same
  original current cycle; a used/expired/unknown notification emits no send call.
- Ordinary source-bound inquiries inherit the saved enabled standing policy.
  The new default no longer requires manual new-cycle initiation. Explicit
  operator manual policy, revocation, scoped/global stop and old attempts stay
  effective. Actual new inquiries need no separate init or per-message consent.
- Queue items/checkpoints retain original customer/channel/context scope.
  Related unknowns/stops remain barriers, while proven unrelated work proceeds.
  Unknown reconciliation needs a new original evidence revision or bounded timer,
  records consumed wake-ups with results and cannot replace the original attempt.
  Missing legacy scope remains conservative.
- SMS instructions consistently require authorized sending configuration,
  device/sender and recipient. Missing inbound-reading capability is separately
  disclosed, without delivery, physical sender-display or stability trials.

Both editions pass 552 offline tests, including 27 new flow regressions.
Marketplace validation and archive content checks are recorded in the development
release evidence. No customer send, CRM/Notion repair, actual native schedule or
cloud-host test was executed for this release. Fresh host acceptance remains.

Public commands and installation identities are unchanged. Existing scan cadence
30/optional20 minutes, bounded budget, separate email approvals, original
Gmail/AndroidSync acknowledgement completion and CRM readback remain.
Original completed records are historical: do not rewrite old proof or rerun an
effect. Eligible unsent legacy material notifications require a prospective
same-source limits freeze; no invented historical permission or extra review.
