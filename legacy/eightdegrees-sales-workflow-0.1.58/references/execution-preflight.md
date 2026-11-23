# Other-owner and legacy repair preflight

Normal inquiry email uses [email-flow](email-flow.md), without these extra owner
plan stages. This resource covers manual CRM/other-owner work and explicit
legacy repair only.

Use [API results/minimal reads](api-result-policy.md). New execution.prepare plans
are execution-api-v1. Preparation validates proposed facts, Notion values,
reply parameters, source intake and one current ResumeStep before any dependent
write. Do not include future send phases in a current draft/review plan.

Input fields remain owner_skill, policy, operation, invocation_id,
publication_version, resources, and the actual proposed facts/notion_rows/reply
when relevant. Each resource has a unique role, type, actual entity_id or null
creation slot. Exactly one run is required. Tasks have content_version and
resume_step; actions bind task_role. html/image-preview resources retain their
frozen package versions. Reuse actual registered schemas, not guessed enums.
A changed proposed payload is checked once before its actual submission.

1. Run execution.prepare via local_checks. A failed preflight stops dependent
   writes. Persist its exact execution_plan/plan_sha256 and generated run_properties
   on the owning WorkflowRun; include them in the initial create when new.
   Every Notion call still uses notion.mutation's exact returned arguments.
2. Inspect the write's original response. Run execution.ready with prepared,
   bindings (role to returned IDs for declared creation slots), and
   run_write={response,request}. No saved_plan fetch is required. The helper
   checks our local original plan/preflight and the run write acknowledgement;
   it never compares remote content. A failed/unknown write needs reconciliation.
3. Retain registry/required_checks and ready's execution-plan result. Check the
   current original task route once before its business action. Reuse that
   result locally; final completion does not re-read a terminal task as a route.
4. Collect write.confirm receipts for affected Notion records and the generated
   current-phase external effects. Use completion-gate and owner-write (or the
   narrower report-write) before final Completed/Success. Save final changes,
   confirm their original API responses and return actual links. Never fetch
   the final body to compare. A later human decision is read when observed.

Generated receipt kinds: api-write for each affected Notion role; route for
current tasks; draft acknowledgement for ReviewReplyDraft; CRM Note
acknowledgement for actual approved Notes/receipt phases; original provider
handoff for send phases; standing SMS authority for notification dispatch;
material-handoff persistence for a material send/registration. A content proposal
for ReviewCommunication does not require the future approved CRM append.

write.confirm fields: service, response, request, expected_id when known,
entity_id (workflow task for external effects), purpose, content_version.
Required purpose/service come from the generated specs. For a Notion write,
record_id must identify that resource. For CRM, record_id is the actual NoteId;
entity_id remains the owning task. API acknowledgements never grant approval.

Frozen execution-v1/v2 records remain history. legacy-readback is a diagnostic
compatibility mode, not the current default or a reason to repeat old effects.
If an old phase is unfinished, preserve it and create a linked current phase
using the actual previous attempts/receipts; never fabricate historical success.
