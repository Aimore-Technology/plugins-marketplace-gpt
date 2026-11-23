# 8Degrees workbench tools by area

Generated from the workbench's Platform MCP guide for beta 01 (2026-11-23). The tool list your connection shows is authoritative: it hides tools your permissions do not allow.

# All 61 tools

Tools marked **read** change nothing. Every other tool is a write and needs the
permission shown.

## Workspace and work (17, `platform.read` unless the row names another permission)

| Tool | What it does |
| --- | --- |
| `platform_get_workspace` | The workspace, the signed-in operator, this connection's permissions, the scanning switch, review counts, every settings section with its revision, and what data the workspace reads. |
| `platform_list_work` | Lists work items, newest first: `reviews`, `inquiries` (information follow-ups), `contacts` (unmatched contact inquiries) or `sms`. |
| `platform_get_task` | One review task in full: text, translation, original source, version, the customer SMS released with it, and the actions allowed now. |
| `platform_list_people` | The people in the workbench's recent tasks, inquiries and matched contacts: type, referrer, projects asked about, how often they wrote and the amounts they wrote themselves; and the lines of the relationship map. Optional `type` filter. |
| `platform_list_training` | The review questions waiting for the operator and the practices that guide reply drafts. |
| `platform_reply_training` | Passes the operator's reply to the AI's review questions and returns the AI's next questions or its proposed practice. The proposal is not saved. Needs `platform.configure`. |
| `platform_answer_training` | Records the operator's answer to a review question: a practice, or a one-off. Needs `platform.configure`. |
| `platform_save_practice` | Adds, rewords, retires or restores a practice. Needs `platform.configure`. |
| `platform_get_health` | Whether the service can do its work: overall status and the state of the workbench service, the sales records, the automation platform, the mail scan and the SMS phone. Works while Activepieces is down. |
| `platform_get_sms` | One customer SMS notification: status, why it waits or stopped, consent basis, opt-out state, texts already handed to the phone, and `audit`: what the phone gateway reported for each accepted SMS afterwards. |
| `platform_get_inquiry` | One information follow-up: the customer, project, the facts still missing (`missingInformation`), the facts already supplied, status and version. |
| `platform_get_contact_inquiry` | One unmatched contact inquiry: channel, original source and summary, the email, phone and name found in it, status and version, and the CRM contact once chosen. |
| `platform_list_sms_opt_outs` | The workspace-wide SMS opt-out list, with active and lifted opt-outs. Lifting one is done in the workbench only. |
| `platform_get_materials` | The indexed project materials. Without a project it lists the cached projects; with a project key it returns that project's facts. |
| `platform_find_email` | Searches the sales mailbox for an original customer email by sender or subject. Returns Gmail message IDs for the reply and communication tools. |
| `platform_get_operation` | The state of a submitted command and the review, inquiry, report or run it produced. |
| `platform_get_connection_setup` | Whether Gmail, Dropbox, CRM or AI is connected, with the workbench link to authorize it. Returns no credentials. |

## Runs and reports (4, `platform.read` unless the row names another permission)

| Tool | What it does |
| --- | --- |
| `platform_list_runs` | The 30 most recent runs of the business workflows. |
| `platform_get_run` | One run's workflow, status, timing and step outcomes. No step inputs or outputs. |
| `platform_report` | `mode=overview`: the workbench home page: what waits now, the first ten waiting items, the last 24 hours, service health and the last seven days of results. `mode=brief`: today's daily brief from workbench records. `mode=sms_audit`: whether the SMS phone is online, and the gateway's later status for recent SMS. `mode=usage`: how often each feature was used, by workbench and assistant, and the weekly beta reports. `mode=list`: days of a month with a saved report. `mode=read`: one day's report. `mode=generate`: starts a new report run; this mode needs `platform.submit`. |
| `platform_send_daily_brief` | Prepares the daily brief from the records as they are now and emails it at once to the connected sales mailbox itself: the "send a brief now" button. Each call sends one more email. Needs `platform.submit` and the email switched on in the daily brief settings. |

## Replies and review (6)

| Tool | Permission | What it does |
| --- | --- | --- |
| `platform_prepare_reply` | submit | Prepares a reply draft for an original email from a project's indexed materials. Chinese when the customer wrote in Chinese, English otherwise. Optional `originalText` replaces the mailbox copy as the source. |
| `platform_add_communication` | submit | Records a customer communication (pasted text, pasted SMS, a Gmail message or a Dropbox file) and prepares a CRM Note for review. The email and phone are checked by the same rules as the workbench form; a pasted SMS sender's Australian local number becomes +61. |
| `platform_supply_information` | submit | Adds the facts an inquiry follow-up is waiting for. The follow-up goes out in the same email thread and starts no new SMS cycle. |
| `platform_update_draft` | review | Edits a draft from the customer-facing side or the translation side and regenerates the other. Saves a new version, which needs approval again. |
| `platform_decide_task` | review | Approves, returns or cancels the exact version read with `platform_get_task`. Approval queues it for the next cycle to send. |
| `platform_run_once` | submit | Asks the next timer tick to run one full cycle. It sends nothing the normal cycle would not. |

## Contacts and SMS (7, `platform.contacts`)

