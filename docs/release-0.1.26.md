# EightDegrees Sales Workflow 0.1.26

Unattended approved-work reliability fixes after the 0.1.25 inquiry run. No new
service, connector or permission model is introduced. Business fact and email
approval stay in Notion; factual SMS retains standing authority. Upgrades create
no schedule and do not broaden disabled/revoked or stopped work.

## Change and reviewer path

Start at references/unattended-operation.md, scripts/scan_cycle.py and
tests/test_unattended.py. Bounded scans use an eight-minute soft budget with one
minute for publication and 12 owner steps, persist original cursor/work/receipt
pointers and reconcile unknown attempts after restart. One verified serialized
native owner is required; a Notion timestamp cannot establish an atomic lock.
Old observed coverage is not fresh coverage when the current source read failed.

scripts/sms_presentation.py binds the frozen notification and actual provider
request to seven original task/action/run/cycle pages. A status update converges
those surfaces without another request, count reset or reopening a stopped
cycle. Pending is machine waiting, network-send is not handset delivery, and
failed/unknown requests are never fabricated as successful. Completion guards
require saved projection evidence for the new maintenance routes.

scripts/contact_preferences.py maps a direct same-enquiry customer stop source
to a separate current persona restriction overlay, above the old approved
snapshot. Scope and quote must be explicit; ambiguous source/scope blocks the
affected item. The overlay cannot rewrite approved facts, set global CRM DND or
automatically re-enable contact. CRM Notes review remains independent.

The email projection planner now catches the actual version-bound English and
Chinese current-package heading/adjacent stale approval sentence. It changes
only display labels, preserving frozen package/approval/provider bytes. CRM
Notes reject persona-review workflow labels before review while retaining
legitimate pending finance facts. Idle ticks avoid unchanged writes/notifications,
full history sweeps and repeated raw-capture serialization.

## Verification and impact

359 offline tests per edition, portable marketplace/ZIP validation and shared
payload comparison. Tests include five restart cycles, unknown-result
reconciliation, completed-step suppression, pending/failure status, unrelated
human/future waits, conflicting executor observations, partial/unsaved source
coverage, source-bound scoped stop, exact saved readback and owner completion.
A local replay of authorized original stop/persona captures preserved the whole
approved snapshot and produced zero changes on repetition. Original email
captures verify label repair separately; customer material is not distributed.

No new dependencies, credentials or customer captures in the package. Helpers
have no network/send/CRM capability and grant no approval. Current source/stop/
approval/attempt checks remain necessary immediately before external effects.
Original approved records remain unchanged; only additive checkpoint/overlay
records and current workflow-owned projections are new. Existing user settings
are preserved; explicit init adds missing defaults and readiness fields.

Live Notion reads were unavailable during this fix. The seven-page SMS path has
synthetic recovery/readback coverage, not a new live seven-page acceptance.
Actual native Work/Cowork serialization, continuous ticks, interruption timing
and cloud connector access need host acceptance. A soft budget cannot cancel an
in-flight provider call; its overrun is recorded and no further work is admitted.
Do not label these checks as production unattended, delivery or Claude acceptance.
