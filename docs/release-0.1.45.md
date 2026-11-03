# EightDegrees Sales Workflow 0.1.45

A replay of actual Notion row captures found that a source-key email may be presented as a mailto link. Exact text comparison missed the two existing ClientMatching tasks and proposed another source handoff. Decode only the exact matching email-label/mailto rendering, retaining the original source/task. A conflicting SourceKey and SourceURL produces a scoped identity-repair block, not another task. Arbitrary links and mismatched mailto labels are never accepted as canonical identities.

Regression coverage uses the real response shape with synthetic addresses; actual authorized captures were replayed locally: before the fix two original waiting tasks were missed, after the fix both are reused as human waits with zero new handoffs. No original source, customer approval or provider action is rewritten.

Includes 0.1.43 current scheduled rules, durable backlog/baseline recovery and metrics, and 0.1.44 visible business setup/audit. Automated and package checks remain distinct from native trigger/cycle/restart acceptance. No claim of full local reliability until original live evidence meets the acceptance criteria.
