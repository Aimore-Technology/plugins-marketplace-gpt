# Aimore GPT Plugin Marketplace

Private marketplace containing `eightdegrees-sales-workflow` 0.1.30: eight workflow skills plus one command entry derived from the current EightDegrees P0 workflow. Shared business rules are identical across the Claude and GPT editions; manifests and runtime guidance differ.

For a local ChatGPT/Codex marketplace, clone this private repository, open the checkout in the desktop host and use its plugin directory to install the listed plugin. With a compatible Codex CLI:

```bash
codex plugin marketplace add /absolute/path/to/plugins-marketplace-gpt
codex plugin add eightdegrees-sales-workflow@aimore-gpt-marketplace
```

A GitHub push does not save a plugin into your ChatGPT account or publish it to OpenAI's public directory. The ZIP is also suitable for the supported private plugin-creation/upload workflow; that account operation is separate. This repository contains no registered app IDs or MCP endpoints. Connect customer services separately and verify their tools in the target host.

## Package and check

Requires Python 3.11+; validation dependencies are pinned in `requirements-dev.txt`.

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/check-marketplace.py
python3 scripts/package.py --output-dir dist
```

`dist/` contains one plugin ZIP plus a SHA-256 file. It excludes the marketplace and development tooling. See [plugin instructions](plugins/eightdegrees-sales-workflow/README.md), [release record](docs/release-0.1.30.md) and [pilot acceptance](plugins/eightdegrees-sales-workflow/references/pilot-acceptance.md).

This is a skills-only distribution. It adds no server, secret, customer data, account authorization, actual schedule or automatic send. Readiness must be established in the customer's own environment. Real samples and test logs stay in customer accounts.

Operator identity is configured at initialization; names, reminder destinations and approval ownership are not fixed. Dropbox remains the project-material source. See [operator setup and upgrade](plugins/eightdegrees-sales-workflow/references/operator-setup.md).

## Short commands

Use `@eightdegrees-sales-workflow init`, `start`, `stop`, `add-communication`, `run-auto`, `report`, or `reply-draft` with the plugin enabled/selected. See [command quickstart](plugins/eightdegrees-sales-workflow/references/commands.md) for inputs, boundaries and native Claude equivalents.

## Missing-data input

Open Aimore/Today for review, missing information, attention and waiting lists; each original task links to its dedicated ordinary input page under Actions. Fill the requested fields and check the named submission to-do. Automatic tasks are validated on the next authorized scan; Submitted manually initiated communication decisions resume through the same queue, without another command. Technical properties remain on the canonical PendingTasks record. Validation, content review and send approval remain separate. On first init, choose Chinese or English for workspace text; the saved choice is reused. See [input contract](plugins/eightdegrees-sales-workflow/references/pending-input.md).

## Mail recovery and task clarity

Garbled mail suspends fact extraction until the same authorized MIME source is strictly decoded or handed to manual recovery. The offline Python 3 helper has no network/send capability and does not repair the upstream connector. See [mail decoding](plugins/eightdegrees-sales-workflow/references/mail-decoding.md). Source identity uses exact stored fields rather than Notion display Markdown; task pages show one current state/version, original links and missing dependencies.

## Periodic scan controls

`@eightdegrees-sales-workflow start` creates/reuses one native 30-minute (20-minute optional) approved-work task; `stop` deletes it. Exact host cadence and task readback are required. Installation/init create no schedules. Native ticks may execute valid approved Automatic steps; public run-auto handles independently approved Automatic work and manually initiated communication submissions also resume through the queue. Explicit no-send requests remain restricted. Unsupported native scheduling/deletion is reported explicitly. See [schedule lifecycle](plugins/eightdegrees-sales-workflow/references/scheduling.md).

## Shared queue and standing notification authority

run-auto chains ready work across authorized sources and current Notion submissions; no extra continue command is required. Factual SMS notifications default to enabled standing authority and do not need individual content/send review. Email/CRM review, current stop/window/count/channel/attempt checks and explicit existing disable/revocation remain. Run explicit init after upgrade to register the additive ScheduledWork category and actual policy bindings; it creates no native task.

## Scan timing defaults

New installs use a 30-minute scan interval; choose the optional faster mode with
`@eightdegrees-sales-workflow start interval_minutes=20`. An unqualified start
keeps a supported saved choice. Each cycle has a 15-minute soft budget including
a 2-minute publication reserve; stop admitting new phases at minute 13 and
preserve unfinished work for the next tick. Existing explicit customer budgets
are preserved until deliberate init upgrade; plugin installation never changes
a live native task. Configure/update the same owned task through explicit start
and verify its actual cadence.
