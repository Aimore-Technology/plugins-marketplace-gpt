# Aimore GPT Plugin Marketplace

Private marketplace containing `eightdegrees-sales-workflow` 0.1.44: eight workflow skills plus one command entry derived from the current EightDegrees P0 workflow. Shared business rules are identical across the Claude and GPT editions; manifests and runtime guidance differ.

Current 0.1.44 behavior: start/stop controls the scanning switch; explicit start registers the existing native task configuration when readable. Every native wake loads current scheduled rules, recovers durable backlog independently of new input, and records timer/guard/business progress separately. No duplicate tasks are created.
A stopped run-auto reads only settings and exits without discovery or logs.
No command creates/updates/pauses/deletes native automations. Older release
sections below describe historical behavior and are superseded for start/stop.


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

`dist/` contains one plugin ZIP plus a SHA-256 file. It excludes the marketplace and development tooling. See [plugin instructions](plugins/eightdegrees-sales-workflow/README.md), [release record](docs/release-0.1.44.md) and [pilot acceptance](plugins/eightdegrees-sales-workflow/references/pilot-acceptance.md).

This is a skills-only distribution. It adds no server, secret, customer data, account authorization, actual schedule or automatic send. Readiness must be established in the customer's own environment. Real samples and test logs stay in customer accounts.

Operator identity is configured at initialization; names, reminder destinations and approval ownership are not fixed. Dropbox remains the project-material source. See [operator setup and upgrade](plugins/eightdegrees-sales-workflow/references/operator-setup.md).

## Short commands

Use `@eightdegrees-sales-workflow init`, `start`, `stop`, `add-communication`, `run-auto`, `report`, or `reply-draft` with the plugin enabled/selected. See [command quickstart](plugins/eightdegrees-sales-workflow/references/commands.md) for inputs, boundaries and native Claude equivalents.

## Missing-data input

Open Aimore/Today for review, missing information, attention and waiting lists; each original task links to its dedicated ordinary input page under Actions. Fill the requested fields and check the named submission to-do. Automatic tasks are validated on the next authorized scan; Submitted manually initiated communication decisions resume through the same queue, without another command. Technical properties remain on the canonical PendingTasks record. Validation, content review and send approval remain separate. On first init, choose Chinese or English for workspace text; the saved choice is reused. See [input contract](plugins/eightdegrees-sales-workflow/references/pending-input.md).

## Mail recovery and task clarity

Garbled mail suspends fact extraction until the same authorized MIME source is strictly decoded or handed to manual recovery. The offline Python 3 helper has no network/send capability and does not repair the upstream connector. See [mail decoding](plugins/eightdegrees-sales-workflow/references/mail-decoding.md). Source identity uses exact stored fields rather than Notion display Markdown; task pages show one current state/version, original links and missing dependencies.

## Periodic scan controls

`@eightdegrees-sales-workflow start` creates/reuses one local 30-minute (20-minute optional) approved-work task; `stop` deletes it. Exact host cadence and task readback are required. Installation/init create no schedules. Native ticks may execute valid approved Automatic steps; public run-auto handles independently approved Automatic work and manually initiated communication submissions also resume through the queue. Explicit no-send requests remain restricted. Unsupported native scheduling/deletion is reported explicitly. See [schedule lifecycle](plugins/eightdegrees-sales-workflow/references/scheduling.md).

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

Dispatch completes on the original successful Gmail/AndroidSync acknowledgement.
No post-send status or receipt checks. Our Notion records and CRM writes remain
verified under [the provider boundary](plugins/eightdegrees-sales-workflow/references/provider-boundary.md).

## Event-driven work

run-auto now discovers changed or due input before loading business processing.
Quiet ticks exit immediately; submitted forms and due timers still wake work.
See [event discovery](plugins/eightdegrees-sales-workflow/references/event-discovery.md)
and [release 0.1.33](docs/release-0.1.33.md). Actual live idle time/token savings
remain to be measured after upgrade.

## Scoped SMS initiation fix

Version 0.1.34 consumes the saved explicit initiation of a new inquiry without
letting an unrelated closed project cycle suppress it. Old project/global stops,
Pause, expiry, unknown attempts and per-cycle limits remain. The original unsent
implementation-blocked stub can recover in place, without another email or CRM
receipt. See [release 0.1.34](docs/release-0.1.34.md).

## Short scans and successor handover

Version0.1.35 narrows discovery to active dependency/form watches, preserves raw
read errors and current run metadata, and avoids repeatedly charging a phase
estimate before dispatch. See [release0.1.35](docs/release-0.1.35.md). Original
Gmail/AndroidSync acceptance still ends dispatch; fresh send guards remain.

Version0.1.36 corrects Notion presentation-escaped run metadata readback;
see [the readback fix](docs/release-0.1.36.md). Saved originals are preserved.

Version0.1.37 gates sales preparation on durable source intake, preserves review bindings/current sections, synchronizes original source results and pins command recovery. See [the handover fix](docs/release-0.1.37.md).

Version0.1.38 preserves effective invocation restrictions, inquiry-level SMS limits and scoped queue barriers. Ordinary verified inquiries inherit standing SMS authority without re-init; missing inbound SMS is coverage metadata, not a send gate. See [the flow fixes](docs/release-0.1.38.md).

Version0.1.39 makes start/stop local-only: bind the selected computer and directory, verify actual local task readback and retain safe legacy cleanup. Installation/init does not create or enable a task. See [local scheduling](docs/release-0.1.44.md).

## Existing local tasks do not need management tools

0.1.40 separates schedule management from execution. A verified existing local
tick runs email-scanning with its current execution guard without requiring
automation_update or scheduler list/read/create/update/delete tools in that
conversation. Start/stop capability limits affect only those management actions.
Current per-task approval, stop and duplicate-effect guards remain required. Native identity/lifecycle and management checks are not execution gates. No job is created by
this update. See the packaged schedule-execution.md contract.

## Execute without a unique host/session

0.1.41 uses task-state-v2 for existing local ticks. No unique executor, assigned
conversation, privileged native invocation/host/thread/turn identity, global
activity listing or serialization proof is required. Local RunIds label logs
and recovery only. Legacy executor assignments are inert without init/rebinding.
Per-task approvals, stops, completed results and original pending/unknown attempts
remain checked. Native schedule target IDs remain for start/stop management;
this release creates no schedule and does not claim an atomic parallel lock.

0.1.44 makes business setup visible on every explicit init/upgrade: operator, mailbox labels/time scope, Dropbox allowlist, sender/signature, CRM/workspace and optional channels. Saved values are not newly confirmed consent. Missing or conflicting scopes are shown explicitly; setup audit adds no periodic execution gate.
