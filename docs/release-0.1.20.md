# EightDegrees Sales Workflow 0.1.20 candidate

The controlled 0.1.19 run found three quality defects despite successful actual
email, SMS-network and CRM results. Q19-01 checked initial publication links
late; Q19-02 omitted exact property validation before a result projection;
Q19-03 left a completed email page claiming its separate SMS was not sent.

- notion_mutation.py combines visible-link and exact property/schema checks
  BEFORE each supported page call, including initial creates, metadata-only
  progress/results and log batches. It requires original target/schema captures
  and emits executable args only after all checks pass. Changed args require a
  new check; a refused batch exposes no partial args. All eight owners use it.
- Current send-result verification now requires the actual registered action
  fetch, not only normalized JSON. It rejects stale other-channel negatives,
  undated/contradicted receipt claims, wrong IDs and incomplete/duplicate current
  sections. Owner completion binds that display result to the original task.
- Completed pages keep current copy channel-local. Other channels and later
  Communications stay linked to their own records. Send-time receipt unknowns
  are dated historical observations, not permanent current non-receipt claims.
  A legacy display repair preserves approved bytes, history, attempts and stop
  state without repeating CRM, email or SMS operations.
- Shared rules, regressions and Experience entries are shipped in both editions;
  edition-specific manifests, commands and runtime targets remain separate.

The helpers are offline model-execution checks, not host-enforced MCP interceptors.
They neither send nor widen command permissions. Schema captures may be reused
within a phase, while actual changed body/property objects must be checked.
Historical failures remain in the 0.1.19 report; later passes do not erase their
original order. See [directed acceptance](test-0.1.20.md) for live follow-up.

Verification: 249 offline tests per edition, including 15 new rejection/display
regressions; package/reference checks and deterministic archives. A live display
maintenance check is recorded outside the distributed plugin. This release does
not establish SMS recipient delivery, inbound SMS, image/attachment EDM, native
15-minute scheduling, or measured performance improvement.
