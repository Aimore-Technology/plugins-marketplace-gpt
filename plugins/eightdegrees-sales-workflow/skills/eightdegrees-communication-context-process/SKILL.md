---
name: eightdegrees-communication-context-process
description: "Activepieces client entry for the EightDegrees add-communication command. Submit customer communication for one Notion review."
---

# add-communication client entry

Apply the [client protocol](../../references/activepieces-client.md) and the `add-communication` route in [commands.json](../../references/commands.json). This entry's policy is `manual-review`. It is a request adapter, not a business executor.

For readable supplied text, collect the customer email or verified E.164 phone and submit source.text. Do not retrieve mailbox or project material just because it is mentioned. A supplied actual Gmail message ID can supply sender identity inside the owner. An authorized Dropbox file uses source.filePath within saved roots. A Gmail thread URL is not a message ID; collect the correct source instead of guessing. Preserve original communication time and provenance when available. A repeated source continues its existing owner review; do not retry a failed or unknown business write. The owner performs semantic extraction, exact matching and Notes rendering; this client only submits the request.

Use `activepieces_client.py plan` to validate the request against verified workspace and flow captures. Missing input or a disabled/unpublished/ambiguous flow produces no executable call. Execute only the planned MCP call once, then use bounded result lookup and `observe` to match the transport ID and flow ID. Do not silently switch operation, retry an uncertain call, inspect unrelated service data or use old workflow helpers as a fallback. Return only the owner's actual result and one appropriate next action.
