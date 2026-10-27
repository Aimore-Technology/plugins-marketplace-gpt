---
name: eightdegrees-communication-context-process
description: "Process authorized customer email, text or transcripts into reviewed CRM Notes and approved persona changes; P0-A starts and resumes manually at John's request."
---

# Process customer communication

Read [operating-contract](../../references/operating-contract.md) and [notion-model](../../references/notion-model.md). Default Mode=Manual for John's P0-A request. Only an explicit upstream automatic workflow may supply Mode=Automatic for a separate new item; it cannot adopt an existing Manual task.

1. Save/reuse a source-linked Inbox record for the authorized email, text or transcript. Record account, original time/timezone and immutable SourceKey/CommunicationId; keep source and derived notes distinct. Link raw Gmail/Dropbox content rather than mirroring it. Sensitive originals follow manual handling.
2. Match within the configured CRM LocationId using email/phone; use names/social profiles only as supporting data. Ambiguity, absence or conflict becomes ClientMatching with exact candidates/missing input and original source. John selects or supplies data; no guessing or automatic contact creation. Manual mode waits for an explicit continue request after saving.
3. On verified mapping, move/link the record under `Clients/{ClientId}/Communications`, retaining source/page identity when supported. Record mapping, processing state and local timestamp + unique title suffix. Reuse any valid upstream mapping instead of asking again.
4. Produce the four-section Notes from notion-model, separating confirmed facts, actions, suggestions and unknowns. Read the approved persona/template to propose only supported changes. Persist one ContentReview covering the exact note and explicitly listed persona changes. John may edit, confirm or return; confirmation is not permission to send. Retain the approved version; new conflicts require a new review.
5. On a valid decision and manual continue where required, reread the CRM target/latest records and check completed writes. With NO persona changes, append the approved Notes once. With persona changes, pass the approved Notes and changes to [persona update](../eightdegrees-client-persona-update/SKILL.md), which owns ONE combined Notes append. Do not prewrite a duplicate note. Key reconciliation by CommunicationId + approved version; only mapped/verified structured fields may additionally change.
6. Read back actual CRM results; save the approved Notion note/persona snapshot and per-step sync status. Return target, external record IDs, confirmed version and task/run links. Partial failure or unknown state goes to ExecutionExceptions; manual mode waits for John's explicit retry/continue and reconciles before filling missing steps.

Finish only when source is traceable, customer verified, proposed changes approved, CRM result read back and Notion sync state consistent. This skill sends no customer email/SMS, starts no timer, calls no scanner, and never changes an existing Manual task's mode.
