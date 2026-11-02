# EightDegrees Sales Workflow 0.1.34

An explicitly initiated new inquiry could not register its notification SMS when
the same customer had a closed cycle for another project. The helper demanded
new-context authorization but offered no way to consume the saved initiation.
The mail handoff succeeded while SMS never reached AndroidSync. This was an
internal business-flow defect, not missing delivery evidence.

material.plan now reads the original registered RunSettings context override
and inquiry binding. It checks installation, account, CRM customer, source,
recipient, standing authority, expiry and count/timing limits. A scoped stop for
another project stays on that project. Current/global SMS stops, CRM guards,
Pause, revocation, unknown attempts and closed/capped related cycles still block.
One active cycle per customer and manual+AI counts remain unchanged. Saved
one-message limits and explicit zero-delay exceptions are not widened/reset.

The original zero-attempt ClosedPriorContextBlocksExplicitNewContext stub may
recover only after exact original cycle-page readback, fresh valid saved
initiation, and no stop/pause/attempt/outcome/reservation. Keep the original page,
cycle/event identity and failure history. Recovery does not re-send the accepted
email, duplicate its CRM receipt, create a separate schedule or require another
SMS approval. Expired authorizations are never extended automatically.

Both editions include 478 passing offline tests, including 16 new regression
methods with additional negative subcases. Frozen incident replay changes the
same original stub from Stopped to ReadyForNotification while preserving the
old stop and one-message cap. Marketplace/reference validation and deterministic
archive inspection pass; shared business payloads match. The helper plans and
checks saved evidence only: no account mutation or live SMS was performed by
these checks. Public-command AndroidSync handoff requires a separate live test.

This release does not alter native schedules or successful Gmail/CRM results.
Original Gmail/AndroidSync acceptance still finishes dispatch; no external
post-handoff status/delivery checks are added. The other 0.1.33 display and
historical checkpoint findings remain separate, not claimed fixed here.
