---
name: eightdegrees-automation-control
description: "Create, reuse or delete one native 15-minute approved-work task: Work GPT task for GPT, Cowork cron task for Claude. Does not immediately scan or send."
---

# Start or stop approved periodic work

start establishes one native 15-minute cycle using [scheduled work](../../references/scheduled-work.md);
stop deletes it. Apply [schedule lifecycle](../../references/scheduling.md) and
the edition's [runtime](../../references/platform-runtime.md). The scheduler
operation itself scans/sends nothing and supplies no business approval. Before EVERY Notion page write, including setup/status/log fields, run [exact-call preflight](../../references/notion-mutation.md); require exit 0 and NotionMutationPrepared and use the returned unchanged arguments.

1. Read current RunSettings and actual selected native runtime tools. Require
   real root/operator/mailbox/scope/connector setup. GPT targets a cloud Work GPT
   task; Claude targets Cowork native cron. Discover automation_update first when
   exposed, then use actual native schemas; keep required host UI confirmation.
   If this chat cannot manage that runtime, return the exact setup limitation and
   Work/Cowork next action. Never substitute a Codex project worker or daemon.
2. Use [execution preflight](../../references/execution-preflight.md) to generate,
   persist and read back the scheduling-only owner plan before dependent writes.
   Establish the [owner completion contract](../../references/owner-completion.md). Read complete
   native listing including paused tasks and actual owned task prompts. Resolve
   previous unknown native attempts and competing executor ownership first.
3. Start reuses/updates one exact owned task or creates after proven absence.
   Save intent first and verify actual task ID, cloud Skill/connector access,
   prompt, 15-minute cadence, timezone and enabled state. Then set Running and
   approved_work_enabled=true. A package/init upgrade never enables an old no-send
   lifecycle; explicit current start is required. This still grants no content
   or send approval and never enables an unverified automatic SMS channel.
4. Stop sets StopRequested and approved_work_enabled=false, deletes only proven
   owned IDs, and verifies complete native absence before Stopped. Pause, a local
   flag, missing API or unknown deletion is not success. Preserve history,
   approvals, business tasks and unrelated schedules.
5. Verify final owner result/log scope and return actual native links. Reconcile
   uncertainty without another create/delete. Installation, init and public
   run-auto create no jobs; Claude live runtime remains untested until observed.

## Operator path and local checks

Apply [operator experience](../../references/operator-experience.md) for Today, short review summaries/differences, verified prefill and explicit post-submit guidance. Give concise chat progress at meaningful stages; an internal read/check does not require another Notion status write. Run [local check batches](../../references/local-check-batch.md) over unchanged original captures instead of repeatedly serializing/rereading them. Preserve every required fresh external-action and saved-result check. Verified Today linked views replace manual queue snapshots; legacy queue mode remains until explicit upgrade.
