# Short email helper inputs

All operations run through local_checks.py with named original captures and
--output. They call no connectors. Capture original tool results once; do not
paste their full bodies or Python implementations back into model context.
Use actual IDs from responses, not the documentation placeholders below.

## email.prepare

Input: transport={manifest,write_result:{response,request}}, root_id,
source_page_id, source_key, source_write={response,request}, action_page_id,
operator_id, window={not_before,not_after,timezone}; optional language=en|zh-CN,
material=true (false for acknowledgement-only), source_snapshot_id,
material_sources and crm_target={location_id,contact_id} or null for mail-only.

New manifests use mime_type=text/plain, text_base64url (actual UTF-8 message),
text_sha256, plus original task/content_version/draft/message/thread/source IDs,
RFC parent Message-ID and scalar From/To/Cc/Bcc/Reply-To/subject headers.
reply_transport.prepare produces the exact text/plain update_draft payload.
Retain returned draft/message IDs and original write acknowledgement. No
review_ready, prepared_copy, render provenance, image or preview is required.

email.prepare returns SingleEmailReviewPrepared with email-review-v3 package.
email.review input={package} returns content, binding and task_records. Publish
content as the ordinary operator page. Save both task_records as JSON only on
the canonical task and set its actual ActionPageURL, version and route. Do not
paste the technical records into the action page, even collapsed. Keep all
choices blank until a real operator submission. No separate copy/preview page.
A successful task/action publication response confirms registration; no reread.

## email.accept

Input: task/action original Notion captures, task_id, action_id, current
operator_id and now with offset. The helper reads the bound email-review-v3
package from the canonical task (legacy v2 stays on its original route) and current submitted native choices, validates visible recipients,
window, subject/body and version once, and returns EmailDecisionAccepted with
record_type=email-decision-v2, decision, package and input_sha256. Persist that
record and stable AttemptId on the original task before dispatch. Do not clear
or manufacture choices to make an approval pass. Return requires useful comments.
Changed copy returns EmailRevisionRequired, not permission to send old bytes.

## email.dispatch

Use the same current input as accept, plus policy, actual sender_account,
accepted_input_sha256, stable attempt_id, original attempt_write={response,request},
optional original attempt_status, send_tool (actual installed Gmail send_draft),
and controls with explicit observed booleans: scan_enabled, channel_enabled,
no_reply_or_stop, attempt_clear, approval_current, date_allowed. These are derived
once from the current settings/task/source observations; a cached project file
cannot supply them. Missing/false controls defer only this dispatch. A native
cycle also retains its already validated current scan-control guard.

One imminent dispatch reuses acceptance captures; delayed/later-cycle work takes
one new original task/action/control observation. A consumed submission checkbox
is not withdrawal: the unchanged Approve can resume from its email-decision-v2
record on the original task. Changed comments/choice/version or a new Pause/Cancel
cannot reuse it. The helper emits the exact call={tool,args:{draft_id}} only
when policy/window/controls and saved attempt acknowledgement pass. Already
accepted/pending/unknown attempts never emit another call.

## email.complete

Input: exact package, original successful Gmail response, writes with
source/task/action entries={response,request}, optional followup_write (actual
cycle/registration Notion write), and crm_write (actual CRM Note response).
Provider handoff plus these original own-write acknowledgements are enough;
no fetch-after-write. Output records actual message/status, required/saved CRM
and SMS-registration states, pending_steps and retry_send_allowed=false.
A pending recording step recovers only itself; successful email is never sent
again. Material SMS registration is attempted independently of CRM failure.
No provider status/delivery polling is introduced.

## Existing HTML approvals

The adapter retains email-review-v2 and HTML transport solely to finish an
existing frozen approval without changing approved bytes. New inquiries use v3.
Do not call review.prepare, render_preview or publication_writes for plain text.
