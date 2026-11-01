# EightDegrees Sales Workflow 0.1.27

Fixes a blocking 0.1.26 regression found in the live simulated inquiry: a public
run-auto paused before consuming the submitted review because it required
cloud-wide executor serialization even though scheduling was stopped and one
conversation was explicitly designated. No CRM/customer send was attempted.

scan_cycle.py now accepts a separate BoundOnDemand observation basis only for
one-cycle-approved-work and one-cycle-no-customer-send. It requires original
saved root/thread selection, actual matching current thread/turn, complete
installation scan coverage without another active scan, and a stopped disabled
scheduler with no IDs or pending native attempt. Conflicting active IDs still
block. Unrelated host conversations are not installation scan workers. Native
scheduled-approved-work still requires original host serialization and schedule
guards; this change grants no native readiness, approval or send authority.

Explicit init records/reconciles the actual designated on-demand thread while
preserving submitted action pages, versions, attempts and disable state. The
existing NoSend policy, latest stop/approval/attempt checks and cloud gating
remain. Local capture normalization is model-assisted, not an atomic lock or
host middleware. Review scripts/scan_cycle.py, references/unattended-operation.md
and tests/test_unattended.py.

Verification: 361 offline tests per edition, marketplace/ZIP checks, explicit
negative cases for wrong root/thread/turn, partial reads, competing scan, active
or unknown native scheduling, and attempted fallback under scheduled/report
policies. These tests do not establish native cloud availability or timing.
