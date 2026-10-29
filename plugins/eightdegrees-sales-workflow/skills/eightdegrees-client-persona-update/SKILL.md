---
name: eightdegrees-client-persona-update
description: "Apply explicitly approved customer persona changes from communication processing, append one combined CRM note and verify the corresponding Notion snapshot."
---

# Apply approved persona changes

Before saving extracted/clarified customer boolean facts or persona snapshots, apply [customer fact semantics](../../references/customer-facts.md) and run the fact helper on the actual proposal. Unknown is null, never a default false.

Before the first owner mutation, establish the [owner completion contract](../../references/owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action.

Read [operating-contract](../../references/operating-contract.md) and the CRM section of [notion-model](../../references/notion-model.md). This is a downstream step, not an independent scheduled job. Reuse the parent RunId and approved version; do not call communication processing back.

1. Require verified LocationId/ContactId, CommunicationId, the complete approved plain-text Notes payload/digest, explicitly approved persona changes, approval evidence and prior step results. Revalidate using [CRM Notes](../../references/crm-notes.md); persona proposals must already be included in that reviewed payload. Read the latest CRM record. Missing identity goes to ClientMatching; missing headers, formatting changes, changed/conflicting facts or expanded scope require a corrected new ContentReview. Do not repeat approval for the same still-valid complete version.
2. Apply only confirmed property type, dwelling/bedroom preferences, buyer status, provided age-band reference, budget and other approved facts. Leave unknown or unchanged values intact. Default CRM storage is the existing Notes/activity log; no custom-field creation. Structured fields are optional only with verified existing mappings.
3. Append the upstream complete combined note exactly once, keyed by CommunicationId + approved version. Do not combine, reformat or add a fifth section after approval; identity/actor/attempt evidence stays in task/log metadata. Check whether that exact append already succeeded; reconcile unknown results before retry. Update only enabled, approved structured mappings. Compare actual CRM Notes text/digest with the approved payload; save the Notion snapshot, source/version and external IDs. A provider success does not erase a content-quality failure. Do not overwrite conflicting existing facts silently.
4. Return individual completion states to the communication owner; do not mark its parent run complete from this child. A persona exception closes only its own registered task through owner-write. Return individual completion states: Notes synced; structured fields synced or not enabled; Notion snapshot synced or pending. A disabled structured mapping is not a failure or a claim that fields were updated. An enabled mapping error, wrong target, permission failure or unknown write becomes ExecutionExceptions; preserve successful steps.

Finish when approved changes are reflected through the configured CRM write mode, verified by readback, and the Notion snapshot/status agrees. No customer sends or new contacts.
