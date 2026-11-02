# EightDegrees Sales Workflow

Version 0.1.35. Eight workflow skills plus one command entry for the EightDegrees pilot. Start with `eightdegrees-initialization`; shared rules live in `references/operating-contract.md`. Actual customer settings belong in `Aimore/Dashboard`, not in this installation directory. Open `Aimore/Today` for the current work; dedicated input pages stay under Actions. See [operator experience](references/operator-experience.md) for setup, short reviews and honest post-submit guidance.

## Skills

| Skill | Use |
| --- | --- |
| eightdegrees-sales-workflow | Route the seven short commands to existing workflows. |
| eightdegrees-automation-control | Start/reuse or delete one native 30-minute (20-minute optional) approved-work task. |
| eightdegrees-initialization | Set up customer Notion, actual connections, defaults and readiness. |
| eightdegrees-email-scanning | One scoped scan and automatic-task validation cycle. |
| eightdegrees-communication-context-process | Manual P0-A; reviewed communication to CRM Notes. |
| eightdegrees-client-persona-update | Approved downstream persona changes and one combined note. |
| eightdegrees-sms-follow-up | Verified material-send follow-up, at most two messages per cycle. |
| eightdegrees-sales-reply | Source-backed, previewed and explicitly approved HTML replies. |
| eightdegrees-daily-brief-and-handover | Daily actions, important reminders, confirmed appointments and handover. |

Read `references/platform-runtime.md` for this platform's capabilities. Cross-skill calls use packaged relative paths; no development Notion page is required at runtime. No Portal or independent backend is included.

## Pilot defaults

Australia/Adelaide; customer sends Mon-Fri 10:00-17:00; daily brief 08:30 including weekends; first SMS no earlier than materials +30 minutes and second no earlier than first actual SMS +24 hours. Manual+AI follow-ups total at most two. Four-section Notes append to the existing CRM. Files remain read-only and all versions are retained. Reminder targets are 19 minutes and 24 hours, subject to actual host/channel validation. Automatic deletion, sensitive-original processing and unverified channels are disabled. No deliberate redaction or sanitized-sample prerequisite.

## First use

Install the package, run initialization in the customer account, supply actual scope/account references, then follow `references/pilot-acceptance.md`. Missing connectors do not appear by installing skills. Customer emails require exact-version/window approval; factual SMS uses the configured standing notification authority. Package checks do not prove channel readiness or business acceptance.

Operator identity is configured at initialization; names, reminder destinations and approval ownership are not fixed. Dropbox remains the project-material source. See [operator setup and upgrade](references/operator-setup.md).

## Short commands

Use `@eightdegrees-sales-workflow init`, `start`, `stop`, `add-communication`, `run-auto`, `report`, or `reply-draft` with the plugin enabled/selected. See [command quickstart](references/commands.md) for inputs, boundaries and native Claude equivalents.

## Missing-data input

Open `Aimore/Actions` for ordinary task-specific input/review pages without the PendingTasks technical-property panel. Fill only requested information or choose one applicable decision, then check the named submission to-do. Workflow-managed IDs, actors, state and versions stay on the canonical task. Automatic tasks validate on the next authorized scan; Manually initiated communication tasks also resume their validated current Notion submissions through the shared queue. New DataCompletion uses task-input-v2; existing routes remain compatible until verified upgrade. Content confirmation, send approval and reminder receipt remain separate. See [operator actions](references/operator-actions.md) and [input contract](references/pending-input.md).

## Mail recovery and task clarity

Garbled mail suspends fact extraction until the same authorized MIME source is strictly decoded or handed to manual recovery. The offline Python 3 helper has no network/send capability and does not repair the upstream connector. See [mail decoding](references/mail-decoding.md). Source identity uses exact stored fields rather than Notion display Markdown; task pages show one current state/version, original links and missing dependencies.

## Standard CRM Notes and monitoring

