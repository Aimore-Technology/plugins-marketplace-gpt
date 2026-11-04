# Short email helper inputs

All operations run through local_checks.py with named original captures and
--output. They call no connectors. Capture original tool results once; do not
paste their full bodies or Python implementations back into model context.
Use actual IDs from responses, not the documentation placeholders below.

## email.prepare

Input: transport={manifest,write_result:{response,request}}, review_ready
(the actual review.prepare output from prepared_copy/publication_writes),
root_id, source_page_id, source_key, source_write={response,request},
action_page_id, operator_id, window={not_before,not_after,timezone}, optional
language=en|zh-CN, material=true for project material replies (false for an
acknowledgement-only reply), source_snapshot_id (cache snapshot), material_sources (the actual
file IDs/paths/versions used by the package), and crm_target with actual
location_id/contact_id or null for mail-only. manifest is the existing scalar
reply_transport contract, including current draft/message/thread/source IDs,
sender/recipient/subject, html_base64url and html_sha256. Retain the actual
Gmail update response message mapping before freezing the review package.

Prepare returns SingleEmailReviewPrepared with package and one human decision.
email.review input={package} returns content and action binding. Use those exact
values on the active action page after its inert creation returns its actual ID;
preserve existing native preview blocks. The form is inert until the matching
local copy/preview and original API acknowledgements pass review.prepare.
No new content-only task or separate content-approval pointer is needed.

## email.accept

Input: task/action original Notion captures, task_id, action_id, current
operator_id and now with offset. The helper reads the bound email-review-v2
package and current submitted native choices, validates visible recipients,
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
