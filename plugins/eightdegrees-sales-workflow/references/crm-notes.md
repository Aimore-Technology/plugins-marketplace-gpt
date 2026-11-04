# Standard plain-text CRM Notes

Use assets/crm-note-v1.txt and crm_note.py for the fixed plain-text template.
No Markdown/HTML/fences in the actual CRM body. Keep CommunicationId,
ContentVersion, original CommunicationTime/Timezone, Source, LocationId,
ContactId and Customer, followed by Context Background, Action,
Recommendation and Next Schedule. Unknowns remain Not provided/null as applicable.

Manual communication/persona fact changes need their one exact-version Notes
review. An inquiry does not call that workflow just to obtain a name or draft.
An operational send-result Note uses send-receipt-v2 and the combined email
approval's recorded receipt scope, without approving new customer facts.

Render once, validate its complete proposed payload before submitting and append
once with the original source/version/attempt key. Save actual API success and
NoteId; do not fetch the saved body or compare hashes. Reuse a prior successful
append. Unknown legacy attempts need scoped existence reconciliation before any
retry. Never overwrite conflicting facts or repeat a Note for presentation repair.
