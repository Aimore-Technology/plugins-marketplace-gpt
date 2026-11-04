---
name: eightdegrees-initialization
description: "Initialize or inspect the EightDegrees sales workflow in the customer's Notion and authorized accounts; configure pilot defaults, connections and readiness."
---

# Initialize EightDegrees

Apply [API result and minimal-read policy](../../references/api-result-policy.md) before this workflow. Successful writes use acknowledgements/record IDs; do not fetch stored bodies to compare. Reuse initialized workspace metadata.


Apply [provider handoff completion](../../references/provider-boundary.md): successful Gmail/AndroidSync acceptance finishes dispatch. Verify our request/approval and own records; CRM writes also finish on successful API acknowledgement and NoteId. Do not re-query external send status or verify delivery.

Before dependent writes, use [execution preflight](../../references/execution-preflight.md) to generate and persist this owner's affected-role plan, then confirm its API acknowledgement; a failed preparation stops the phase. Apply the [owner completion contract](../../references/owner-completion.md). Before final Completed/Success, run its owner-write preflight with the frozen current evidence; report-only uses report-write. A successful provider action with missing publication evidence stays a partial result, never a reason to repeat the provider action. Before EVERY Notion page write, including the first create and progress/result properties, run [exact-call preflight](../../references/notion-mutation.md); only use its returned unchanged arguments after exit 0 and NotionMutationPrepared.

Before making tasks/action pages executable, create and validate OwnerSkill/ResumeStep/ResumeContractVersion using [task routing](../../references/task-routing.md). Explicit upgrade recovers eligible legacy owners from original payload/run/operation evidence while preserving parent Workflow, record IDs, approvals and completed steps. Sales source/draft/send and mailbox checkpoint tasks must not default to communication. Ambiguous routes stay pending; init does not execute repaired tasks. Distinguish GHL Workflow-API capability absence from working contact/Notes access under [connector I/O](../../references/connector-io.md).

Read [operating-contract](../../references/operating-contract.md), [notion-model](../../references/notion-model.md) and [platform-runtime](../../references/platform-runtime.md). Load [pilot defaults](../../references/pilot-defaults.json) for the initial configuration, not on every later skill call.

