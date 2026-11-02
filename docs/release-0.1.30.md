# EightDegrees Sales Workflow 0.1.30

Real-estate pilot inquiries do not need a fixed 15-minute polling cadence.
The 0.1.29 seven-cycle local simulation completed actual email, CRM and SMS work;
its active cycles took roughly 9.5 minutes from dispatch to observed completion.
The former 480-second budget deferred eligible successors and recorded two
performance overruns despite successful business outcomes.

New installs now default to a 30-minute native task. The existing start command
accepts interval_minutes=20 as an explicit faster option; an unqualified start
preserves a supported saved choice. Native capability and exact task readback
must match the chosen interval and the interval is bound into its prompt.
Unsupported cadence never silently falls back. An owned legacy 15-minute task
is updated in place on explicit start or can still be stopped before migration.
Installation/init do not create or alter a live native task.

The soft cycle budget becomes 900 seconds, including a 120-second publication
reserve. New owner admission stops at minute 13. Phase/item limits, executor
ownership, original attempts, current approvals and reply/stop checks remain.
The planner exposes elapsed/budget/reserve/overrun evidence without rewinding
successful provider results. Explicit customer limits (including 480/60) stay
until the operator deliberately adopts new defaults; historical overruns retain
their original limits. The unchanged 19-minute reminder threshold may be observed
late under 20/30-minute polling; actual lateness must remain visible.

Both editions share business helpers, defaults, instructions, command guidance
and the scan-timing Experience card. GPT keeps Work-native guidance; Claude
keeps Cowork-native guidance and command wrappers. No customer records, actual
schedules, permissions or connections are changed by this release.

Verification: regression tests cover exact 20/30 selection/readback, saved-choice
reuse, owned-task update and legacy stop, unsupported/invalid capability data,
cadence/ownership/overlap guards, new and legacy budget boundaries, durable
remaining work and retained completed results after timing overrun. Full unit
discovery, marketplace/schema validation, deterministic ZIP inspection and
cross-edition shared-file comparison are required before publication. Release
evidence is traceable to each repository's commit and CI; live Work/Cowork
recurrence remains a separate, unperformed acceptance test. This is a cadence
and budget configuration update, not a claim of faster execution.

Verified before publication: 399 offline tests passed in each edition; both
marketplace/schema gates and deterministic archive inspection passed. All 97
shared business files match byte-for-byte. Source review includes the actual
legacy saved target=15 migration, exact 20/30 readback and both native runtime
labels. Existing cloud/recurrence acceptance limits remain explicit.
