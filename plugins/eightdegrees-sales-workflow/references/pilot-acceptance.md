# Pilot acceptance and first test sequence

Package validation proves file/schema/reference integrity, not CRM access, mailbox scope, HTML rendering or actual sending. Record Passed/Failed/Untested plus run/log/provider evidence per case. Use authorized real data without deliberate redaction; do not store customer samples/results in this repository.

1. Initialize the customer's accounts and clean Aimore tree with pilot-v1/schema 2. Use any designated test operator with actual authorized accounts; unset operator fields require setup, not a name fallback. Use real allowed labels, work-folder IDs, verified CRM LocationId and explicit test recipients; missing values remain disabled/waiting, never fabricated.
2. Test 3-5 authorized emails/records: scoped listing/body access, matching, customer/stakeholder separation, four-section Notes, draft and Notion preview. Mixed-label thread limitations must not broaden reads. Gmail attachments remain unopened by default.
3. Without a scheduler, complete manual P0-A: submit, match, review exact note/persona changes, explicitly continue, append ONE combined CRM note, read back and sync Notion. Repeated continue only fills unfinished steps. A saved manual task must not resume from a scan.
4. With operator-approved content/window, test a normal Gmail message to a designated test recipient. Verify actual received content, HTML/assets and reply visibility. Edited content/recipient/file or expired window invalidates approval. Note confirmation and reminder acknowledgement must never send a customer message.
5. Test material -> SMS -> email response with the operator present. Before gateway acceptance, the operator sends SMS manually and logs it; automatic SMS remains disabled. Verify actual first +30-minute and second +24-hour timing, allowed-window rollover, weekend/no-send date rules, manual+AI two-message cap and non-reset after resending materials.
6. Verify reply/stop first, do-not-contact, the operator's manual pause for unconnected channels, one active cycle and handover after two. Unknown results/counts block later attempts. Own-number display and replies in the operator's original inbox are mandatory for automatic SMS acceptance.
7. Test reminders on actual connected channels: one initial, 19-minute escalation, 24-hour acknowledgement/overdue. Single-channel or late checks are marked degraded, not passed. Acknowledgement closes only the reminder. Check scan reruns do not duplicate notices.
8. Create one confirmed work Calendar appointment; store/reuse its event ID. Do not access unrelated family events or duplicate existing Hub/Hux reminders. Test daily 08:30 timezone/DST configuration and one catch-up after a missed run.
9. Interrupt after an external action but before Notion result saving. Reconcile the actual external ID/result before retry/backfill. Test unknown send, changed approval, duplicate scan, partial pagination, Notion outage and two-host ownership conflict. No blind resend or duplicate CRM note; incomplete coverage remains visible.
10. Expand to 5-10 real inquiry cases. Review failures with the operator, iterate 1-2 rounds, then decide which verified capabilities to use more broadly. Log links and handover instructions stay in customer Notion.

Not part of this pilot: automated deletion/archiving, sensitive-original processing, customer-facing Portal/backend, independent stakeholder sends, unverified extra channels, business conversion/reply-rate dashboards. Production preferences may later replace pilot defaults without pretending they were already interview-confirmed.

## Operator portability and upgrade checks

- In a fresh installation, configure a chosen operator and separately authorized test Gmail/Notion/Dropbox accounts. Verify the configured display name, notification destination, manual-continue owner and approval identity. Never default a missing operator to a named person.
- Distinguish the scanned mailbox, customer sender and internal reminder email; do not send reminders to a test customer because those roles share a name. Unverified operator SMS remains disabled.
- Upgrade a legacy installation while paused. Preserve task/database IDs, supplied operator identity and historical actors; map old input/status fields without duplicating records. Conflicting old/new values require review.
- Switch to another configured operator or sender account. Pending unsent approvals must not transfer; reconcile unknown external attempts before new approval/resume. Check read-only diagnosis remains possible while required operator setup is missing.

These are required live scenarios, not claims that packaging has executed customer-account tests.

## Input forms and language checks