1. Check the customer's own authenticated Notion, Gmail, Dropbox, CRM and optional SMS/Calendar tools. Ask which workspace language to use: Chinese or English; save the explicit answer as customer_setup.workspace_language (zh-CN or en). Reuse an existing saved choice unless a change is requested; never infer a permanent choice just from account locale. Use this language for task titles, input forms, guidance and reports; keep schema keys stable and source/customer-message language independent. Configure operator_id, operator_name, operator_email and any verified operator_sms_number using [operator setup](../../references/operator-setup.md). Resolve supplied/profile information without a fixed person default. On an explicit upgrade, preserve old IDs/history and migrate legacy fields before resuming automation. Verify the actual CRM and LocationId before any writes; do not request passwords/tokens in Notion. Record missing capabilities per stage rather than blocking independent P0-A tests.
2. Register authorized Dropbox work folders, project versions and the operator as maintainer. Keep all old versions; no moving, archiving, cleanup, overwrite, migration or SSD backup takeover. Resolve unclear current versions with the operator.
3. Create/reuse the clean `Aimore/` tree and registered IDs. Follow [customer pages](../../references/client-pages.md) for human-readable titles, identity metadata and in-place legacy renaming. Keep ONE PendingTasks database/five human issue views; add ScheduledWork to its actual Category select and register complete machine-queue discovery. Set up Today and its registered native display views under [operator experience](../../references/operator-experience.md), retaining ordinary action pages under Actions; expose direct current action links. Preserve the five original execution-discovery views and register Today display views separately. Apply [Notion publication](../../references/notion-publishing.md) for schema types, current summaries and the current entry (native Today or legacy queue): historical Current operation headings become clearly historical, with native child tags preserved. Data-only pages have no choose-one prompt without choices. New DataCompletion uses task-input-v2 under [pending input](../../references/pending-input.md). Explicit upgrade preserves inputs/decisions/IDs/Mode without submission or execution; unresolved in-flight legacy records keep one original input route until reconciled. Presentation migration never repairs/reapproves business content. Add RunSettings; do not install developer hierarchy. Report missing page/view capability or partial migration honestly.
4. Create/reuse `Aimore/Templates/CRMNotes` from the packaged plain-text template using [CRM Notes](../../references/crm-notes.md); register its actual page ID/version and provide localized field guidance. Set up the approved ClientPersona template. On explicit upgrade, add the template without rewriting old notes or silently migrating approvals; incomplete approved drafts need a new reviewed version before write. Map existing Notes/activity-log capabilities; do not create custom CRM fields. Existing contact reads need no new factual approval; proposed notes/persona changes do. Examples may tune bullet prose, not remove required headers/sections or introduce Markdown into CRM Notes.
5. Register actual Gmail allowed labels, exclusions, time range, sender/signature and separately authorized internal-reminder scope. Missing labels never imply all-mail access. Use existing templates and 3-5 authorized real sent samples for writing style; do not fabricate samples or require redaction. Attachments default unopened.
6. Apply [inquiry intake](../../references/inquiry-intake.md): create/reuse `AimoreInquiry` as the output classification label, saving actual inquiry_label_id and inquiry_label_name without adding it to required read filters. Unknown senders need no pre-labeling. Separately create/reuse `AimoreScanned` only as a saved-progress checkpoint, not as an allowed-read label. Persist source and progress before applying it. Do not auto-label unrelated mail into scope.
7. Register the operator's own SMS number and original reply inbox expectations. Default standing factual-notification SMS permission to enabled with no per-message review under sms-notifications.md. Verify the authorized sending connector/device configuration. Do not require test delivery, physical sender display, stability probes or inbound reading to enable one-way notifications. Missing actual sending tools/configuration blocks dispatch; record inbound coverage separately. Preserve recorded explicit disable/revocation and old stop/unknown attempts. New installs use sms_follow_up.new_cycle_requires_explicit_manual_start=false: ordinary source-bound inquiries use standing notification authority. During explicit init upgrade, adopt this default when the old true value is the legacy structural default, preserving an actually recorded operator requirement for manual initiation. Do not infer a new user consent or change live cycle counts/expiry. Ordinary new inquiries need no separate init or context_override; explicit timing/count exceptions still retain their original scope. Verify Calendar access only for confirmed work appointments. Leave Hub/Hux and untested extra channels disabled; avoid duplicate existing reminders.
8. Save actual pilot-v1 business settings. New installs use scan_control={contract:scan-control-v1,enabled:false}. On explicit upgrade preserve an existing switch; when absent, preserve only effective verified legacy enabled/approved Running state under scan_control.py, otherwise remain stopped. Do not copy fresh false over a verified running installation. Native job IDs/runtime/host/lifecycle remain untouched historical metadata. start/stop only changes the switch, never creates/updates/deletes tasks or modifies cadence. The operator configures periodic local run-auto separately;30 minutes is suggested,20 optional. No scheduler API, host/session identity or cadence proof is required for initialization or scanning. Keep original business scope, SMS standing authority, user limits, approvals and due work.

9. Use the staged checks in [pilot acceptance](../../references/pilot-acceptance.md) only within the current invocation policy; setup-only init records readiness and defers business tests. Set up the monitoring fields/semantics in [monitoring](../../references/monitoring.md), preserving legacy values/history on upgrade. Customer email needs exact approval; notification SMS uses its bound standing policy and actual channel checks. Record Passed/Failed/Untested per capability, not a blanket green status.
10. Return root, settings, task and health links; configuration version; actual connection/cadence results; and readiness by stage: ReadyForTest, WaitingForConnectionOrData, or Failed. Recommend the next independent test. Defaults adopted does not mean installation, real sending or customer acceptance passed.

## Operator path and local checks

Apply [operator experience](../../references/operator-experience.md) for Today, short review summaries/differences, verified prefill and explicit post-submit guidance. Give concise chat progress at meaningful stages; an internal read/check does not require another Notion status write. Run [local check batches](../../references/local-check-batch.md) over unchanged original captures instead of repeatedly serializing/rereading them. Keep fresh external-action safeguards; confirm saved results from original API acknowledgements only. Verified Today linked views replace manual queue snapshots; legacy queue mode remains until explicit upgrade.

## Unattended configuration

Add missing queue_execution cycle_budget_seconds=900, publication_reserve_seconds=120, bounded_work_items=12 and checkpoint_contract=scan-checkpoint-v1 on explicit init upgrade. Preserve saved user limits, native lifecycle, review decisions and disabled authority. Existing 480/60 budgets remain valid; replace them with 900/120 only when the operator explicitly adopts the new defaults during init upgrade. Do not reset a deliberate 20-minute choice or mutate a live native schedule during init; start/stop never changes its native ID/cadence. Use scan-control-v1 without registering a unique executor or requiring activity/serialization evidence before reporting readiness under [unattended operation](../../references/unattended-operation.md); do not create schedules during init.