| Tool | What it does |
| --- | --- |
| `platform_search_contacts` | **Read.** Searches CRM contacts for an unmatched contact inquiry by name, email or phone. A contact whose type is known carries `contactType`. |
| `platform_resolve_contact` | Links an unmatched inquiry to an existing CRM contact, or creates a contact from basic details after checking for duplicates. Optional `contactType` (Developer, ChannelAgent, Buyer, Other): a new contact gets the matching CRM tag; an existing contact is not changed. |
| `platform_save_person` | Sets a person's type or who introduced them, under the version that was read. Kept in the workbench; the CRM contact is not changed. |
| `platform_record_sms_opt_out` | Records that a customer asked for no more SMS. Applies to every inquiry in the workspace. Lifting it is done in the workbench only. |
| `platform_reconcile_sms` | Records what the operator found out about an SMS whose hand-off result stayed unknown: Sent, NotSent or Undetermined, with a note on how it was checked. Nothing is sent again and that inquiry's SMS follow-up ends. |
| `platform_stop_sms` | Stops the SMS follow-up of one inquiry: its unsent notices are not sent. The customer's other inquiries go on and the customer is not put on the opt-out list. |
| `platform_record_manual_sms` | Records that the operator sent this customer one SMS about this inquiry by hand. It counts against the inquiry's SMS allowance and reschedules the next notice. Nothing is sent. |

## Commitments (4)

| Tool | Permission | What it does |
| --- | --- | --- |
| `platform_list_commitments` | read | Lists commitments in both directions. The default view is what needs attention today. |
| `platform_save_commitment` | submit | Adds or edits a commitment, with a due date or a review interval. |
| `platform_resolve_commitment` | submit | Confirms a suggestion, or records a commitment as done, dropped, snoozed or reopened. |
| `platform_extract_commitments` | submit | Reads one review task and stores the commitments it finds as suggestions. Nothing is tracked until confirmed. |

## Knowledge base (16)

| Tool | Permission | What it does |
| --- | --- | --- |
| `platform_list_knowledge_projects` | read | Lists the knowledge Projects. Every other knowledge tool needs a `projectId` from here. |
| `platform_search_knowledge` | read | Searches one Project's current knowledge. Unaccepted proposals are never returned. |
| `platform_list_knowledge` | read | Lists one Project's current knowledge as short summaries, newest first. |
| `platform_get_knowledge` | read | One piece of knowledge in full, with sources and lifecycle state. |
| `platform_get_knowledge_history` | read | How a Project's knowledge changed, and one change in full. |
| `platform_propose_knowledge` | submit | Proposes knowledge with at least one real source. An operator accepts or rejects it in the workbench. |
| `platform_list_knowledge_proposals` | submit | **Read.** Lists the proposals this connection made, with their status. |
| `platform_get_knowledge_dropbox` | read | **Read.** Shows the Dropbox project folder a knowledge project reads and the import state of each current file, with a link to the file. |
| `platform_link_knowledge_dropbox` | submit | Links a knowledge project to a Dropbox project folder, changes it, or unlinks it (omit `folder`), without importing. |
| `platform_create_knowledge_project` | configure | Creates a knowledge Project of kind Project (`[Project]` name) or Org (`[Org]` name). |
| `platform_rename_knowledge_project` | configure | Renames a Project or changes its kind; the name keeps a `[Project]` or `[Org]` prefix. |
| `platform_delete_knowledge_project` | configure | Deletes a Project. Only for a connection made by a portal administrator. |
| `platform_write_knowledge` | submit | Adds knowledge directly with at least one source; it is saved unconfirmed. |
| `platform_list_knowledge_proposals_for_review` | read | **Read.** Lists every proposal in a Project, whoever made it. |
| `platform_decide_knowledge_proposal` | review | Accepts or rejects a proposal with a reason. |
| `platform_import_knowledge_from_dropbox` | submit | Reads the next new, changed or failed file of the linked folder and proposes the knowledge it states, each with a quote and a link to the file. One file per call; an operator decides every proposal. |

## Notifications (3)

The same notifications the bell at the top of the workbench shows: what waits
for a person, and what assistants sent. The workbench never calls an
assistant. To follow notifications, an assistant calls
`platform_list_notifications` on its own schedule with the cursor from its
last call.

| Tool | What it does |
| --- | --- |
| `platform_list_notifications` | **Read**, `platform.read`. Without `after`: what is open now, and a cursor. With `after`: what changed since that cursor, each notification in its present state. |
| `platform_send_notification` | `platform.notify`. Sends one notification to the workbench: a title of up to 80 characters, optional plain text of up to 500, optionally about one task, inquiry, contact, commitment or SMS. Only the person who made the connection sees it unless `workspace` is true. It is not an email, an SMS or a push and never reaches a customer. 30 an hour for each connection. |
| `platform_withdraw_notification` | `platform.notify`. Withdraws a notification this connection sent. |

A connection made before 2026-11-23 does not have `platform.notify`. Disconnect
and connect again, and tick the permission.

## Settings and templates (4, `platform.configure` unless the row names another permission)

| Tool | What it does |
| --- | --- |
| `platform_configure_workspace` | Changes one settings section: approval, SMS, inquiry alerts, daily brief, notifications (which kinds are raised) or mail scan. Customer email approval cannot be turned off while the deployment locks it. |
| `platform_set_scanning` | Pauses or resumes scanning. Saved work stays queued while paused. |
| `platform_list_templates` | **Read**, `platform.read`. The email and SMS templates in full, with which one is in use for each channel and its version. |
| `platform_save_template` | Adds a template or saves a new version of one, under the version that was read. Making it the one in use switches off the other templates of that channel. Only content prepared later follows it; saving sends nothing. |
