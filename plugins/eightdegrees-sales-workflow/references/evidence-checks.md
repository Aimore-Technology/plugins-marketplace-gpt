# Offline workflow evidence checks

Use [workflow_checks.py](../scripts/workflow_checks.py) on actual tool captures/canonical task data when Python 3 is available. It has no connector, network, dispatcher, approval or write capability. It does not execute the workflow or replace factual/authorization checks. If unavailable, perform the same checks manually and label that limited evidence; never claim a script ran.

```text
python3 <plugin>/scripts/workflow_checks.py tool-result --input <original-mcp-result.json>
python3 <plugin>/scripts/workflow_checks.py notion-links --input <actual-notion-fetch.json>
python3 <plugin>/scripts/workflow_checks.py notion-links --input <saved-page.md> --input-format markdown
python3 <plugin>/scripts/workflow_checks.py resume-task --input <canonical-task.json> --policy one-cycle-approved-work
```

Store authorized captures outside the source repository. Inputs must be the actual original result/saved page/canonical task, not a reconstructed successful response. Preserve both text and structuredContent layers in tool-result captures.

For publication regressions, use [Notion publication](notion-publishing.md) and its offline `notion_checks.py section-patch`, `preview` and `report-write` operations. They plan exact owned-section updates, verify saved embed/file evidence and compare proposed/captured writes to a frozen report target registry. They cannot authorize, execute or host-enforce a workflow. Run link checks before publishing too: bare URLs are examined because Notion may auto-link punctuation into their targets.

## Results

- tool-result: Accepted is tool evidence, not delivery; Unclassified requires interpretation using the actual tool contract. Error preserves the specific upstream code/status plus wrapper diagnostics. In particular WORKFLOW_API_NOT_ENABLED_FOR_LOCATION is a capability unavailable to that location, even when a wrapper says INVALID_ARGUMENT. The helper never authorizes automatic retries; read retry rules and unknown-write reconciliation still apply.
- notion-links: NeedsCorrection means suspicious visible targets need literal presentation or exact verified URL evidence. It examines tables, prose, native mention/media references and history across the supplied text, excluding literal code. It catches file-name hosts, encoded non-ASCII hosts/punctuation, malformed app.notion.com page paths and local-file links unsuitable for Notion. For a real verified file-like domain, pass a JSON list of exact original URLs with `--allowed-urls`; do not allow an entire domain or a guessed URL to hide a finding.
- ClearForCheckedPatterns is only a static pattern result, not a claim that all links work, permissions are granted or the Notion UI renders correctly. Record page ID, fetched cutoff, examined links, exceptions and any truncated/unknown blocks separately. A failed fetch is not an empty clean page. Repairing project file cells does not establish that script paths or historical tables are clean.
- resume-task: NeedsCorrection blocks missing/inconsistent owner/step/binding; Deferred preserves terminal state, Manual boundaries and shortcut limits. Default `--phase execute` checks business routing; EligibleForOwnerCheck never grants approval. `--phase observe` checks only input/choice validation and recording, returning EligibleForInputCheck. A permitted scan may record an Automatic send choice while execute remains Deferred. report-only/draft-only cannot consume SendApproval; Manual forms stay excluded from scans in both phases. Never change policy to force eligibility. Original action/approval/stop/attempt checks remain mandatory. `--explicit-continue` requires an actual operator continuation.

CLI exit code 2 denotes Error/NeedsCorrection; valid Deferred and EligibleForOwnerCheck return 0 with different statuses. Always inspect the status, not exit code alone. Only a separately authorized owner-workflow invocation may use that policy; changing a helper argument cannot widen any command's scope.

For saved Notion pages use the typed page-links check in [publication validation](publication-validation.md); database/view documentation is excluded rather than reported as a clean page. The same reference defines schema-values, task-display and completion-gate. Check actual process exit and structured result before completion; report-write requires full current gate evidence for final completion/Success.

## Fact and native schedule checks

Use `fact_checks.py --input <actual proposed facts>` before source/proposal or
persona writes. Unknown/null is distinct from confirmed no/false; its schema and
limits are in [customer facts](customer-facts.md).

For new forms use workflow_checks.py resume-task with --phase register. The
ValidResumeRoute result is metadata-only; it cannot satisfy completion-gate's
executing route evidence. For start/stop use schedule_checks.py plan, then fresh
native results with verify; scheduled ticks use guard. See [scheduling](scheduling.md).
All helpers are offline: no job creation/deletion or automatic host enforcement.

## Native execution and actual result checks

A real native tick supplies schedule_checks guard evidence before resume-task
with --policy scheduled-approved-work --schedule-guard <current-guard.json>.
Public run-auto uses one-cycle-approved-work for independently approved Automatic steps. Explicit no-send invocations retain one-cycle-no-customer-send. A manually pasted
marker cannot create native context or authorize a send.

Use [outcome checks](../scripts/outcome_checks.py) task/project/verify/counts for
actual state conflicts, current result projections and deduplicated known totals.
Use [send receipt checks](../scripts/send_receipt.py) render/reconcile/verify
for the final send package's deterministic CRM receipt. Required field mappings
and current readbacks are in [outcome state](outcome-state.md) and
[send receipts](send-receipts.md). Bind successful outcome/crm-receipt results to
the original task/version in owner completion; these scripts call no provider.

## Owner preparation

Use [execution preflight](execution-preflight.md) prepare/ready before dependent
owner work. It combines actual fact/schema/transport prechecks, derives role
coverage and verifies an exact persisted plan. Exit 0 alone is insufficient:
require PreflightPrepared or ExecutionPlanReady at the corresponding phase.
These checks neither execute providers nor prove historical call order.
