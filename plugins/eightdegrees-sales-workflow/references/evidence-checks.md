# Offline workflow evidence checks

Use [workflow_checks.py](../scripts/workflow_checks.py) on actual tool captures/canonical task data when Python 3 is available. It has no connector, network, dispatcher, approval or write capability. It does not execute the workflow or replace factual/authorization checks. If unavailable, perform the same checks manually and label that limited evidence; never claim a script ran.

```text
python3 <plugin>/scripts/workflow_checks.py tool-result --input <original-mcp-result.json>
python3 <plugin>/scripts/workflow_checks.py notion-links --input <actual-notion-fetch.json>
python3 <plugin>/scripts/workflow_checks.py notion-links --input <saved-page.md> --input-format markdown
python3 <plugin>/scripts/workflow_checks.py resume-task --input <canonical-task.json> --policy one-cycle-no-customer-send
```

Store authorized captures outside the source repository. Inputs must be the actual original result/saved page/canonical task, not a reconstructed successful response. Preserve both text and structuredContent layers in tool-result captures.

For publication regressions, use [Notion publication](notion-publishing.md) and its offline `notion_checks.py section-patch`, `preview` and `report-write` operations. They plan exact owned-section updates, verify saved embed/file evidence and compare proposed/captured writes to a frozen report target registry. They cannot authorize, execute or host-enforce a workflow. Run link checks before publishing too: bare URLs are examined because Notion may auto-link punctuation into their targets.

## Results

- tool-result: Accepted is tool evidence, not delivery; Unclassified requires interpretation using the actual tool contract. Error preserves the specific upstream code/status plus wrapper diagnostics. In particular WORKFLOW_API_NOT_ENABLED_FOR_LOCATION is a capability unavailable to that location, even when a wrapper says INVALID_ARGUMENT. The helper never authorizes automatic retries; read retry rules and unknown-write reconciliation still apply.
- notion-links: NeedsCorrection means suspicious visible targets need literal presentation or exact verified URL evidence. It examines tables, prose, native mention/media references and history across the supplied text, excluding literal code. It catches file-name hosts, encoded non-ASCII hosts/punctuation, malformed app.notion.com page paths and local-file links unsuitable for Notion. For a real verified file-like domain, pass a JSON list of exact original URLs with `--allowed-urls`; do not allow an entire domain or a guessed URL to hide a finding.
- ClearForCheckedPatterns is only a static pattern result, not a claim that all links work, permissions are granted or the Notion UI renders correctly. Record page ID, fetched cutoff, examined links, exceptions and any truncated/unknown blocks separately. A failed fetch is not an empty clean page. Repairing project file cells does not establish that script paths or historical tables are clean.
- resume-task: NeedsCorrection blocks missing/inconsistent owner/step/binding; Deferred preserves terminal state, Manual boundaries and shortcut limits. Default `--phase execute` checks business routing; EligibleForOwnerCheck never grants approval. `--phase observe` checks only input/choice validation and recording, returning EligibleForInputCheck. A permitted scan may record an Automatic send choice while execute remains Deferred. report-only/draft-only cannot consume SendApproval; Manual forms stay excluded from scans in both phases. Never change policy to force eligibility. Original action/approval/stop/attempt checks remain mandatory. `--explicit-continue` requires an actual operator continuation.

CLI exit code 2 denotes Error/NeedsCorrection; valid Deferred and EligibleForOwnerCheck return 0 with different statuses. Always inspect the status, not exit code alone. Only a separately authorized owner-workflow invocation may use that policy; changing a helper argument cannot widen any command's scope.
