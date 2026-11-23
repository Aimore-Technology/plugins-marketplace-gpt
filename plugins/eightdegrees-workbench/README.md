# 8Degrees Workbench (beta 01)

Connects your assistant to the 8Degrees sales workbench through its business MCP server and teaches it how to work there safely. Version 0.1.0-beta.1, released with workbench beta 01 on 2026-11-23.

## What it contains

- `.mcp.json`: the business MCP server of the Demo workbench, `https://act.demo.starfield.com.au/portal/mcp/platform`. It signs in with OAuth through the workbench; the plugin holds no credentials.
- `skills/eightdegrees-workbench`: how to use the 61 `platform_*` tools: starting a session, the review and approval rules, the reply-language and SMS rules, common jobs, permissions and errors. `references/tools.md` lists every tool by area.

## Connecting

The first tool call opens the workbench sign-in in the browser. On the **Connect an assistant** page tick what the assistant may do and choose **Allow**:

| Permission | Lets the assistant |
| --- | --- |
| `platform.read` | Read work, tasks, materials, knowledge, runs and reports. Always included. |
| `platform.submit` | Prepare replies, record communications, supply facts, commitments, knowledge proposals, run a cycle, send the brief. |
| `platform.review` | Edit drafts; approve, return or cancel tasks. |
| `platform.contacts` | Search and resolve contacts, people types, SMS opt-outs, stop or reconcile SMS. |
| `platform.configure` | Settings, scanning, templates, training practices, knowledge Projects. |
| `platform.notify` | Send and withdraw its own workbench notifications. |

To change permissions, disconnect in the workbench (**Settings → Assistant connections**) and connect again. If the assistant reports `reauthorization_required`, sign in to the workbench in the browser again.

## Another workbench

The address in `.mcp.json` is the Demo. For another deployment, replace the host and keep the path `/portal/mcp/platform`. The customer delivery server does not run a version with Platform MCP yet.

## Limits

Nothing reaches a customer without an operator's approval of that exact version; customer email approval stays locked on during the beta. Opt-outs are lifted, the workspace is set up and provider connections are authorized in the browser only.

## Install (Codex)

```bash
codex plugin marketplace add /absolute/path/to/plugins-marketplace-gpt
codex plugin add eightdegrees-workbench@aimore-gpt-marketplace
```

For ChatGPT, add the server address as a custom MCP connector that signs in with OAuth, and give the assistant the skill text. ChatGPT has not been tested against the workbench.