Do not select/rebind a sole conversation or request native host/thread/turn
identity. New defaults omit single_owner_required/executor_mode; historical
values and on_demand_executor_thread_id do not gate current execution. Preserve
original attempts, approvals, stop state and configured native job IDs. This
behavior applies immediately on upgrade without another init.


## Compatible records and channel setup

Use [record contracts](../../references/record-contracts.md) for new snapshots
and original result layouts. Read [SMS channel setup](../../references/sms-channel-setup.md)
when capability is incomplete: create a deduplicated ordinary setup input, not
only a read-only error. Register any explicit controlled one-message test from
the original operator setup context, with exact destination/device/sender,
context, expiry and attempt pointers; never certify unverified ordinary SMS or
an unavailable inbound reader. Init still performs no customer send.

Adopt send_completion.policy=provider-handoff-v1 on the authorized configuration
update: Gmail/AndroidSync success responses complete dispatch with no provider
status or recipient checks; CRM writes finish on successful API acknowledgement and NoteId.
Never rewrite old decisions, receipts or observed provider states on upgrade.

## Event discovery index

Register queue_execution.event_discovery_contract=scan-event-index-v1 and the
actual event_index_page_id for one compact Aimore/Dashboard/EventIndex page.
Use [event discovery](../../references/event-discovery.md). This page stores only
scope/cursors, input fingerprints, pending work identities/due times and durable
owner-result pointers. Initialize from complete actual registered discovery
coverage, never from an assumed empty workspace/mailbox. An explicit upgrade
preserves prior source cursors, accepted submissions, future work and attempts;
missing/expired coverage needs a targeted baseline before claiming idle.
This creates no task/schedule and executes no business work. Add missing settings
without resetting human choices, scheduler state or authority.

When the operator explicitly initiates a different inquiry/context, save its
source/customer/number binding and any bounded timing/count exception under
[saved SMS context initiation](../../references/material-handoff.md). Reuse that
authorization on later scans; do not request it again, copy a prior project's
stop into global scope, reopen old cycles or extend an expired exception.

On explicit 0.1.33 upgrade, register one recovery wake-up for a registered
ClosedPriorContextBlocksExplicitNewContext stub that passes the original-page
and current saved-authorization checks. Bind the existing SMS task/step/version
and a stable scoped-sms-initiation-v2 repair revision in EventIndex's recovery
feed under [event discovery](../../references/event-discovery.md). This makes the
repair visible once to run-auto without repeated human submission or quiet-tick
history sweeps. Init only registers the wake-up; it does not activate/send work.
Stopped, used, unknown or expired work remains blocked with its original reason.

## Required business configuration review

At every explicit init/upgrade run setup.audit on the original saved settings.
Show a short business-readable configuration summary: operator name, scanned
mailbox, actual allowed label names/IDs and date scope, authorized Dropbox
folders, sender/signature, CRM location, Notion root/language and optional
notification channels. Never substitute installation success for this summary.
Profiles only propose an operator name; fresh setup asks the operator to choose
the name and source scopes unless already explicitly supplied. Do not guess
Dropbox scope, choose UNREAD as a fallback, or treat AimoreScanned as inquiry
authorization. A broad unread scope must be described as such.

On upgrade preserve prior valid authorizations and show their saved values; do
not demand repeated consent simply because the package version changed. Record
which choices were supplied now versus inherited; installation or a profile is
not a new confirmation. Missing required choices get one concise setup input,
with concrete fields and owner/ResumeStep=ValidateSetupInput. Conflicting legacy
projections are displayed together; never union folder sets or silently replace
current scope. customer_setup holds the current business scope; legacy duplicate
fields are diagnostic and must not secretly drive another scope. Apply only
explicitly authorized corrections, retaining original cursors and attempts.

Persist/link the configuration summary under Dashboard and return it with the
normal init result. Readiness is per capability. This audit is setup-only, not
another scheduled-cycle gate: existing saved sources can recover without a full
re-onboarding; only genuinely missing/revoked permissions or necessary facts
block their affected work. Existing stop/revocation always remains effective.
