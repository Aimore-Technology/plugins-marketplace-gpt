# Release 0.1.0-beta.1: 8Degrees Workbench MCP plugins (2026-11-23)

Released with workbench beta 01 (Portal tag `v0.1.0-beta.1`). It adds two plugins that work through the workbench's MCP servers instead of running workflow steps locally. The skills-only `eightdegrees-sales-workflow` plugin is unchanged and remains listed for existing installs; new installs should use `eightdegrees-workbench`. Update 2026-11-27: `eightdegrees-sales-workflow` was taken out of the marketplace and moved to `legacy/eightdegrees-sales-workflow-0.2.3`; the legacy checks named below were removed from `scripts/check-marketplace.py` with it.

| Plugin | Who | MCP server | Listed |
| --- | --- | --- | --- |
| `eightdegrees-workbench` | Operators and their assistants | `https://act.demo.starfield.com.au/portal/mcp/platform` (61 business tools, OAuth) | Yes |
| `eightdegrees-automation-admin` | Aimore maintenance only | `https://act.demo.starfield.com.au/portal/mcp/admin` (allowlisted Activepieces tools, portal administrators) | No, under `internal/`; built with `scripts/package.py --internal` |

Each plugin is one skill plus one `.mcp.json`. They contain no credentials, scripts or customer data.

## Checks

- `scripts/check-marketplace.py` checks the MCP plugins separately from the legacy plugin: manifest, SemVer with an optional `-beta.N`, exactly the expected skill, frontmatter, one plain HTTPS server on the expected path with no headers, and nothing but Markdown and JSON. The legacy checks are unchanged.
- The unit tests give the same result as before the change (1 failure and 45 errors in each repository, present before this release; not investigated).
- In a throwaway Codex home, `codex plugin marketplace add` and `codex plugin add eightdegrees-workbench@aimore-gpt-marketplace` installed the plugin, and `codex mcp list` showed the `eightdegrees` server from its `.mcp.json` as enabled and not yet signed in.
- Not tried: signing in to the Demo from Codex, and ChatGPT.

