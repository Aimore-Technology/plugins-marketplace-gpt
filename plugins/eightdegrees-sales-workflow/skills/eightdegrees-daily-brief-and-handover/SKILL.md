---
name: eightdegrees-daily-brief-and-handover
description: "Activepieces client entry for the EightDegrees report command. Show the report returned by the report flow."
---

# report client entry

Apply the [client protocol](../../references/activepieces-client.md) and the `report` route in [commands.json](../../references/commands.json). This entry's policy is `report-only`. It is a request adapter, not a business executor.

Use an empty business payload. This command is permitted before initialization so the owner can show missing setup and queue coverage. Show the exact reportText returned by the backend, together with its actual report link when present. Preserve unknown/pending distinctions, business timezone and partial coverage. Do not paraphrase a failed run as an empty healthy queue, add counts or customer facts, scan mail, repair task state, write CRM, send notifications or invoke the scheduled scanner. If no correlated result is available yet, show in-progress status with the original request ID and stop rather than reading unrelated history.

Use `activepieces_client.py plan` to validate the request against verified workspace and flow captures. Missing input or a disabled/unpublished/ambiguous flow produces no executable call. Execute only the planned MCP call once, then use bounded result lookup and `observe` to match the transport ID and flow ID. Do not silently switch operation, retry an uncertain call, inspect unrelated service data or use old workflow helpers as a fallback. Return only the owner's actual result and one appropriate next action.
