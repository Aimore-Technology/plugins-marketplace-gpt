# Inquiry email flow

This is the normal email entry for email-scanning and sales-reply. Read only
this procedure, current scheduled entry when native, and a specific failed
helper's reference. Do not traverse every historical owner/check document.

## One pass to one review

1. Discover authorized new mail plus saved unfinished events and new Notion
   submissions. Read each new message body once. Reuse its immutable message ID,
   source key and original capture across helpers. Classify inquiry mail and add
   AimoreInquiry; that label is output, never a prerequisite or expanded scope.
   Save/reuse one original Inbox source. A successful source-write response/ID
   permits preparation immediately; no extra saved-plan/checkpoint fetch.
2. Search the configured CRM location once by exact sender email/phone; reuse that match for the same sender/location within this cycle. A unique
   match supplies its name. Otherwise use the current signature, then From
   display name, then Dear Customer and a name question after answering. Store
   that display name automatically; no name-confirmation form. A different
   signature is not an identity conflict. No-match/ambiguous CRM can remain
   mail-only for this inquiry; do not guess a ContactId, create a contact or
   block draft preparation. Unresolved CRM recording is its own scoped issue.
3. Extract project and exact lot once. Reuse the registered project catalog;
   project.cache-match resolves exact names/aliases and lot. A unique match
   leads to project.cache-get. A miss, expiry, manual refresh or observed revision
   change fetches only the affected authorized files once and stores their text,
   parsed facts, versions and source references with project.cache-put. A hit
   needs no Dropbox traversal, source fetch or repeated extraction. Do not
   confuse Maple Grove Lot 58 with Lot 96. Unknown/ambiguous project or missing
   required material opens one tailored DataCompletion page, not guessed facts.
   An operator may accept a narrower factual reply when a source remains absent.
4. Draft from the current cache snapshot and actual inquiry. Unknown parking,
   costs or dates stay unknown. Preserve conditions; no quotations, reservations,
   signatures, payments, appointments or guaranteed delivery. Use the configured
   sender/signature and cached project style. Do not fetch a persona/Notes
   history unless personalization actually needs it. No automatic factual CRM
   persona update or pre-draft communication review is required by an inquiry.
5. Prepare one Gmail reply draft. Replace its complete HTML once if needed to
   avoid automatic quoted text; use the original write response/IDs as the
   result. Render the same local package once and publish a usable native
   preview. No raw MIME download, saved-byte/hash comparison or preview download.
   Keep one canonical task, one operator action page and one reusable source;
   do not create separate content-review and send-approval tasks for new mail.
6. Use email.prepare, then email.review to create the combined email-review-v2
   page. It displays exact From/To/Cc/Bcc, subject, body, preview, materials and
   date/time window. One choice, Approve this draft and send in the stated
   window, approves both content and sending. Return, Pause and Cancel are
   alternatives; one named submission requests processing. Category=SendApproval,
   OwnerSkill=eightdegrees-sales-reply, ResumeStep=SendApprovedReply, Mode=Automatic.
   reply-draft stops after preparing this page; it never sends in that command.

## One submitted decision to dispatch

7. Read the original task and its active action page once on a new submission.
   Run email.accept on those same captures. Editing recipient/window/body or
   returning useful comments creates a new draft/version with blank choices;
   do not approve a changed payload with the old decision. An actual Approve is
   recorded with that exact package and stable AttemptId on the original task.
   Confirm this write by its API response/ID, without fetching the result.
8. Use email.dispatch once with that current observation, the accepted input
   digest, original attempt-write response, actual policy and current scoped
   controls: scan enabled, channel enabled, no relevant reply/stop, approval
   current, allowed date and attempt clear. Window and accepted/pending/unknown attempts are
   checked in code. There is no separate native admission record, second review,
   full owner-plan cycle, global executor proof or repeated CRM/file lookup.
   Refresh only if an intervening change or delayed/later-cycle send needs it.
   Send exactly send_draft(draft_id); never regenerate approved content.
9. Successful original Gmail acknowledgement finishes email dispatch. Record
   source/task/action results together at the boundary using original responses
   and email.complete. Append/reuse the deterministic CRM send-result Note when
   a real target exists, using send-receipt-v2. API success plus NoteId finishes
   that write. CRM failure does not replay email or suppress SMS registration.
10. Immediately register the material notification/cycle or reuse its original
    registration. Generate the factual SMS under standing notification authority
    and dispatch when due within current channel/stop/time/count/attempt limits.
    No human SMS review or extra command. Keep original accepted/unknown attempts
    and context-scoped stop rules; one customer's history cannot block others.
    API acknowledgements confirm cycle/notification persistence; no seven-page
    projection audit. A missing number/channel is one scoped recovery item.

## Read and write budget

A warm inquiry needs one message read, one scoped CRM match and zero Dropbox
content reads, followed by draft/preview publication and one review page. Scope,
IDs, schemas, templates and source captures are reused. Use [helper input contracts](email-helper-inputs.md) rather than reading Python source. Run local_checks with
--output and print only summaries, not every raw body or Python source. Log
observable actions and compact cycle metrics, not every thought/helper call.
No new input, submitted decision, due work or runnable recovery means immediate
idle exit. Existing backlog continues even with no newly discovered email.

New normal mail uses email.prepare/review/accept/dispatch/complete, not the
older multi-owner execution.prepare/ready/dispatch.admit chain. Those helpers
remain for explicit legacy/other workflow repair only; they do not add work to
this path. Deprecated saved crm_write_readback_required or two-review flags cannot restore old verification/approval stages. A restart uses saved original source/task/attempt pointers once,
never replays each missed interval. Installation creates no task or approval.

Existing content-only Confirm decisions stay content-only. Existing genuine
send approvals retain their exact original scope. For an unfinished old content
review, retain its history and offer one combined sending decision; do not turn
Confirm into Approve or repeat an already accepted email/SMS/CRM action.
