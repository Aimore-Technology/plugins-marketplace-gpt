---
name: eightdegrees-sales-reply
description: "Activepieces client entry for the EightDegrees reply-draft command. Submit an inquiry for a grounded draft and workbench review."
---

# reply-draft client entry

Apply the [client protocol](../../references/activepieces-client.md) and the `reply-draft` route in [commands.json](../../references/commands.json). This entry's policy is `draft-only`. It is a request adapter, not a business executor.

Collect the original Gmail message ID, exact projectKey and exact registered lot when the project catalog has lots. Supplied captured text may accompany the message ID; it does not remove the thread requirement. Present known catalog choices when available. The saved projects object contains optional overrides, not the full automatic source index; the backend resolves the supplied exact project/lot against its cached authorized library. Do not ask the user to register material paths or rebuild/import a catalog when a project is absent from the saved overrides. If the intended project/lot is ambiguous, ask only for that identity. Do not infer a project/lot from a vague match, promise prices/delivery, fetch a second set of materials or prepare another chat draft. Activepieces performs cache lookup, grounded drafting and draft publication. Return ReviewRequired with the original workbench review link only after the exact owner response is observed. The flow stops at review; the scheduled backend handles any later valid approval.

Use `activepieces_client.py plan` to validate the request against verified workspace and flow captures. Missing input or a disabled/unpublished/ambiguous flow produces no executable call. Execute only the planned MCP call once, then use bounded result lookup and `observe` to match the transport ID and flow ID. Do not silently switch operation, retry an uncertain call, inspect unrelated service data or use old workflow helpers as a fallback. Return only the owner's actual result and one appropriate next action.
