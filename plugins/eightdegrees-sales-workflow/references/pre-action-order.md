# Prospective review and dispatch gates

Run these only for the affected event/owner phase, never on an idle tick. These
offline helpers release exact supported arguments; they do not intercept MCP
or prove historical execution order. Existing authority/approval guards remain.

## Open email review only after saved-copy agreement

Create an inert action with its actual action-binding and no decision/submission
to-dos. Save the copy, native preview and current stored Gmail draft first.
Use local review.prepare with transport (reply_transport verify input), original
copy_page and preview={kind:html|image,input:original preview check input}.

The saved copy contains one email-review-copy-v1 JSON record with task_page_id,
content_version and html_sha256, plus unique H2 sections Email subject and Email
HTML. Subject is exact plain text; HTML is an exact fenced html block. Include
the frozen file's trailing newline INSIDE the fence, plus the fence's own
separator newline; no trimming/normalizing bytes. Localized headings may be
supplied explicitly as subject_heading/html_heading. The helper checks original
saved copy bytes against the actual raw draft and saved native preview bytes.

Then pass the SAME original evidence as review_release to notion.mutation for
the proposed activation write. Its guard requires EmailReviewReady and matching
TaskPageId/ActionPageId/ContentVersion/DraftBindingSha256 before returning call.
Never create active email controls in the first page creation, activate before
checking, or reuse verification for a changed copy/version. Existing human
checkbox submissions and clearing/closing existing controls need no repeat
activation. A new version/binding needs fresh release. Missing prerequisites
leave inert recovery copy; they do not ask for approval of unverified content.

## Admit before emitting outgoing calls

Before Gmail send_draft or AndroidSync request_sms, use local dispatch.admit.
Inputs: original scan.cycle input as scan (including actual policy), work_key,
task_page_id, run_page_id, channel=email|sms and exact proposed call={tool,args}.
email supplies transport (current unsent raw draft verification input). sms
supplies notification (sms.verify input with actual saved task/current policy).
Only the one currently selected matching send step/version is eligible.

The result contains dispatch-admission-v1, with no executable call. Persist it
on that actual phase run and fetch the original saved run. Each phase run has
one current admission; preserve previous attempts/versions as immutable history
on their original runs/logs, not competing current admission records.

Then use dispatch.prepare with the same input, saved_run, actual now and
current_scan. The current scan observation must retain the same invocation,
start, policy and exact selected work; reobserve ownership, stop, time and queue.
An already recorded in-flight reservation is not another completed owner step;
do not add its key to attempted_keys until finishing or saving its unknown result.
Admission expires after 120 seconds or sooner if budget/ownership/stop changes.
Expired admission requires prospective fresh admission, never a backdated log.
Only DispatchArgumentsPrepared emits the exact unchanged call and digest.

Separately retain actual current approval/standing authority, original task/
action, stop/reply coverage, window/count/channel/schedule and prior-attempt
checks immediately before invoking it. Queue admission is not an approval.
After a successful original acknowledgement, finish our own results and CRM
readback without querying external send/delivery status. Unknown blocks replay.

Changed SMS text, version, recipient, device or key needs a fresh frozen payload
and its own saved admission. A connector rejection does not authorize bypassing
the new admission. This connector's conservative checks enforce body <=70
characters and key matching [A-Za-z0-9_-]{8,100} before emitting arguments;
these are AndroidSync observations, not general SMS standards.

Keep full captures locally once and use local_checks --output for small console
results. Do not implement these checks as repeated model comparison or run
them after the dependent action. Live forward execution still needs testing;
offline regression cannot certify that a host/model never bypasses a helper.
