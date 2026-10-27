# 0.1.1 configurable operator

Replace the named pilot operator throughout all seven English skills and shared workflow references. Initialization now records a stable operator ID, display name, internal email destination and optional verified SMS number. Required identity values have no packaged default. Customer Dropbox, Gmail and Notion account references remain configurable; Dropbox stays the material source.

Read `references/operator-setup.md` before an explicit legacy settings upgrade. New settings use schema version 2; timing/business defaults remain pilot-v1. Generic input/waiting-state/channel names replace person-specific names. Preserve actual existing account/page/task IDs and historical actors; map legacy properties rather than duplicating them. Different operators/sender identities cannot inherit pending approval. Unknown external attempts still require reconciliation.

This is still a single-operator Skill Pack using the host's existing authentication, not a multi-user identity system. English packaging, manual P0-A, explicit exact-version send approvals, bounded follow-ups and no-deliberate-redaction rules remain unchanged. No customer settings are changed by installing the package.

Verification: run the repository gate and archive builder; compare shared payloads and validate all skill frontmatter. Operator switching, legacy migration and actual reminder/approval behavior have acceptance scenarios in `references/pilot-acceptance.md`; no live account changes or sends are performed by packaging. Native Claude validation remains unavailable in this environment.
