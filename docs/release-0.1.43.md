# EightDegrees Sales Workflow 0.1.43

Fix durable source-to-owner recovery and fresh scheduled rules. Native wakes load current_rules.py and enter the scanner/current guard directly, independent of public run-auto and start/stop administration. Explicit start reuses and registers observed existing task configuration; stop and revoked business access remain effective. No recurring task is created, duplicated or modified.

scan.probe retains pending/handled work across scope changes, revalidates actual feed snapshots and derives Complete/NeedsBaseline from real coverage with targeted recovery actions. backlog.recover reuses original sources and resumes missing handoffs through RecoverSourceHandoff even when ReadMessageBody was completed. Unknown effects remain reserved, but do not globally block unrelated customers/channels.

cycle.metrics records actual timer evidence, guard, persisted progress, counts, waits, blocks, elapsed time, recovery pointers and rule version/hash. Ready/no-progress without a concrete blocker is rejected; repeated faults have stable notice keys. Dispatch windows affect sending only. Exact email/CRM approval, factual SMS authority and accepted/unknown no-resend rules remain.

Validation: automated regression and package checks are recorded in the accompanying task artifacts. Offline results do not establish native trigger, restart recovery, two actual timer cycles or cross-version adoption. Those require original live evidence; do not claim complete local reliability from package release alone.
