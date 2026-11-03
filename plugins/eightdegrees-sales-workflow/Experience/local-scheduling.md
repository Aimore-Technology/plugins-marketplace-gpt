# Local scheduling without a unique executor

Use this card for start/stop, a periodic tick or legacy task migration.

0.1.41 removes the unique executor requirement from business execution, including
scan admission, scheduled routing, dispatch and compaction recovery. Do not ask
for native host/thread/turn/task invocation identity or serialize all conversations.
An existing local tick uses schedule-execution.md with actual RunSettings and
task-state-v2; a local RunId is just a log label. Legacy assigned-thread and
single-owner flags are inert immediately, without init or rebinding.

Only start/stop manages native jobs. Keep its actual native ID/account/host/
directory evidence for correct creation, reuse and deletion. Maintain one
configured scanner per root; management target identity is not a business
executor identity. Do not relabel/drop unresolved cloud IDs to create duplicates.

Per-task approvals, stop state, source/context scopes, counts and original
AttemptIds remain. Completed effects are skipped. Pending/unknown requests are
not resent. Another session alone does not block independent work. Notion
provides no atomic parallel exactly-once guarantee; use actual provider
idempotency support and never claim a global lock.

Keep the selected computer/app available. After restart discover current events
once, not each missed tick. No management APIs are needed for execution.
Offline tests do not certify live scheduler timing or concurrent delivery.
