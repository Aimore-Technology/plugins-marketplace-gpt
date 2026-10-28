# Standard CRM Notes

Use for initialization, communication review and every CRM Notes append. GHL Notes is treated as plain text. The packaged [template](../assets/crm-note-v1.txt) is the canonical layout, version `aimore-crm-note-v1`. Create/reuse `Aimore/Templates/CRMNotes` at init and register its page ID and template version in RunSettings. Save the template in a Notion code block plus localized field guidance; copy only the code block's contents into the CRM payload, never its fence. Do not install a filled customer example.

## Review payload

Keep the header labels, section names and order stable. Localize bullet prose using the workspace language; customer/source language is independent. Use plain `- ` bullets, literal URLs and normal line breaks. No Markdown emphasis, heading markers, code fences/backticks, Markdown links, tables, HTML, Notion mentions or serialized JSON in CRM Notes. Notion review pages may use those features outside the exact plain-text payload.

Required header values: CommunicationId, ContentVersion, CommunicationTime, Timezone, Source, LocationId, ContactId and Customer. IDs and Source must be verified, never placeholders. CommunicationTime is the original communication instant, converted to the stated IANA timezone with an explicit numeric offset; do not substitute processing/approval time. If genuinely absent, use `Not provided`, retaining a known display timezone. A missing customer display name may also be `Not provided`; verified LocationId/ContactId are still mandatory.

Each of the four sections needs at least one plain-text bullet:

- Context Background: source-backed background and confirmed facts. Include every proposed persona change here, explicitly labeled as a proposed change for review; no separate free-form fifth section.
- Action: actions actually performed; do not claim the proposed write or suggestion has already happened.
- Recommendation: label AI/operator origin and whether each suggestion is executed or pending. `Not provided / To confirm` is acceptable when absent.
- Next Schedule: next action, owner and time, explicitly marking unknown values rather than inventing an appointment.

Persona-update receives this complete combined payload. It must not append another persona section, prepend an actor banner or reformat the approved text. Approval/attempt evidence belongs in the original Notion task/log, linked to the exact note digest.

## Offline render and validation

On a host with Python 3, use [crm_note.py](../scripts/crm_note.py), which has no network, CRM or approval capability. Its input is UTF-8 JSON with exactly these keys:

```json
{
  "template_version": "aimore-crm-note-v1",
  "communication_id": "communication-unique-id",
  "content_version": "notes-v1",
  "communication_time": "2026-10-28T22:33:11+10:30",
  "timezone": "Australia/Adelaide",
  "source_url": "https://www.notion.so/00000000000000000000000000000001",
  "location_id": "verified-location-id",
  "contact_id": "verified-contact-id",
  "customer_name": "Verified display name",
  "sections": {
    "context_background": ["Confirmed source facts; any persona proposal explicitly listed."],
    "action": ["Source saved and customer matched; no reply sent."],
    "recommendation": ["AI suggestion, pending: verify the missing project fact."],
    "next_schedule": ["Next action: verify source; owner: configured operator; time: Not provided."]
  }
}
```

The example is documentation, not test/customer data or permission to use its identifiers. Use an authorized temporary directory outside the repository:

```text
python3 <plugin>/scripts/crm_note.py render --input <payload.json> --output <note.txt>
python3 <plugin>/scripts/crm_note.py validate --input <payload.json> --note <note.txt> --expected-sha256 <approved-digest>
```

Render checks required fields, timezone/offset agreement, sections and unsupported formatting before producing the note. Invalid input returns `NeedsCorrection` with exit code 2 and creates no note file. Validation compares exact UTF-8 bytes, including final newline, with the rendered payload and approved SHA-256. It does not establish customer identity, factual accuracy or approval. If Python/template/timezone support is unavailable, manually apply the same template/checklist and record `ManualTemplateCheck`; do not claim script validation. Never silently fall back to a free-form note.

## Before approval and before write

1. Before ContentReview, validate the complete combined note and proposed persona changes, then save the exact UTF-8 payload, template version, input snapshot and digest. Missing verified identity/source goes to ClientMatching/DataCompletion; malformed formatting or incomplete note returns for correction before approval.
2. Immediately before appending, fetch the original task/current approved payload, recheck mapping/version/mode/decision and prior attempts, and validate the exact payload again. Send the approved plain text without additions or conversions. API request JSON may wrap it; JSON serialization is not the Notes body.
3. If an approved legacy note lacks fields or changes are needed, retain it and submit a new version for ContentReview. Do not silently repair approved bytes or rewrite an existing CRM note. For an already written incomplete note, preserve the append result and upsert one ExecutionExceptions quality task keyed by CommunicationId + approved version + NoteQuality, linking the actual NoteId, missing fields and original review/run. Do not duplicate it per scan. Obtain an explicit decision on any corrective new version, avoiding duplicate append on retry; ordinary schema upgrade must not automatically append corrections.
4. Read back the actual CRM body and compare exact text/digest where supported. Record any provider normalization explicitly; an unverified difference is not an exact match. A successful API call with an incomplete or mismatched body is not quality acceptance. Save the NoteId and original approved version separately from quality status.