- Fresh init asks Chinese/English once and persists the explicit choice. A later init reuses it. Verify both language branches produce localized task guidance while schema keys, customer language and exact approved payloads remain unchanged.
- Upgrade an eligible open task containing free text: preserve its page/run IDs, Mode and original OperatorInput; retain supplied values in the ordinary action-page form. Register its binding before enabling task-input-v2. Unresolved in-flight legacy records keep their original input route until reconciled. Migration supplies no new submission, decision or execution.
- Fill half a templated Automatic task without submitting: the scan must wait. Submit incomplete data: record NeedsCorrection and each missing field, preserve answers, clear only the unchanged submission to-do (v2) or legacy InputSubmitted property (v1), and request resubmission. Optional style examples must not block a standard business style.
- Submit complete data: validate authorized source/version, preserve the exact accepted snapshot and resume only the unfinished step. A Manual task remains pending during run-auto even when submitted. An explicit owner-skill continuation can validate it.
- Withdraw or edit input during validation; stale data must not be consumed. Repeat a scan after successful application or interrupt after application: use recorded evidence to reconcile, without duplicate writes, new customer approval or sends.

These are behavioral acceptance cases to execute in the customer environment, not packaging-pass claims.

## Dedicated action-page regression scope (0.1.10)

- Fresh init creates an ordinary Actions hub. For each of the five task categories, open the registered ordinary action page: only title properties, a short business summary, relevant answers/choices and a named submission to-do appear before technical history. The operator does not fill TaskId, DecisionVersion, ApproverId or State. Verify actual host presentation and direct primary links, not just Markdown structure. Native card/title clicks may still open the database record; the action link must work without a property-panel detour.
- Half-fill an action page without checking submission: no consumption. Select zero/multiple exclusive choices or omit required data: NeedsCorrection, exact field errors, all answers/choices retained, only the unchanged submission flag reset. Supply valid data: original task receives a durable bound snapshot before application; Completed follows actual application/readback, not the checked to-do.
- Submit ContentReview and separately SendApproval; verify localized intent-to-decision mapping and automatic version/actor recording. Content confirmation and reminder receipt cannot approve a send. Manual action forms stay untouched by run-auto, even when submitted; explicit owner continuation accepts the registered action URL and returns to its original task.
- Change content/version after approval: a new active review page has blank choices; the old page becomes superseded. A copied page, old checked decision, direct legacy Decision edit on a migrated task, or a completed/cancelled page edit cannot approve/reopen current work.
- Withdraw/change input between observation and action; reject stale snapshots. Interrupt after durable acceptance but before projection/checkbox/result saving: reconcile and repair the original records without duplicate CRM/send or demanding unchanged answers again. Consumed unchecked submission plus preserved accepted evidence is distinguishable from withdrawal.
- Explicit upgrade migrates eligible open tasks in place, preserves answers/IDs/Mode/decisions and never manufactures a new submission. Unresolved in-flight legacy tasks remain clearly labeled on one original route until reconciled. Do not delete old properties or create closed-task forms.
- Verify preview unavailable, expired approval, inaccessible action page, no active tasks and already cancelled cases each have a business explanation/next step rather than a live misleading form. A report-only invocation links forms but neither creates them nor consumes input. Package/CLI tests do not establish this live Notion UX or workflow coverage.

## Encoding, source identity and current-state regressions

- Read GB2312/GBK/GB18030 and UTF-8 mail, base64/quoted-printable and multipart alternatives. When native full text is corrupt, verify the exact raw source and strict decoder result. Native failure and recovery success remain separate. Malformed MIME, unknown charset, doubtful output or unauthorized raw attachments must suspend that item rather than invent readable facts.
- Fetch a source through a Notion view that renders mailto links/escaped colons. Exact typed/parameterized SourceKey lookup must reuse the original business record even after it moves out of Inbox. Multiple exact matches require reconciliation; a serial rerun is not a concurrency test.
- Return incomplete input, then resubmit it and advance v1 to v2. Verify one current status/version and exact review/preview links at the top, with obsolete correction notices in history. Accepted inputs, original decisions and completed action evidence remain unchanged. Completed data tasks remain reachable from the original run.
- Register an authorized dependency once, then verify a child inquiry reuses the applicable verified version and asks only for remaining facts. Unsubmitted Manual setup data and unrelated project versions must not be consumed.

