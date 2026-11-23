# Operator setup and settings upgrade

## Fresh installation

P0 has one configured operator per customer installation. Use `customer_setup.operator_id` and `operator_name` from Dashboard RunSettings; neither has a packaged default. The operator reviews CRM facts/email content and email sends, receives internal reminders and submits communication decisions in Notion. The shared queue resumes them; factual SMS notifications use standing authority without individual review. This is a configurable role, not a named person or a new multi-user identity system.

Initialization uses available authenticated profile information to propose the operator's display name. If it is unavailable or ambiguous, ask the user to identify the operator. Create and persist a stable installation-local operator ID if no suitable existing ID is available; do not represent that local ID as a provider account identity. Register actual authorized Gmail, Notion, Dropbox and optional CRM/Calendar/SMS account references separately; do not assume matching names prove account ownership.

Populate `operator_email` with the actual internal notification destination. Keep it separate from `gmail_account` (the scanned mailbox) and `sender_account` (the approved sending identity), even when their values are the same. Register `operator_sms_number` only when supplied and verified for the relevant channel. Missing operator name/ID blocks new business writes and sends; missing optional SMS leaves that channel disabled. Read-only connection diagnosis can continue. Do not infer real email addresses or phone numbers from a person's name.

Record `OperatorId` on runs/tasks and `ApproverId` plus the display name on new decisions. Read settings and original approval evidence before action. A reminder addressed to the operator is not a customer message; its receipt is not send approval. The current operator must explicitly approve the exact send version/window.

Changing the operator, sender account, reminder destination or relevant connected account is an explicit configuration change, never a guessed side effect of a login change. Pause affected automation, recheck actual authorization/scope and pending attempts, and obtain new approval for affected unsent actions. Preserve historical actors, approvals, task IDs, provider IDs and completed steps. Existing unknown external results must still be reconciled, not reassigned and retried.

## Workspace language

At fresh initialization, ask the operator to choose Chinese or English before creating user-facing pages. Accept an explicit choice already supplied in the request. Persist customer_setup.workspace_language as zh-CN or en; keep the packaged default null. Reuse the saved value on later init calls. A legacy installation with no choice is asked once on its next explicit init/upgrade; preserve its existing page content while awaiting the answer. Outside init, an unset choice may use the current conversation language for new guidance without saving it as a permanent preference. A language change affects newly generated task/input/report text, not schema/property keys, source documents, historical decisions or approved customer payloads. Ask separately before translating existing approved content.

## Upgrade from 0.1.0

Only initialization performs a settings/schema upgrade in the customer's Notion, during an explicit setup/update request. Installing this package changes no live Notion data. For the additive task-input-v1 upgrade, follow [pending input](pending-input.md); keep settings_schema_version 2 and preserve all existing business settings. Workspace language is an optional additive setting until the operator chooses it. Read and preserve the old settings and registered IDs first. Copy a legacy value into its new field only when the new field is absent; conflicting values require operator review. Never silently replace an existing operator name or claim the currently logged-in person made historical decisions.

| Legacy 0.1.0 key/value | Current key/value |
| --- | --- |
| `customer_setup.john_sms_number` | `customer_setup.operator_sms_number` |
| reminder channel `john_gmail` | `operator_gmail` |
| sensitive-original policy `john_manual_only` | `operator_manual_only` |
| task input `JohnInput` | `OperatorInput` |
| waiting status `WaitingForJohn` | `WaitingForOperator` |

Retain existing populated `operator_id` and `operator_name`; unset values require setup. For a new `operator_email`, propose an existing authorized notification destination and have the operator confirm it; never assume a sender or scanned mailbox is the correct recipient. Add `settings_schema_version: 2` only after validating the resulting settings. `configuration_version: pilot-v1` continues to identify the unchanged timing/business defaults.

Preserve actual database/property/page IDs and task relationships. Reuse or rename registered properties/options/views only if supported; otherwise register an explicit legacy-to-current field mapping. Avoid creating a second database or disconnected input field. Keep historical decided/finished values intact, including actual person names in logs. An old pending send lacking a reliable operator binding must receive a new explicit approval; do not invent ApproverId or transfer the old approval to another user. Keep scanning stopped until required customer setup is available; no unique execution identity is required.

## Scanning control upgrade

Add scan_control-v1 without changing effective scanning: fresh installs are
stopped; verified legacy enabled/approved Running state is preserved when the
field is absent. Never replace an explicit switch. Old scheduling/native IDs,
unknown attempts and executor metadata remain untouched historical records.
start/stop changes only the switch. No scheduler discovery, lifecycle migration,
cleanup, prompt edit or task creation/deletion is part of this upgrade. Preserve
all business facts, approvals, submissions, cursors, counts and attempts.

## Visible configuration, not hidden defaults

Use setup.audit during explicit init/upgrade and expose its saved values in a
Dashboard configuration summary. Include operator display name, mailbox, actual
read-label names/IDs, read time scope, Dropbox folder allowlist, sender/signature,
CRM location and workspace/language. Show inherited values as inherited; do not
claim this deployment obtained new consent. Fresh init asks for a name and scope
selection even when profiles can propose defaults, unless already supplied.

UNREAD is a broad unread filter, not a dedicated inquiry folder. AimoreScanned
is a progress marker, not permission. Missing scope is not all-mail access.
Customer_setup.dropbox_work_folders is the saved current folder allowlist; show
conflicting legacy dropbox.work_folders without silently merging/expanding it.
Collect missing/corrected values in one setup form with explicit submission,
then resume ValidateSetupInput. Preserve existing validated scope on upgrade;
this setup audit is not a fresh global prerequisite for every timer wake.

Inquiry labeling is an output, never a prerequisite read filter. Init creates/reuses AimoreInquiry and records actual inquiry_label_name/inquiry_label_id separately. Scan classifies each newly admitted message within the authorized scope, including unknown senders. See [inquiry intake](inquiry-intake.md). Preserve current UNREAD consent; do not require the operator to predict sender addresses or pre-label incoming inquiries.