Init creates/reuses `Aimore/Templates/CRMNotes` with `aimore-crm-note-v1`: a required audit header and four fixed plain-text sections. Notes contain no Markdown/HTML. The offline renderer checks missing fields, timezone/offset, unsupported formatting and approved-byte integrity; it cannot grant approval or write CRM. See [CRM Notes](references/crm-notes.md). Existing incomplete approved notes require a corrected new review, without rewriting old CRM entries.

For an existing installation, explicitly request an init upgrade after reloading the current version to register the template and monitoring fields. Setup preserves IDs, decisions and history and does not resume business tasks. [Connector I/O](references/connector-io.md) handles current tool contracts, text-only success and bounded rate-limit recovery; [monitoring](references/monitoring.md) separates actual service times, native/recovery health and unresolved quality failures from recovered or simulated issues. Live behavior and independent send gates still need the designated test session.

## Customer page names

Clients shows verified customer names, with email/phone disambiguation for known same-name contacts. Exact CRM IDs remain in metadata; workflows reuse registered page IDs. An explicit init upgrade renames verified legacy ID-titled pages in place, preserving links, children and approvals. Operator-customized titles remain intact. See [customer pages](references/client-pages.md).

## Evidence and continuation

Use [task routing](references/task-routing.md) for explicit owner/resume metadata rather than dispatching every pending task as communication Notes. Use [offline evidence checks](references/evidence-checks.md) to preserve specific upstream errors, inspect page-wide saved Notion link patterns and validate routes under the actual shortcut policy. A scan may record an Automatic send decision while still deferring the send; these phases do not grant broader permission. Helpers never call connectors, approve or execute work. Explicit init upgrade repairs only proved legacy routes and retains the action-page changes from 0.1.10.

## Current publication and report boundaries

Owners synchronize canonical task status/binding and the active action result in the same transition, with old versions clearly historical. Verified Today linked views follow those fields without another queue snapshot; legacy installations retain their original queue until explicit upgrade. Native saved preview and exact downloaded bytes precede review. Report-only fixes its own reports and logs; outside task/preview issues are linked for a separate owner command. The offline publication helper plans exact status patches, checks direct-upload preview evidence and preflights report write targets. It is not a server or an authorization engine. See [Notion publication](references/notion-publishing.md).

Use [publication validation](references/publication-validation.md) for actual schema enums, typed saved-page coverage, current status/result/input consistency and completion-gate evidence. Report completion/final Success is deferred until current required checks pass; native-reference sections are excluded from whole-section patch plans. Explicit one-message SMS channel acceptance and timing exceptions remain separate from automatic enrollment under [SMS rules](references/sms-rules.md).

## Experience library

[Experience/README.md](Experience/README.md) is the portable operation-to-tip index. The entry/shared contract directs Skills to read only relevant cards before risky operations, and to reuse them within the invocation. Cards distinguish verified observations from open route/transport defects; they grant no extra access or sending authority and do not claim a fix merely by documenting it. No historical development workspace access is required.

## Data routes and stored replies

Communication DataCompletion uses CompleteCommunicationData and cannot append Notes; Notes approval/append remains ReviewCommunication. Gmail replies use an actual stored draft: create, replace MIME without resetting reply context, verify raw draft, review, send_draft, then finish from its original successful response without re-querying Gmail. The HTML-only offline adapter rejects asset-bearing packages rather than dropping them. All eight owners use version/binding-aware owner-write completion preflight; provider success remains distinct from publication or delivery. See [owner completion](references/owner-completion.md) and [reply transport](references/reply-transport.md).

## Periodic scan controls

`@eightdegrees-sales-workflow start` creates/reuses one native 30-minute (20-minute optional) approved-work task; `stop` deletes it. Exact host cadence and task readback are required. Installation/init create no schedules. Native ticks may execute valid approved Automatic steps; public run-auto executes one cycle of independently approved Automatic work and Manual intake provenance stays intact while submitted communication decisions resume through the queue. Explicit no-send requests remain restricted. Unsupported native scheduling/deletion is reported explicitly. See [schedule lifecycle](references/scheduling.md).

