# Retired packages

Neither package is listed in the marketplace, and `scripts/package.py` builds neither. Do not install them for current work; use `eightdegrees-workbench`, which works through the workbench's business MCP server.

`scripts/check-marketplace.py` no longer checks their command routes, skill inventory and client boundary. The repository-wide rules still cover their files: valid JSON, English text only, no credential patterns, no runtime wiring files. A host that already has `eightdegrees-sales-workflow` installed keeps its copy until the plugin is removed there.

## eightdegrees-sales-workflow-0.2.3

The Activepieces client as last released, taken out of the marketplace on 2026-11-27 and kept unchanged. It submits `init`, `add-communication`, `reply-draft` and `report` to published Activepieces flows through the host's Activepieces MCP connection. It does not use the workbench's business MCP server, so it has none of the tools added since: review and approval by version, contacts, commitments, knowledge, notifications. `tests/test_activepieces_client.py` still runs its offline request client.

The root README described it at retirement as follows.

> Private marketplace containing 8Degrees Sales Workflow 0.2.3, a lightweight client for published Activepieces flows. The public commands are init, add-communication, reply-draft and report. Activepieces owns business execution, scheduling and queue/approval state.
>
> start, stop and run-auto are not client commands. The backend uses native scheduling; pause/resume on its Activepieces page. Initialization remains required before business intake. Review-required is not CRM completion or a customer send.

See its [client instructions](eightdegrees-sales-workflow-0.2.3/README.md) and [release record](../docs/release-0.2.3.md).

## eightdegrees-sales-workflow-0.1.58

The unchanged original package, archived when 0.2.0 switched the installed plugin to an Activepieces client. Legacy unit tests continue to exercise its original deterministic helpers; they are regression evidence for the archive, not proof of current backend parity.
