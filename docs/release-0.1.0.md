# 0.1.0 pilot package

## Change and review path

Package the current approved pilot description as seven English skills, with shared operational rules, Notion model, machine-readable defaults and acceptance cases. Start review at `plugins/eightdegrees-sales-workflow/README.md`, then `references/operating-contract.md` and the specific skill. Provenance and source hash are in `source-provenance.json`; the private Notion source is not a runtime dependency.

The user requested direct delivery to this repository for pilot testing. This release initializes its marketplace without changing repository visibility or customer environments. Versioned Git commits are the change record. No public-directory submission or account installation is performed by a push.

## Boundaries and implementation choices

P0-A stays manually initiated/resumed. One CRM Notes append owns each approved communication/version; persona changes share that note. Five PendingTasks categories are views of one database. Manual+AI follow-ups share the two-message cap. Approval binds exact payload and send window; unknown results require reconciliation. Notion is not a concurrency lock or immutable audit store. Account/folder values must be supplied by the customer, never invented.

The Claude edition uses verified Cowork scheduling; the GPT edition defaults to on-demand execution and cannot claim Cowork access. Both require separately authorized customer connectors; no endpoints, credentials, customer material or executable lifecycle hooks are bundled. These skills describe tool-driven operations, not an independent connector implementation. Missing send/upload/view/scheduling capabilities stay incomplete or manual, not simulated as successful.

All runtime instructions are English and shared details are loaded progressively. The original Chinese Description remains in Notion; no full duplicate is placed in the installed plugin.

## Validation and limits

Run the local marketplace gate and skill frontmatter validation, inspect archives and relative references, and compare common payload hashes across editions. GPT manifest validation uses the cached Agent Plugins 1.0 JSON schema (`schemas-plugin.json`). The Claude check is the repository's restricted skills-only structural profile, not the complete native Claude validator. Native `claude plugin validate` must be reported separately when available.

Required live checks are in `references/pilot-acceptance.md`. File/schema checks cannot verify actual auth, labels, CRM writes, HTML previews, sender number, received messages or scheduling precision. Do not mark those passed from packaging alone. No actual business data is placed in this repository, and runtime no-redaction preferences remain unchanged.

## Local verification record (2026-10-27)

- Marketplace/payload gate: passed for seven skills in this edition.
- Skill Creator frontmatter validation: passed for each of the seven skills.
- Cross-platform comparison: all 14 shared skill/reference files are byte-identical; only runtime guidance and manifests differ.
- ZIP inventory, member bytes and CRC: passed; the archive contains 17 plugin files with no marketplace or customer data.
- Native Claude validation: not run; Claude CLI is not installed in the build environment.
- Account installation, connector authorization, scheduled execution and live business acceptance: not performed by packaging.