For a command-coverage test, report init, add-communication, run-auto, reply-draft and report separately. Record actual invocation and per-step Passed/Failed/Waiting/Untested; a helper run, package check or three scan rounds do not prove all commands passed. Label simulated operator actions, live test-account observations and real approvals separately. This regression list does not itself grant test approval or authorize a send.

## Customer navigation and title migration

- Create/reuse a verified customer with a human-readable CRM name under Clients; full LocationId/ContactId remain in metadata and exact page registration. Matching and reruns still use those IDs, not the title.
- Use two distinct contacts with the same name: show verified email/phone disambiguation while retaining separate mappings. A shared name/email across locations must not merge records.
- Explicitly upgrade an ID-titled legacy customer page: rename that original page only, retaining its page/child IDs, Communications links, tasks and approvals. A later CRM name change may refresh a generated title, but an operator-customized title must remain intact. Verify no CRM write or historical approved-Notes rewrite occurs.
- With missing name or unavailable CRM verification, use the documented display fallback or keep migration pending. Do not invent identity, create a duplicate client tree or block unrelated verified work for a cosmetic field.

## Notion consistency and report regressions

Before verifying a release fix, record the actual loaded manifest/skill version and the expected target. A run using an older cached version is baseline evidence, not acceptance of the new release; update/reload before claiming the fix passed. Preserve the original tested-version label.

- Update a version-bound decision, then simulate a stale candidate query. Fetch the original task/content before action: do not reject valid saved evidence, consume an outdated version, invent approval or create another task.
- Reject an OperatorInput property request. The dependent workflow must stop, reread the original submission flag and retain body input. Retry only the corrected plain summary/body representation; do not treat intended input as saved.
- Limit SQL during a report/scan. Stop repeated restricted queries, disclose the limit and use supported complete saved-view pagination or known original page IDs. Known-item results cannot establish a global count or absence of duplicates; no new daily brief is created while the registered original exists.
- Verify the original source's customer Communications move/link before ContentReview, preserving ID and mapping. A link failure remains a pending archival step.
- Run report three times: one latest current summary at the top, explicit cutoff/coverage and older snapshots in history. Literal paths remain literal; Markdown tables and actual source links remain readable. Local evidence paths are not fabricated web URLs.

## Standard Notes and 0.1.8 regression scope

- Init creates/reuses `Templates/CRMNotes`, registers aimore-crm-note-v1 and preserves existing Notes/approvals. An explicit upgrade adds missing template/monitoring schema without executing business tasks.
- Test a manual communication and a separate automatic email with all headers and four plain-text sections. An unknown original time is explicitly Not provided; a known email time uses the actual source instant in the stated timezone. Include supported persona proposals before review. Missing headers, empty sections and Markdown/HTML must fail before ContentReview, not merely after CRM append.
- An incomplete legacy approved payload cannot be silently patched. Produce a corrected new version and obtain its own decision. Downstream persona-update appends the exact complete approved text, without actor banners or extra sections. Compare actual CRM body to the approved digest; repeat continue and recover a log-only failure without duplicating the append. A provider-success quality defect stays visible separately.
- Exercise ordinary text success, null structuredContent, explicit tool rejection and unknown provider result separately. A local JSON parsing exception after successful sending must not trigger resend. Observe an exact provider-ID/quoted-subject reconciliation before treating a missing broad search result as absence. Do not claim these live paths passed from helper tests.
- Simulate retryable read rate limiting without exhausting a shared quota: at most one bounded read retry, partial coverage and same-source continuation. Distinguish this simulated adapter behavior from live provider limits. A permission denial never enters that retry path. Scan/command boundaries remain unchanged.
- Compare report GeneratedAt/DataCutoff properties with current body timestamps in UTC and the configured timezone, respecting documented property precision. Later service operations advance LastAttempt/LastSuccess appropriately; report-only reads do not create a new provider success. Inspect saved Notion file-name links, not just the local report. Keep quality, unresolved failures, unknown attempts, recovered history and synthetic cases separately labeled; never hide a Notes defect behind zero provider-write errors.

