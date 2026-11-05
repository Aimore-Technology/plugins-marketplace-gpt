# Aimore GPT Plugin Marketplace

Private marketplace containing EightDegrees Sales Workflow 0.2.0, a lightweight client for published Activepieces flows. The public commands are init, add-communication, reply-draft and report. Activepieces owns business execution, scheduling and queue/approval state; the plugin collects input, submits one request and shows its correlated result.

## Local install

Register this checkout and install the existing plugin identity using the host CLI:

```bash
codex plugin marketplace add /absolute/path/to/plugins-marketplace-gpt
codex plugin add eightdegrees-sales-workflow@aimore-gpt-marketplace
```

The host needs its already authorized Activepieces MCP connection. The package introduces no extra OAuth connection, server, credentials or customer-specific flow IDs. Do not modify the host cache manually. A local install is separate from a shared marketplace push or account/public publication.

## Commands

- init: collect explicit workspace configuration and return actual readiness.
- add-communication: submit the supplied communication/source for one Notion review.
- reply-draft: submit the actual inquiry message and exact project/lot for one draft review.
- report: show the backend report without running business actions.

start, stop and run-auto are not client commands. The backend uses native scheduling; pause/resume on its Activepieces page. Initialization remains required before business intake. Review-required is not CRM completion or a customer send. This update does not complete missing backend capabilities or real-customer acceptance.

## Validation and packaging

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/check-marketplace.py
python3 scripts/package.py --output-dir dist
```

The small installable payload is under plugins/eightdegrees-sales-workflow. Original 0.1.58 execution code is retained under legacy/eightdegrees-sales-workflow-0.1.58 and excluded from release ZIPs. Existing tests still cover that archive; new request/result boundary tests cover the active client. See [client instructions](plugins/eightdegrees-sales-workflow/README.md) and [release record](docs/release-0.2.0.md).
