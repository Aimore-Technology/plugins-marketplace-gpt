---
name: eightdegrees-workbench
description: Operate the 8Degrees sales workbench through its Platform MCP tools (names start with platform_). Use for daily sales work in 8Degrees — what is waiting, reviewing and approving reply drafts, preparing a reply to a customer email, recording a customer communication or pasted SMS, resolving an unmatched contact, supplying missing facts, customer SMS and opt-outs, commitments, the daily brief, the knowledge base, notifications, templates and settings. Not for editing the automation flows themselves (that is the separate administration connection).
---

# 8Degrees workbench

The 8Degrees workbench receives property inquiries, prepares replies from indexed project materials, holds every customer email and CRM Note for review, sends customer SMS notices and keeps the CRM up to date. You reach it through the `platform_*` tools of the business MCP connection. The browser workbench and these tools call the same services, so every rule below is enforced by the server too; follow them so you do not waste calls or mislead the operator.

You act for one signed-in operator, with only the permissions they ticked when they connected. If a tool is missing from your list, the connection lacks its permission (see "Permissions"); say which one, do not look for a way around it.

## Start every session the same way

1. `platform_get_workspace` — who you act for, your permissions, whether scanning is on, review counts, settings and what data the workspace reads.
2. `platform_get_health` if anything looks wrong. A part that is switched off or cannot be checked is not a fault.
3. For "what needs me": `platform_report` `mode=overview` (the home page) or `platform_list_work` per kind (`reviews`, `inquiries`, `contacts`, `sms`).

Give the operator links from the results (`link`) when they want to open something in the browser.

## Rules you must keep

- **Nothing reaches a customer without an approval of that exact version.** Customer email approval is locked on during the beta and you cannot turn it off. Approve only when the operator tells you to, for the task they named, after they have seen the current text.
- **Decide on what you read.** `platform_decide_task` takes the `expectedVersion` and `digest` from your last `platform_get_task`. If it answers `conflict`, someone changed the task: read it again, show the operator what changed, and ask again. Never retry a decision with fresh values on your own.
- **An edit needs a new approval.** `platform_update_draft` saves a new version and invalidates the old approval.
- **Never resend.** An accepted or uncertain send is kept for reconciliation. Do not repeat a submission to "make sure"; use `platform_get_operation`, `platform_get_task` or `platform_get_sms` to see what happened.
- **Request IDs make writes safe to repeat.** Write tools with a `requestId` return the original result when called again with the same ID and arguments. Make one ID per intended action (8–100 letters, digits, `-` or `_`) and reuse it only to retry that same action.
- **Reply language.** Customer replies and customer SMS are in Chinese or English only: Chinese in the customer's script (simplified or traditional) when the customer wrote in Chinese, English otherwise. An inquiry in another language is answered in English; `inquiryLanguage` on the task names the customer's language. When you edit a draft, write in the task's `replyLanguage`.
- **Facts come from the materials.** Prices, sizes, dates and other project facts come from the indexed materials (`platform_get_materials`) or accepted knowledge, never from memory or a template. If a fact is missing, say it is not confirmed; missing facts become an information follow-up.
- **SMS.** Every customer SMS fits one 70-character message and ends with the sender name and an opt-out line. An opt-out applies to that customer for every inquiry and only an operator lifts it, in the browser. Incoming SMS is not read: when a customer replies STOP, the operator tells you and you record it with `platform_record_sms_opt_out`.
- **No customer data where it does not belong.** Do not copy customer emails, phone numbers or message text into other tools, notes or chats beyond what the task needs.

## Common jobs

### Review a reply draft or CRM Note
1. `platform_list_work kind=reviews status=WaitingForReview`, then `platform_get_task` for the one the operator picks.
2. Show the customer-facing text, the reviewer translation, `customerSms` (the SMS notices that approving this version also releases), the materials it used and `missingInformation`.
3. To change wording: `platform_update_draft` with `side=original` (customer text; translation is regenerated) or `side=translation` (the customer text is regenerated). CRM Notes accept `side=original` only.
4. On the operator's word: `platform_decide_task` `approve`, or `return`/`cancel` with the reason they give. Approval queues it; the next cycle sends it. Follow with `platform_get_task` to see `ExecutionClaimed` and `ReceiptRecorded`.