## 0.1.11 evidence and owner-routing regressions

- Replay the preserved GHL MCP shape with structured INVALID_ARGUMENT plus text upstream 403 WORKFLOW_API_NOT_ENABLED_FOR_LOCATION: preserve both layers, classify location capability absence, do not retry params/tokens/scopes and do not infer fixture creation is safe. Verify successful contact/Notes capability remains separate. Ordinary text success, null structuredContent and nested Gmail rate limits retain their own classifications. Offline replay is not a new live provider test.
- Write a report containing code-formatted script/Skill names, project files, invalid-URL examples and explicit verified links; inspect the whole actual fetched page. Include a controlled suspicious-link fixture outside approved business payloads and verify the helper flags it. Repair only exact presentation, then re-read all declared pages/sections before closing the quality issue. Neither three repaired cells nor local Markdown validation establishes page-wide zero issues. Static checks are not network/host visual acceptance.
- Create Notes, sales-source, reply-review/send and checkpoint tasks with explicit owner/step/contract. Reject wrong owner, blank step and category mismatch before input consumption or business dispatch. A parent Workflow=communication with OwnerSkill=sales-reply is valid provenance, not a fallback executor.
- Resume from original persisted task/action records: source completion returns to sales-reply/ResolveProjectSources, reply approval to sales-reply/SendApprovedReply, Notes to communication/ReviewCommunication and checkpoint to scanner/SaveMailCheckpoint. Keep original IDs, completed attempts and invocation restrictions. An add-communication continuation of a send task must defer, without Notes or Mode changes. A checkpoint recovery executes inline, not another scanner recursion.
- Combine 0.1.10 action-page input with route checks. run-auto observe phase may validate/record an Automatic send choice while execute stays deferred; report-only/draft-only cannot consume that send choice. Manual forms remain excluded in both phases. Old/copied action pages, changed binding and incomplete routes cannot approve current work. Owner eligibility is not approval/window/stop validation or sending acceptance.
- Explicit upgrade repairs only unambiguous eligible legacy metadata using source/run/payload evidence, preserving historical Workflow, input, approvals, Pause and record IDs. Ambiguity remains a setup/route issue; no guesses or new customer sends. A failed checkpoint cannot prematurely complete its scan; later recovery preserves original Error history.

## Independent send-gate coverage

For changed version, expired approval, customer stop, incomplete latest-reply coverage and invocation restrictions, record each check's inputs and result separately. Use an offline decision rehearsal/fake provider to isolate one business blocker while others are satisfied, without changing real customer stop settings or granting real send permission. Test zero provider-adapter calls for each rejection and a counterfactual valid case reaching only the fake adapter. Mark this as simulated gate coverage, not live sending acceptance. A record with batchStop=true and CustomerSendAllowed=false proves combined suppression only; it does not prove an independent expiry/version gate or a real delivery path. Real valid sending/received HTML, SMS, scheduling, host visual and concurrency still require their own explicitly authorized tests.

## 0.1.12 publication regressions

Test owners through intake, accepted/rejected input, Return/new version, Pause and completion. In the same invocation verify canonical task, action status and the one current entry agree (native Today links in verified linked-view mode, otherwise the legacy hub link), without another init/report doing repairs. Data-only forms contain no irrelevant choose-one prompt. Keep old children/answers but clearly label historical links/headings; no second current queue. Simulate a display-write refusal only in a controlled fixture or captured-result replay; a recovered projection must not repeat CRM or sending.

Before any actionable HTML review, verify an actual saved native preview block/source, exact downloaded file bytes and copy agreement. Raw upload URI/file/code/external screenshot alone fails the prerequisite. Repair by an explicit draft-owner invocation and fresh review version; old invalid approvals remain history and stop/Pause remains. Distinguish saved-block proof from authenticated Notion host visual and real customer receipt.

During report, compare every actual mutation against frozen report/run/log targets. Report a known bad preview or stale task without changing it, invoking its owner, consuming input or updating Health/navigation. Replaying the prior report43 calls must return Deferred; a fresh report has its own evidence scope. Preflight bare URL targets before publication and inspect saved full output after repair. These checks remain Skill execution obligations, not independent host-enforced guards.

