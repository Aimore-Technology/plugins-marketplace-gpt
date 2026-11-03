# EightDegrees Sales Workflow 0.1.37

The 0.1.36 rehearsal completed the mail-to-notification chain, but found intake
preparation ahead of a durable checkpoint, lost review bindings, duplicate or
stale current text, and compaction briefly changing the executor's role.
This release adds prospective guards and repair plans without rewriting those
failed observations or replaying a provider action.

## Changes

- `intake.plan` prepares a prospective receipt from an original saved source;
  `intake.handoff` requires its actual saved checkpoint and exact source/version.
  New sales content/reply-patch/review plans require that proof before facts.
  Old identity-less checkpoints need explicit prospective recovery, not a
  retroactive ordering pass. New send packages retain the original source ID.
- Exact Notion mutation simulates the proposed whole body before returning
  arguments. It rejects lost/rebound action bindings and duplicate live current
  sections, while allowing atomic cleanup and ordinary human submissions.
  A verified new email review version retains the old binding as history.
- Email presentation synchronizes canonical task bodies, original actions and
  the matching original incoming source. Source final completion follows the
  full owner gate, avoiding a circular prerequisite or an early final write. Inbox uses its Processing/Processed states,
  distinct from task InProgress/Completed.
- Checkpoint reconciliation retires stale waiting work only from matching
  original terminal tasks/versions. Legacy work-only waits are supported.
  Unknown attempts, reservations, restrictions and old captures are preserved.
- Invocation recovery pins one exact public command, actual executor/turn and
  original budget. Compaction does not grant a test-controller role, peer
  messaging, another invocation, an extended budget or permission to resend.
- A missing-metadata legacy Business run can receive only a generated Summary
  pointing to its original terminal task. Old State/version/source/failure
  history stays unchanged; this is not a general metadata-validation bypass.

## Validation and limits

Both editions pass 525 offline tests, including 22 new handover/publication/
recovery regressions. Marketplace validation and package checks pass.
Read-only replay of original 0.1.36 captures verifies rejection of a missing
handoff, binding removal and duplicate output, accepts the original duplicate
cleanup, verifies email/source synchronization and summary-only legacy repair,
and retires the actual stale Cypress waiting work item. Originals are unchanged.
The prospective intake fixture simulates a separate saved receipt; it does not
prove the historical handoff had correct ordering. Customer evidence stays
outside the distributed package.

No live mail/SMS, native schedule or Notion repair was executed to validate this
release. Fresh seven-cycle execution, compaction recovery, timing and cloud
unattended behavior remain to be tested. Existing 30-minute/optional20-minute
cadence, bounded budgets, approval/stop/count/window/unknown checks and successful
original Gmail/AndroidSync handoff completion remain. No external status or
delivery query is introduced. Public commands and plugin identities are unchanged.
