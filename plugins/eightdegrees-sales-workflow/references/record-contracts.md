# Original record contracts

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

New approved-persona-snapshot records include client_id=location_id:contact_id,
content_version, facts, approved=true, original source_page_id,
approved_input_sha256 and actual CRM result fields. Never guess identity from
headings/names. For a legacy snapshot missing client_id, pass original complete
settings_page to contact.restriction-plan/verify: its unique RunSettings
client_pages entry must bind exact location_id, contact_id and persona_page_id.
The helper inserts above the unique original snapshot for localized headings,
preserving every approved byte. A conflicting or unavailable binding refuses.

New sales-send-package records include content_approval={task_page_id,
action_page_id, decision: Confirm, content_version}, referencing the actual
accepted review and content_approval_sha256. Legacy pointer-only packages are
readable only when content_approved, content_task_page_id/content_action_page_id
and content_approval_sha256 match the original completed review's actual
accepted-action-submission. This adapter neither invents approval nor rewrites
the frozen package.

Persist email-handoff-proof with verification (ProviderHandoffVerified phase=handoff),
request (the exact dispatched arguments), manifest, the pre-dispatch
StoredReplyVerified result, original provider_result and accepted_at. Use only
the response's actual ID. No sent raw MIME or sent RFC Message-ID is required.
Legacy email-sent-proof and RFC/receipt metadata remain immutable historical
observations; do not fetch new evidence or create recipient-receipt work.

RecordMaterialHandoff recovery has a DISTINCT task. Save
material-handoff-recovery-v1 with original_send_task_id and original current_outcome;
SourceURL identifies the original email task, ContentVersion stays unchanged.
Pass saved_recovery_task along with input, saved_email_task and saved_cycle to
material.verify. It validates the original task/version/message and both saved
event records, returning entity_id=recovery task, email_task_id=original send,
and projection_page_ids. Freeze kind=material-handoff on that recovery task;
register email/cycle as publication roles. Include page-links AND task-display
for its read-only result page. Normal send completion omits saved_recovery_task
and continues to target the original email. Never manually retarget a success
JSON, omit a missing check, rewrite old provider proof or send again.
