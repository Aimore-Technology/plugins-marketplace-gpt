---
name: eightdegrees-automation-admin
description: Maintain the 8Degrees automation flows in Activepieces through the workbench's administration MCP connection (tools named ap_*, reached at /portal/mcp/admin). Use when a native flow step — a prompt, code step or setting of init, add-communication, reply-draft, report, run-auto, material-index or sms-notifications — must be read, compared, changed, validated or published, or when a flow run must be inspected. Internal maintenance only; not for daily sales work, which uses the business tools (platform_*).
---

# 8Degrees automation administration

The administration connection forwards to the Activepieces MCP server of the 8Degrees project under the signed-in administrator's own Activepieces grant. There is no review, no versioning and no duplicate-send protection from the workbench here: a published change takes effect on the next minute's scan, for real customers. Work slowly and leave evidence.

Deploying the Portal does **not** update the native flows. A change to a prompt or code step under `workflows/activepieces/` in the Portal repository reaches the running flow only when it is written into Activepieces, through this connection or the repository's `scripts/plan-activepieces-*.py`.

## What the connection allows

- **Read** (always): `ap_list_flows`, `ap_flow_structure`, `ap_read_step_code`, `ap_read_step_settings`, `ap_list_runs`, `ap_get_run`, `ap_list_connections`, `ap_list_ai_models`, `ap_list_tables`, `ap_find_records`, `ap_get_piece_props`, `ap_research_pieces`, `ap_resolve_property_chain`, `ap_resolve_property_options`, `ap_setup_guide`, `ap_validate_flow`, `ap_validate_step_config`.
- **Change a flow**, only the workbench's seven flows and only when the call names `flowId`: `ap_update_step`, `ap_add_step`, `ap_delete_step`, `ap_add_branch`, `ap_update_branch`, `ap_delete_branch`, `ap_update_trigger`, `ap_manage_notes`, `ap_lock_and_publish`, `ap_change_flow_status`.
- **Refused**: running actions or tests (`ap_run_action`, `ap_test_step`, `ap_test_flow`), retrying runs (`ap_retry_run`, it can send again), creating, copying, renaming or deleting flows, and writing tables or records. Do not look for another way to do these.

Every call is audited (time, person, assistant, tool, flow, outcome; never the arguments). `tool_not_allowed` or `flow_not_allowed` means the policy refused it. `reauthorization_required` means the administrator must sign in to the workbench in the browser again.

## The flows

| Flow | Job |
| --- | --- |
| `run-auto` | The one-minute scan: finds new mail and due work, chains the other flows, executes approved tasks, hands customer SMS to the phone gateway. |
| `reply-draft` | Prepares a customer reply from cached materials, validates its language and facts, freezes it for review. |
| `add-communication` | Turns a pasted or referenced communication into a CRM Note for review. |
| `report` | Builds the daily report. |
| `init` | Workspace initialization. |
| `material-index` | Indexes project materials from Dropbox, separately from replies. |
| `sms-notifications` | Hands internal and customer SMS to the gateway. |

## How to change a step

1. **Agree the change.** Name the flow, the step and the exact new text with the person who asked. A change to a customer-facing prompt or validation needs their explicit go-ahead to publish.
2. **Snapshot.** `ap_list_flows` to get the flow ID and published version; `ap_flow_structure`, then `ap_read_step_code` / `ap_read_step_settings` for every step you will touch. Keep the exact text you read; it is your rollback.
3. **Compare with the source.** If the change comes from the Portal repository, check that the step you read matches what the repository expects as the "before" state. If it does not, stop: someone changed the live flow, and overwriting it loses their change.
4. **Write to the draft.** `ap_update_step` (or the branch/step tools) writes the flow's draft, not the published version. Change only the steps you agreed.
5. **Check the draft.** Read the changed steps back and compare them character for character with the intended text. Confirm the step count and order did not change unless that was the point. `ap_validate_flow` must report every step valid.
6. **Publish only with the go-ahead.** `ap_lock_and_publish`. Then read the flow again: it must still be enabled, the published version must have changed, and the published steps must equal the intended text.
7. **Watch the next runs.** `ap_list_runs` for the flow (and `run-auto`): the next few runs should succeed. Open a failed run with `ap_get_run`.
8. **Record it.** Report the flow, steps, old and new published version, the checks above and any run IDs. Save the snapshot and the new text with the change record in the repository (the project keeps them under `artifacts/`). Never put credentials or customer content in the record.

To roll back, write the snapshot text back the same way and publish.

## Rules

- Never pause, disable or re-enable a flow (`ap_change_flow_status`) without an explicit instruction; an operator's explicit scan stop must be preserved.
- Never touch flows outside the seven listed, even if Activepieces shows them.
- Do not read connection secrets; `ap_list_connections` shows names and status only, which is all you need.
- Run data can contain customer emails and phone numbers. Read only what the diagnosis needs and do not copy it elsewhere.
- Disconnect the administration connector when the maintenance is done.