## Native image previews

Reply drafts can use a native Notion PNG rendered from the exact frozen HTML. See [image preview](references/image-preview.md) for the optional existing-Playwright renderer, saved-asset download checks and version-bound completion evidence, and [preview experience](Experience/preview-evidence.md) for correct nested reference handling. Original HTML, copy inspection and independent approval remain required. No browser or service is installed automatically.

## Owner preflight and recurring read cost

Use the packaged [execution preflight](references/execution-preflight.md) to
validate actual inputs, generate required checks, persist the plan and read back
its original run before dependent work. Refusals produce no usable plan.
Canonical fact labels preserve null; stored-reply headers keep the current
scalar contract. Recurring scans reuse per-phase captures and known view
fallbacks while still checking eligible human inputs and fresh send guards.
This is local model-assisted validation, not a new server or MCP interceptor.

## One queue and notification SMS

run-auto scans authorized Gmail/reply sources, current Notion submissions, due follow-up records, relevant configured Dropbox versions and due reminders/confirmed appointments. It follows newly ready owner steps in one bounded cycle, without restarting the scanner or sleeping for future work. Manually initiated communications keep Mode=Manual and resume validated Notion decisions without another continue command.

Factual notification SMS is permitted by default under notification-sms-v1. Generate/edit, freeze and send when due without per-message ContentReview/SendApproval or a second chat question. Keep current device/channel, source, stop/Pause, window/count and unknown-attempt checks. Email and CRM facts still need review. Notification queue tasks use ScheduledWork and read-only result pages rather than human approval forms.

See [queue execution](references/queue-execution.md), [SMS notifications](references/sms-notifications.md) and [material handoff](references/material-handoff.md). Explicit init upgrade adds the machine-queue category/discovery and bound standing policy while preserving existing databases, five human views, answers/history and recorded user disable/revocation. Installation still creates no schedule. Offline checks are not live automatic workflow or channel acceptance.

## Unattended approved work

[Unattended operation](references/unattended-operation.md) adds bounded scan/restart checkpoints, scoped restriction overlays and related SMS result convergence. Defaults admit at most 12 owner steps within an eight-minute soft budget, reserving the final minute for persistence. Unknown requests are reconciled, never blindly resent. Human decisions stay in Notion; unrelated ready work continues. Actual cloud scheduling, serialization and channel readiness require native acceptance.

## Scan timing defaults

New installs use a 30-minute scan interval; choose the optional faster mode with
`@eightdegrees-sales-workflow start interval_minutes=20`. An unqualified start
keeps a supported saved choice. Each cycle has a 15-minute soft budget including
a 2-minute publication reserve; stop admitting new phases at minute 13 and
preserve unfinished work for the next tick. Existing explicit customer budgets
are preserved until deliberate init upgrade; plugin installation never changes
a live native task. Configure/update the same owned task through explicit start
and verify its actual cadence.

See [provider handoff completion](references/provider-boundary.md): finish from the original successful dispatch response, verify our records and CRM, and do not check external transmission or delivery.

## Discover before processing

run-auto starts with [event discovery](references/event-discovery.md): unchanged
inputs and human waits exit immediately; new submissions, source changes and due
timers wake only affected owners. See [prospective review/dispatch gates](references/pre-action-order.md)
for saved-copy agreement before controls and saved queue admission before calls.
Offline checks do not establish live timing or host-enforced ordering.

## Short scans and handovers

Use [the short execution procedure](references/scan-fast-path.md) and
[the incident card](Experience/scan-handover.md). New local operations are
scan.watches, connector.capture and run.record; they prepare data, not approvals
or external actions. Unchanged completed projects need no source sweeps.
