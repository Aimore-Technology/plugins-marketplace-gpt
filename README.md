# Aimore GPT Plugin Marketplace

Private marketplace for the 8Degrees sales workbench. It lists one plugin.

| Plugin | Version | What it does |
| --- | --- | --- |
| `eightdegrees-workbench` | 0.1.0-beta.1 | Connects an assistant to the workbench's business MCP server and adds one skill for using its tools. |

See the [plugin instructions](plugins/eightdegrees-workbench/README.md) and the [release record](docs/release-0.1.0-beta.1.md).

## Local install

Register this checkout and install the plugin using the host CLI:

```bash
codex plugin marketplace add /absolute/path/to/plugins-marketplace-gpt
codex plugin add eightdegrees-workbench@aimore-gpt-marketplace
```

The plugin signs in to the workbench with OAuth and holds no credentials. Do not modify the host cache manually. A local install is separate from a shared marketplace push or account/public publication.

## Not listed

- `internal/eightdegrees-automation-admin` is for Aimore maintenance only. It is built on request with `scripts/package.py --internal`.
- `legacy/eightdegrees-sales-workflow-0.2.3` is the earlier client for published Activepieces flows, and `legacy/eightdegrees-sales-workflow-0.1.58` the skills-only package before it. `eightdegrees-sales-workflow` was taken out of the marketplace on 2026-11-27 because it works outside the workbench's business MCP server. See [legacy/README.md](legacy/README.md). A host that still has it installed keeps its copy until the plugin is removed there.

## Validation and packaging

Requires Python 3.11+; validation dependencies are pinned in `requirements-dev.txt`.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/check-marketplace.py
python3 scripts/package.py --output-dir dist
```

`scripts/check-marketplace.py` accepts only MCP plugins in the catalog: each is one skill plus one `.mcp.json` naming a plain HTTPS server, with nothing but Markdown and JSON. It also checks every file in the repository, including `legacy/`, for valid JSON, English text, credential patterns and stray runtime wiring files.

`scripts/package.py` writes one ZIP and a SHA-256 file per listed plugin to `dist/`. The unit tests exercise the helper scripts of the two retired packages.

`docs/` holds the release records. Records before 0.1.0-beta.1 describe the retired packages and name the old path, `plugins/eightdegrees-sales-workflow`.
