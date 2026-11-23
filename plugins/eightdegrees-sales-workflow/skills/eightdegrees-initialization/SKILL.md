---
name: eightdegrees-initialization
description: "Activepieces client entry for the EightDegrees init command. Collect and submit workspace configuration."
---

# init client entry

Apply the [client protocol](../../references/activepieces-client.md) and the `init` route in [commands.json](../../references/commands.json). This entry's policy is `setup-only`. It is a request adapter, not a business executor.

Collect the actual operator email/name/CRM user ID and CRM location, an explicit zh-CN or en workspace language, the connected Gmail account with scope all-new and an optional starting instant (defaults to now), authorized Dropbox source folders; manual project paths/lots are optional overrides. Scan all new incoming emails and let the backend AI classify inquiries; do not ask for sender lists, recipient filters or pre-applied labels. Spam, trash, sent mail and drafts are excluded. Do not ask the user to build or import a project catalog. The backend discovers projects and current documents, caches source revisions and retries incomplete reads automatically. The Portal workspace setup can load the connected Gmail profile, LeadConnector workspace/member choices and Dropbox project suggestions, with manual adjustment. Existing saved values may be reused; do not invent missing IDs or infer permanent language from the conversation. Portal stores review records and reports; no Notion configuration is required. The backend merges configuration and determines initialization readiness. Report any returned missing fields as unfinished setup. Completion unlocks the already configured native schedule; this client does not activate or edit it.

Use `activepieces_client.py plan` to validate the request against verified workspace and flow captures. Missing input or a disabled/unpublished/ambiguous flow produces no executable call. Execute only the planned MCP call once, then use bounded result lookup and `observe` to match the transport ID and flow ID. Do not silently switch operation, retry an uncertain call, inspect unrelated service data or use old workflow helpers as a fallback. Return only the owner's actual result and one appropriate next action.
