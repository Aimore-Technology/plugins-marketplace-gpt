# Joint 0.1.10 + 0.1.11 acceptance prompt

Copy the text below into the designated plugin-test session with the plugin selected. Install/reload 0.1.11; it includes 0.1.10. Do not claim that the older version itself was rerun.

```text
Use @EightDegrees Sales Workflow to test actual installed version 0.1.11, including the 0.1.10 dedicated action-page changes and 0.1.11 evidence/routing fixes. Execute here; do not edit plugin source or delegate workflow testing to another session.

Version and baseline
- Verify actual loaded manifest/Skills=0.1.11 and record hashes before mutations. Stop if stale.
- Use a new TEST BatchId. Preserve the existing customer Aimore tree, unrelated/dev pages, previous reports, CRM Notes and external attempts. This is an in-place upgrade test, not an empty-workspace claim.
- Capture current page/database/task IDs, pending states/approvals, customer-title overrides and CRM Notes baseline. Do not assume any previous count or reuse previous approvals for new fixtures.

Permitted test actions
- Upgrade only this customer workspace; create scoped TEST tasks/action pages, logs/reports and a new Dropbox test folder/files.
- Simulate operator answers, choices, submit checkboxes, Return/Confirm/Approve/Pause/Postpone/Cancel/receipt and explicit Manual continuation. Label every decision AI simulated operator review / test authorization, bound to actor/task/action/version and actual observation time. No claims of real human approval.
- At most three real seed emails from ori.lynn@outlook.com to iamzerolin@gmail.com, with TEST/BatchId/round subjects; authorize only these exact batch messages/time range and their batch labels. Reconcile before any retry; no blind resend or unrelated email/attachment access.
- Verify the 8Degree Test sandbox and existing TEST contact by actual authorized data. At most three approved standard combined TEST Notes may be appended/read back for distinct test communications; preserve every baseline Note and existing contact field.
- No business reply, SMS, notification, Calendar change, schedule activation, contact creation, deletion, unrelated Dropbox writes or automatic cleanup. A simulated Approve does not authorize sending. No deliberate redaction is required.

Run all five commands across three rounds: upgrade/setup, input/error handling, then recovery/deduplication/reporting. Record actual invocations; additional continuations are separate calls. Keep each shortcut's restrictions.

Round 1
1. @eightdegrees-sales-workflow init: explicitly upgrade the existing tree to 0.1.11. Register Actions plus required route fields. Preserve IDs, language, custom customer titles, old decisions and Pause states. Repair owner/step only from original source/run/payload evidence; ambiguous/in-flight legacy records remain pending on one original input authority. Upgrade itself performs no business action.
2. add-communication: create a new Manual test communication, exact-match the existing TEST contact, archive/link the original source, render/validate the standard plain-text Note and create its dedicated review action page. Stop before CRM writes.
3. run-auto: receive/read batch seed R1, route a new inquiry and create Automatic input/review tasks with correct owner/resume fields. Keep Manual forms untouched. Save source/progress before checkpoint; failed required checkpoint must not mark the scan Completed.
4. reply-draft: exercise missing project data and create/reuse the source-completion action page. Keep unsupported commercial facts unknown; no invented project claims.
5. report: update the registered original dated brief, and create this batch's separate test report. Link primary action pages and secondary technical tasks. No task/health/provider mutation from report-only.

Round 2: operator-facing input and exact decision scope
- Open all five categories' action pages. Ordinary pages must show only title properties, concise business context, relevant inputs/choices and the named submission checkbox before technical history. No user-entered TaskId, OwnerSkill, ResumeStep, DecisionVersion or ApproverId. Verify actual host UI when available; otherwise distinguish saved structure from visual acceptance.
- Half-fill Automatic data without submitting: wait. Submit incomplete data or zero/multiple choices: precise errors, retained answers/comments/selections, only unchanged submission reset. Resubmit complete source/version data: durable snapshot, apply/readback, then completion on the same canonical task.
- Submit the Manual Note review: run-auto must not consume it. Explicit add-communication continue <registered action URL> may validate its current decision, append once and read back exact approved Note. Return/revise/review a second version separately. Repeat continuation without duplicate Notes.
- Use actual Dropbox initial/conflicting/corrected TEST files and immutable IDs/revs/effective dates. Source conflict belongs to sales-reply/ResolveProjectSources, not communication Notes.
- ContentReview confirmation, SendApproval approval and reminder receipt must remain different. For an Automatic send task, run-auto may record a valid submitted choice in observe phase, but execute phase stays deferred and no real send occurs. reply-draft/report cannot consume send approval. Use a fresh batch task; do not clear old customer stop/Pause to manufacture this case.
- Edits create a new reviewed content version/action page with blank choices. Old/copied/superseded/closed page edits cannot approve or reopen current work. Preserve prior decisions/answers. Postpone/Pause requires explicit permitted owner continuation, not an arbitrary input edit.

Round 3: 0.1.11 regression checks and recovery
- Replay the preserved or synthetic MCP envelope with structured INVALID_ARGUMENT plus text upstream 403 WORKFLOW_API_NOT_ENABLED_FOR_LOCATION. Use packaged workflow_checks.py: preserve both layers, classify capability unavailable and do not retry token/scope/parameter changes. This offline replay is not a new live API call or proof fixture creation is safe. Existing contact/Notes health remains separately evidenced.
- On batch-only negative fixtures, verify wrong OwnerSkill, blank ResumeStep and wrong category cannot consume a form or dispatch business work. Preserve the fixture snapshot. An add-communication continuation targeting a sales-send task must defer, without a new Note or Mode change.
- Recover using persisted task/action/source records and explicitly verify routes: project data -> sales-reply/ResolveProjectSources; draft review -> sales-reply/ReviewReplyDraft; final reply approval -> sales-reply/SendApprovedReply; Notes -> communication/ReviewCommunication; checkpoint -> scanning/SaveMailCheckpoint. Parent Workflow may remain communication. Do not fill missing routes from conversational memory or restart the scanner recursively.
- Interrupt after accepted submission before projection/result saving, then reconcile only missing work. Preserve inputs and external IDs; a consumed unchecked submission plus accepted evidence is not revocation. Changed/withdrawn input before action rejects stale evidence. No duplicate CRM/send for a log or display repair.
- Scan saved Notion report/action/task pages in full with packaged notion-links: include script/Skill names, all tables, examples and history, not just project-file cells. Use code literals for file names/invalid URL examples and explicit verified URLs. A controlled bad-link fixture must be detected. Repair exact presentation and re-fetch before declaring the scoped issue resolved; remaining findings/truncation cannot produce global zero quality failures. Keep failed observations and original captures.
- Send/read seed R2 for correction/conflict and R3 for stop as needed within the three-mail cap. Keep batch stop and final SendApproval Pause. Verify same-source deduplication after a controlled original-page move and repeated scans. No real business send/SMS.
- Re-run all five commands for the final round within their policies. Verify one current brief, historical snapshots, consistent UTC/Adelaide timestamps, real LastAttempt/LastSuccess, quality/failure/recovery/synthetic separation and all baseline records preserved.

Evidence and reporting
- Write artifacts/plugin-test-<BatchId>/REPORT.md, machine coverage, invocation ledger, actual tool audit, baseline/final CRM comparison, route migration evidence, actual action-page submissions/snapshots, helper outputs and saved Notion link checks. Store authorized customer captures outside plugin repositories.
- Return Notion test report, original daily brief, current action/task links and all created resource IDs. Check report tables and actual saved targets. Preserve resources; no cleanup.
- Separate Passed/Failed/Waiting/Blocked/Untested and three groups: retained workflow behavior, 0.1.10 action-page behavior, 0.1.11 fixes. Count actual cases, not inherited totals.
- Package/unit/helper replay is not live workflow acceptance; ordinary-page structure is not host visual proof; route policy checks are not independent version/expiry/stop send-gate acceptance; serial deduplication is not concurrency. This test does not authorize actual business HTML/SMS sending or a new backend. Leave unexercised capabilities Untested with precise reasons.
```
