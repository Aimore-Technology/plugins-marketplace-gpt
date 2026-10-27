---
name: eightdegrees-initialization
description: "Initialize or inspect the EightDegrees sales workflow in the customer's Notion and authorized accounts; configure pilot defaults, connections and readiness."
---

# Initialize EightDegrees

Read [operating-contract](../../references/operating-contract.md), [notion-model](../../references/notion-model.md) and [platform-runtime](../../references/platform-runtime.md). Load [pilot defaults](../../references/pilot-defaults.json) for the initial configuration, not on every later skill call.

1. Check the customer's own authenticated Notion, Gmail, Dropbox, CRM and optional SMS/Calendar tools. Verify the actual CRM and LocationId before any writes; do not request passwords/tokens in Notion. Record missing capabilities per stage rather than blocking independent P0-A tests.
2. Register authorized Dropbox work folders, project versions and John as maintainer. Keep all old versions; no moving, archiving, cleanup, overwrite, migration or SSD backup takeover. Resolve unclear current versions with John.
3. Create/reuse the clean `Aimore/` tree and database IDs from notion-model. Create ONE PendingTasks database with five filtered views. Add RunSettings to Dashboard; do not install the developer document hierarchy. Record partial setup honestly if view/file tools are missing.
4. Set up the four-section Notes template and approved ClientPersona template. Map existing Notes/activity-log capabilities; do not create custom CRM fields. Existing contact data needs no new factual approval just to read it; proposed new notes/persona changes do. Use provided examples to tune the template, not as a prerequisite to having a template.
5. Register actual Gmail allowed labels, exclusions, time range, sender/signature and separately authorized internal-reminder scope. Missing labels never imply all-mail access. Use existing templates and 3-5 authorized real sent samples for writing style; do not fabricate samples or require redaction. Attachments default unopened.
6. Create/reuse `AimoreScanned` only as a saved-progress checkpoint, not as an allowed-read label. Persist source and progress before applying it. Do not auto-label unrelated mail into scope.
7. Register John's own SMS number and original reply inbox expectations. Keep automatic SMS disabled until gateway stability, own-number display and visible two-way replies pass. Verify Calendar access only for confirmed work appointments. Leave Hub/Hux and untested extra channels disabled; avoid duplicate existing reminders.
8. Save `pilot-v1` actual settings: Adelaide timezone, daily 08:30 brief, weekday 10:00-17:00 sends, two-SMS limit and reminder rules. Use platform-runtime to prepare supported scheduled jobs only when requested/enabled in the host. Verify actual cadence; 15 minutes and 19-minute escalation are targets, not assumed features. Manual P0-A stays manual.
9. Run the staged checks in [pilot acceptance](../../references/pilot-acceptance.md) with authorized real data. Do not send customer messages without their specific approval. Record Passed/Failed/Untested per capability, not a blanket green status.
10. Return root, settings, task and health links; configuration version; actual connection/cadence results; and readiness by stage: ReadyForTest, WaitingForConnectionOrData, or Failed. Recommend the next independent test. Defaults adopted does not mean installation, real sending or customer acceptance passed.
