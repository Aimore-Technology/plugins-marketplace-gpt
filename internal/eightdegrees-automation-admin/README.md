# 8Degrees Automation Admin (internal, beta 01)

For Aimore's own maintenance team only. It is not listed in the customer marketplace and must not be given to customers. Version 0.1.0-beta.1.

## What it contains

- `.mcp.json`: the administration MCP server of the Demo workbench, `https://act.demo.starfield.com.au/portal/mcp/admin`. It forwards to Activepieces under your own sign-in, with a tool allowlist limited to the seven workbench flows. Only a portal administrator (`portal-admin` or `admin`) can approve the connection, and it carries the single permission `platform.admin`.
- `skills/eightdegrees-automation-admin`: how to change a flow step safely: snapshot, compare with the repository, write to the draft, check, publish only with a go-ahead, watch the next runs, record the change.

The administration endpoint exists only where the deployment sets `PlatformMcp:AdminEnabled=true`; today that is the Demo. Changes published here act on real customers at the next one-minute scan, without the workbench's review. Disconnect when the maintenance is done.

## Install

Package it with `python3 scripts/package.py --internal` and install the folder with the Codex CLI, or add the server address as a custom MCP connector.
