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
