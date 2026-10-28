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
- Upgrade an open task containing free text: preserve its page/run IDs, Mode and original OperatorInput; retain the supplied values in a tailored editable form. Add task-input-v1 only after saving the form. Do not treat migration as submission or execution.
- Fill half a templated Automatic task without submitting: the scan must wait. Submit incomplete data: record NeedsCorrection and each missing field, preserve answers, clear the checkbox and request resubmission. Optional style examples must not block a standard business style.
- Submit complete data: validate authorized source/version, preserve the exact accepted snapshot and resume only the unfinished step. A Manual task remains pending during run-auto even when submitted. An explicit owner-skill continuation can validate it.
- Withdraw or edit input during validation; stale data must not be consumed. Repeat a scan after successful application or interrupt after application: use recorded evidence to reconcile, without duplicate writes, new customer approval or sends.

These are behavioral acceptance cases to execute in the customer environment, not packaging-pass claims.

## Encoding, source identity and current-state regressions

- Read GB2312/GBK/GB18030 and UTF-8 mail, base64/quoted-printable and multipart alternatives. When native full text is corrupt, verify the exact raw source and strict decoder result. Native failure and recovery success remain separate. Malformed MIME, unknown charset, doubtful output or unauthorized raw attachments must suspend that item rather than invent readable facts.
- Fetch a source through a Notion view that renders mailto links/escaped colons. Exact typed/parameterized SourceKey lookup must reuse the original business record even after it moves out of Inbox. Multiple exact matches require reconciliation; a serial rerun is not a concurrency test.
- Return incomplete input, then resubmit it and advance v1 to v2. Verify one current status/version and exact review/preview links at the top, with obsolete correction notices in history. Accepted inputs, original decisions and completed action evidence remain unchanged. Completed data tasks remain reachable from the original run.
- Register an authorized dependency once, then verify a child inquiry reuses the applicable verified version and asks only for remaining facts. Unsubmitted Manual setup data and unrelated project versions must not be consumed.

For a command-coverage test, report init, add-communication, run-auto, reply-draft and report separately. Record actual invocation and per-step Passed/Failed/Waiting/Untested; a helper run, package check or three scan rounds do not prove all commands passed. Label simulated operator actions, live test-account observations and real approvals separately. This regression list does not itself grant test approval or authorize a send.

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

## Independent send-gate coverage

For changed version, expired approval, customer stop, incomplete latest-reply coverage and invocation restrictions, record each check's inputs and result separately. Use an offline decision rehearsal/fake provider to isolate one business blocker while others are satisfied, without changing real customer stop settings or granting real send permission. Test zero provider-adapter calls for each rejection and a counterfactual valid case reaching only the fake adapter. Mark this as simulated gate coverage, not live sending acceptance. A record with batchStop=true and CustomerSendAllowed=false proves combined suppression only; it does not prove an independent expiry/version gate or a real delivery path. Real valid sending/received HTML, SMS, scheduling, host visual and concurrency still require their own explicitly authorized tests.
