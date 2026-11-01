# EightDegrees Sales Workflow 0.1.28

A real local simulation sent the approved mail correctly but could not close
handoff recovery or refresh contact/receipt displays. Approved records used
legacy identity/RFC layouts, and recovery evidence targeted the original send
instead of the distinct recovery task. Long post-send repair also starved intake.

Changes: read legacy persona identity only through the actual settings binding;
accept consistent top-level/nested RFC proof and original accepted approval
pointers without rewriting frozen records; return separately bound recovery
completion evidence. Scan admission selects one fitting owner at a time, prioritizes
sources over optional repair, suppresses stale completed digests and reconciles
unknown attempts across changed versions. SMS capability has a separate setup
input and an explicitly scoped single diagnostic slot, not repeated per-message
approval or ordinary readiness. Health updates use real service observations;
report-only remains unable to repair business/Health records.

Reviewer path: scripts/contact_preferences.py, email_presentation.py,
material_handoff.py, scan_cycle.py, sms_channel.py and test_live_record_contracts.py.
The new references/record-contracts.md and sms-channel-setup.md define exact
original layouts and setup behavior. Existing permissions, identity checks,
freeze/readback requirements, provider retry boundaries and stop rules remain.
No backend, connector, secret or native scheduling capability is added.

Verification: full offline tests, package checks and three private real-record
replays (persona restriction, receipt display, distinct handoff recovery). Public
regression fixtures contain synthetic data only. An actual latest-version fresh
workspace rehearsal follows publication; offline pass does not certify the cloud,
phone delivery, live scan timing or overall unattended readiness.

Equivalent reviewed change record: diff inspected for scope, identity/approval
preservation, original evidence binding, unknown-slot safety and customer-data
exclusion. Platform packages are compared before release; revisions and build
results are retained outside customer workspaces. P0 repair/acceptance stays
IN_PROGRESS until the fresh live rehearsal establishes its results.
