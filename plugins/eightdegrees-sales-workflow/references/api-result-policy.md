# API write results and minimal reads

Current policy: api-result-v1. This governs every command and scheduled wake.
It supersedes older instructions requiring post-write body, byte, hash, saved
projection or downloaded-preview comparisons, including CRM. New owner plans
use execution-api-v1. Frozen historical contracts/results stay as history; new
unfinished phases use the current policy without repeating completed effects.

## Normal success path

1. Before submission, check the intended target and proposed payload once,
   including the actual approved email/CRM version when required. Use the fixed
   Notes renderer and exact-call Notion preflight locally. Freeze the same local
   HTML/asset package used for review and submission. Do not regenerate it.
2. Submit once. Inspect the original response for errors and save its returned
   record ID. Successful API response + record ID finishes that write. For an
   update API returning only explicit success/204, retain its known target ID.
   An empty envelope/isError=false alone is not a successful write receipt.
3. Use write.confirm in local_checks with service, response, actual request,
   optional expected_id (physical API record), entity_id (owning workflow page),
   purpose and content_version. The helper returns APIWriteConfirmed. It does
   not fetch, compare saved content or grant approval. A batched create must
   select the actual returned ID for each planned role; do not invent IDs.
4. Continue immediately. No fetch-after-write, raw Gmail MIME readback, CRM
   body comparison, preview download/hash loop or repeated status/plan fetch.
   Local preflight hashes bind our submitted/approved package only; they do
   not claim the provider's stored body was read or compared. Keep original
   errors/responses and own request in local captures, not the chat context.

Only a timeout/error/unknown result requires scoped reconciliation. Preserve its
original attempt and search by the saved record/request key for existence, not
body equality. Supply expected_id and existence_response to write.confirm only
after resolving that original identity. Do not blindly retry, duplicate a Note,
source or provider request. An explicit refusal is a failure, not completion.
Unknown Gmail/AndroidSync dispatch retains the existing no-automatic-resend rule;
this policy does not introduce transport polling or delivery checks.

## Pre-call protections and stable workspace

Keep current stop/revocation, scope, recipient/account, exact approval version,
send window/count, original attempt and reply restrictions. Read each relevant
live record once for the imminent external action, reuse it across local checks,
and refresh only after an actual intervening event/change. A stored successful
write is not a new approval. Do not use submitted AI content as human input.

Reuse init's actual root/database/page IDs, complete schemas, template versions
and client mappings across runs. Do not rediscover the tree or re-audit every
folder/capability. Refresh static metadata only for explicit init/configuration
change, a relevant observed version/schema change, or an actual provider error.
Read current RunSettings/scan switch and changed human inputs; do not cache live
approvals, stop states, attempts or new inquiry discovery across cycles. Read
only the relevant authorized Dropbox files; no broad search to confirm an
unchanged folder still exists. Full absence audits belong to explicit diagnosis.

## Helper adapters (no post-write fetch)

- execution.prepare defaults to execution-api-v1; execution.ready takes the
  original prepared output, role bindings and run_write={response,request}.
- Completion requires receipts for affected Notion records and this phase's
  actual CRM/draft/dispatch/handoff effects. Reuse the pre-call route result.
  A review phase never requires its future send, receipt or SMS outcome.
- reply_transport.verify takes manifest plus write_result={response,request};
  use actual draft/message IDs returned by Gmail when freezing the manifest.
  Same-version approved package + draft acknowledgement replaces raw MIME reads.
- review.prepare takes transport above, preview={kind,input}, and
  publication_writes={copy,asset,preview}, each a write.confirm input. Include
  prepared_copy from local generation (task_page_id, content_version, subject,
  html_sha256), binding that editable copy to the submitted package. Each has
  actual expected_id; the image input includes its local render_manifest,
  content_version and html_sha256. Render/inspect the local preview before
  publication; successful copy, upload and preview-page responses finish it.
- send_receipt.verify accepts write_result for the original CRM append. CRM
  persona/Notes writes use write.confirm(service=crm,purpose=crm-note). Save the
  returned NoteId; do not fetch it for body verification.
- intake.verify accepts checkpoint_record (the exact submitted local record),
  checkpoint_page_id and checkpoint_write instead of fetching checkpoint_page.
  Source identity/root/version checks remain on the existing source capture.
- dispatch.prepare accepts admission_write instead of saved_run; the original
  prepared admission and fresh current dispatch eligibility still apply.
- scan.control-verify accepts write_result instead of saved_settings. The next
  wake reads the current live switch; start never overrides a later real stop.

Old strict-readback helper branches remain for interpreting frozen history or
explicit diagnostics. They are not the normal execution path and must not add
remote reads to a new invocation. A user asking to diagnose a concrete problem
may explicitly request a scoped inspection; routine successful writes need none.

For the existing inquiry-only CRM no-match path, freeze the task resource's
crm_recording=pending-unmatched, crm_match=none, crm_search_complete=true and
actual crm_pending_task_id before dispatch. Completion needs that recovery
record's write acknowledgement, not a fabricated CRM Note receipt. This exception
is only for source-bound inquiry sends; manual Notes/persona still require CRM.
