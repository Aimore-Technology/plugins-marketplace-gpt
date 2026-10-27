---
name: eightdegrees-client-persona-update
description: "Apply explicitly approved customer persona changes from communication processing, append one combined CRM note and verify the corresponding Notion snapshot."
---

# Apply approved persona changes

Read [operating-contract](../../references/operating-contract.md) and the CRM section of [notion-model](../../references/notion-model.md). This is a downstream step, not an independent scheduled job. Reuse the parent RunId and approved version; do not call communication processing back.

1. Require verified LocationId/ContactId, CommunicationId, approved Notes, explicitly approved persona changes, approval evidence and prior step results. Read the latest CRM record. Missing identity goes to ClientMatching; changed/conflicting facts or expanded scope go to ContentReview. Do not repeat approval for the same still-valid version.
2. Apply only confirmed property type, dwelling/bedroom preferences, buyer status, provided age-band reference, budget and other approved facts. Leave unknown or unchanged values intact. Default CRM storage is the existing Notes/activity log; no custom-field creation. Structured fields are optional only with verified existing mappings.
3. Combine the upstream Notes and approved persona changes in ONE append keyed by CommunicationId + approved version. Check whether that exact append already succeeded; reconcile unknown results before retry. Update only enabled, approved structured mappings. Read back each actual result; save the Notion approved snapshot, source/version and external record IDs. Do not overwrite conflicting existing facts silently.
4. Return individual completion states: Notes synced; structured fields synced or not enabled; Notion snapshot synced or pending. A disabled structured mapping is not a failure or a claim that fields were updated. An enabled mapping error, wrong target, permission failure or unknown write becomes ExecutionExceptions; preserve successful steps.

Finish when approved changes are reflected through the configured CRM write mode, verified by readback, and the Notion snapshot/status agrees. No customer sends or new contacts.
