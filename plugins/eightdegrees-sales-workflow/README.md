# EightDegrees Sales Workflow

Version 0.1.3. Seven workflow skills plus one command entry, with English-only instructions for the EightDegrees pilot. Start with `eightdegrees-initialization`; shared rules live in `references/operating-contract.md`. Actual customer settings belong in `Aimore/Dashboard`, not in this installation directory.

## Skills

| Skill | Use |
| --- | --- |
| eightdegrees-sales-workflow | Route the five short commands to existing workflows. |
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

Install the package, run initialization in the customer account, supply actual scope/account references, then follow `references/pilot-acceptance.md`. Missing connectors do not appear by installing skills. Every customer send still requires exact-version/window approval. Package checks do not prove channel readiness or business acceptance.

Operator identity is configured at initialization; names, reminder destinations and approval ownership are not fixed. Dropbox remains the project-material source. See [operator setup and upgrade](references/operator-setup.md).

## Short commands

Use `@eightdegrees-sales-workflow init`, `add-communication`, `run-auto`, `report`, or `reply-draft` with the plugin enabled/selected. See [command quickstart](references/commands.md) for inputs, boundaries and native Claude equivalents.