## 0.1.13 completion and channel acceptance

Replay the actual invalid source enum and native-mention whole-section plan offline: both must refuse before mutation. Exclude database/view schema descriptions from typed page coverage, and block completion on failed/nonzero/missing/duplicate/stale/wrong-target results. Before final report Completed/Success, all registered report pages need current successful checks. A top Pause with Not submitted or a choose-one prompt in another current section fails task-display. Retain original answers/history and provider IDs on repair.

Only on the operator's explicit real-channel test request, use separate owner-workflow invocations for an exact approved HTML reply and one AndroidSync SMS. Record actual recipients/device, immutable payload, AttemptId and one-message timing exception; waive only the requested hours/delay. Verify actual received mail/thread/MIME and SMS state/inbound evidence when available. An unobserved phone reply stays Waiting/Untested; simulation is not receipt. Shortcuts retain no-send policies, old stopped batches remain stopped and automatic enrollment stays disabled. A standalone channel probe does not establish material-follow-up acceptance.

## 0.1.16 scheduling and realistic-business regression

- Save finance not confirmed as null before any projection; false with an unknown
  status must be rejected. Explicit sourced yes/no and unrelated control flags
  retain their different meanings. Existing approved content is never silently
  rewritten to satisfy a new guard.
- New form registration uses the actual policy/PageId in register phase; it
  supplies neither Manual continuation nor completion evidence. Execute checks
  still enforce explicit continuation and owner scope.
- Notes headers stay machine-readable; body uses business actions and future
  customer follow-up. Execute terms are caught before review, without altering
  approved bytes or suppressing source quotations.
- On a connected native scheduler: start once, verify one actual active task,
  exact 15 minutes, real ID, prompt and timezone. Repeat start must reuse it.
  Missing native support, unknown create result, duplicate ownership and another
  host's owner block creation; they must not produce a second scanner.
- Trigger a real scheduled tick, verifying original scope and Automatic-only,
  manual no-send behavior and native guarded approved-work execution separately. Repeat no-change ticks stay quiet. A busy
  run must not launch a parallel catch-up. Measure actual wall time/call count.
- stop must delete the exact owned native task, verify absence including paused
  records and preserve unrelated schedules/business records. Repeat stop is a
  verified no-op. A paused task, missing delete API or unknown result is not
  Stopped. A stale queued tick must defer; manual run-auto remains usable.
- Native schedule support, UI confirmation/deletion, live concurrency and actual
  runtime speed remain untested until observed in that host. Source/package
  checks and mocked normalized scheduler fixtures are not live acceptance.

## 0.1.17 alignment acceptance

- In a real Work GPT task, verify native 15-minute creation/readback, same-ID
  reuse, current lifecycle/connector access and deletion. Claude targets native
  Cowork cron but remains explicitly untested until its environment is available.
  Do not substitute a Codex project-local task for the requested Work runtime.
- Manual run-auto still defers customer sends. A real current native tick may
  reach only valid approved Automatic owner steps. Test no guard, stale/stop,
  wrong operator/runtime, competing run, Manual input and legacy no-send job
  upgrade: none may dispatch customer work. A policy name alone is insufficient.
- Verify an actual sent email's deterministic GHL receipt and current task/index/
  action projections. Interrupt after send and after receipt append: reconcile
  existing IDs, backfill only unfinished result work, never send/append again.
  Changed actual message/customer/payload or unknown receipt append blocks reuse.
- Force candidate/original state conflict and quota failure in a controlled
  rehearsal. Do not reopen Completed, infer no pending work or silently publish
  complete counts. Test permitted view/original-page fallback and its coverage.
- Observe daily 08:30 or labeled catch-up, exactly one configured summary notice,
  reminder receipt/escalation/overdue phases, confirmed event-ID reuse and busy
  tick behavior. These are live tests still required, not passed by packaging.
- Recheck real image/attachment EDM, edit invalidation, two-message SMS timing/
  inbound stop and actual operator usage in a later authorized acceptance round.