### Prepare a reply to a customer email
1. `platform_find_email` by sender or subject to get the Gmail message ID.
2. `platform_get_materials` without arguments to list projects; pick the project key (and lot) the email is about. Ask if unclear.
3. `platform_prepare_reply` with a new `requestId`. Poll `platform_get_operation` until `ReviewRequired`, then review as above.

### Record a customer communication
`platform_add_communication` with pasted `text` plus `customerEmail` or `customerPhone`, or a `gmailMessageId`, or a `dropboxFilePath`. For a pasted SMS set `channel=sms` and give the sender's phone (an Australian local number becomes +61). State `ContactMatchRequired` means the contact is not in the CRM: resolve it as below, and the communication continues.

### Resolve an unmatched contact
1. `platform_list_work kind=contacts`, `platform_get_contact_inquiry` for details.
2. `platform_search_contacts`. If exactly one is right, `platform_resolve_contact` to link it. Create a contact only when the operator says so, with the details they confirm, and the `contactType` (Developer, ChannelAgent, Buyer, Other) they choose.

### Supply missing facts
`platform_get_inquiry` shows `missingInformation`. When the operator gives the facts, `platform_supply_information` under the version you read. The follow-up goes out in the same email thread and starts no new SMS cycle.

### Customer SMS
`platform_get_sms` explains why a notice waits or stopped. `platform_stop_sms` ends one inquiry's follow-up; `platform_record_manual_sms` records an SMS the operator sent by hand; `platform_reconcile_sms` records what the operator found out about an SMS whose result is unknown (nothing is resent). `platform_list_sms_opt_outs` shows the opt-out list.

### Commitments
`platform_list_commitments` (default: what needs attention today). `platform_extract_commitments` on a task only suggests; a suggestion is tracked after the operator confirms it with `platform_resolve_commitment`.

### Daily brief and reports
Read the brief with `platform_report mode=brief`. `platform_send_daily_brief` emails it to the sales mailbox itself; each call sends one more email, so call it once and only when asked.

### Knowledge base
`platform_list_knowledge_projects` gives the `projectId` every other knowledge tool needs; `[Project]` names are real-estate projects, `[Org]` names are company knowledge. Search with `platform_search_knowledge`. Propose with `platform_propose_knowledge` and at least one real source; an operator decides. Import a project's Dropbox folder one file per call with `platform_import_knowledge_from_dropbox` while `remaining` is above zero.

### Notifications
The workbench never calls you. To follow notifications, poll `platform_list_notifications` with the cursor from your last call. `platform_send_notification` (needs `platform.notify`) posts plain text to the workbench, shown as coming from you, at most 30 an hour; it never reaches a customer.

### Settings and templates
`platform_configure_workspace` changes one settings section under its revision; `platform_set_scanning` pauses or resumes scanning; templates via `platform_list_templates` / `platform_save_template` under the version you read. Change settings only when the operator asks.

## Permissions

| Permission | Lets you |
| --- | --- |
| `platform.read` | Read everything listed above. Always included. |
| `platform.submit` | Prepare replies, record communications, supply facts, commitments, knowledge proposals, run a cycle, send the brief. |
| `platform.review` | Edit drafts; approve, return or cancel tasks. |
| `platform.contacts` | Search and resolve contacts, people types, SMS opt-outs, stop or reconcile SMS. |
| `platform.configure` | Settings, scanning, templates, training practices, knowledge Projects. |
| `platform.notify` | Send and withdraw your own workbench notifications. |

To change permissions the operator disconnects the connector and connects again, ticking what they want.

## Errors

| Error starts with | Meaning and what to do |
| --- | --- |
| `conflict` | The record changed since you read it. Read again and ask the operator. |
| `invalid_argument` | Fix the arguments; the message says which. |
| `not_found` | Wrong ID, or the item is gone. |
| `incomplete` | Something must be done first (for example workspace setup in the browser). |
| `reauthorization_required` | The operator must sign in to the workbench in the browser again. Stop and tell them. |
| `provider_unavailable` | Gmail, CRM, Dropbox, the AI service or the automation platform did not answer. Do not repeat writes; check later with the read tools. |

## What you cannot do here

Send anything to a customer without a recorded approval; turn off customer email approval; lift an SMS opt-out; set up the workspace or authorize Gmail, Dropbox, CRM or the AI service (browser only; `platform_get_connection_setup` gives the link); delete a knowledge Project unless the connection was made by a portal administrator; change the automation flows.

See `references/tools.md` for every tool by area.
