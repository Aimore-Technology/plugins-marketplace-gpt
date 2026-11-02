# Operational monitoring and report consistency

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

## Actual observations

Use real tool/provider timestamps when supplied; otherwise record the actual observation time from the host clock. Never make up event times, reuse init time as a later attempt, or backdate an inferred action. Keep OccurredAt, ObservedAt and RecordedAt distinct when they differ. A manual report observes existing evidence; it is not a new health probe.

After each service operation, refresh that service's known LastAttempt from the actual attempt/observation. Advance LastSuccess only for a verified success; keep the last error and its time/log link even after recovery. Store a DataCutoff for evidence included and original run/log links. Log/projection saving failure needs backfill from the original evidence, never another external action. A report reread must not replace LastAttempt with its generation time.

Collect per-action evidence and coalesce each service's latest observation into one health update at invocation end when policy permits. Do not recursively probe/log the monitoring write itself. A report-only command writes only its report and required operational logs: expose stale health/quality evidence and the next owner-workflow action without changing HealthStatus, task state or schema. The next authorized owner workflow applies any pending projections.

Healthy means the documented tested capability is working at the last observation. Use Degraded for partial capability: for example native GB2312 full-body failure with successful same-source raw recovery, or Outlook sends working while searches omit known messages. One successful profile call does not clear that condition. Unknown/missing access is not Healthy; no configured schedule means no invented heartbeat interval. Stale is based on an actual configured interval. Add Degraded to the existing status select during an explicit schema upgrade if absent; otherwise explain the unsupported status in the body and mark schema setup incomplete.

## One consistent time snapshot

For each current daily summary, capture GeneratedAt once after collecting evidence; DataCutoff is the latest instant through which the stated scope is actually covered, not automatically the generation time. Derive the local display and business date using the configured IANA timezone/DST from those same instants. Use the same GeneratedAt/DataCutoff values in properties and current body summary. A UTC 12:37:14 on 2026-10-28 is Adelaide 23:07:14, not an independently composed local time.

Label observation time, planned time and missed-run/catch-up separately. If Notion properties normalize precision to minutes, disclose that precision and retain exact observed timestamps in the body/log; do not invent seconds to match. Before publishing a current summary, check property/body consistency, timezone conversion, current version and coverage. Read back when warnings or dependent decisions require it. Partial saving means summary synchronization pending; it must not redo business actions.

## Count outcomes separately

State scope, cutoff and completeness next to counts. Count distinct unresolved issues by original source/run + StepId + issue type/version, not retry events. Use:

- PendingCount: currently open operator tasks; paused/postponed are visible subsets, not extra rows.
- FailureCount: unresolved real workflow failures, including output-quality failures, in the stated scope. QualityIssueCount is the explicitly labeled subset, not an extra number to add again.
- UnknownCount: unreconciled real external attempts; never fold unknown into a zero-failure claim.
- RecoveredFailureCount: distinct historical issues with verified recovery, kept separate from unresolved counts.
- SyntheticFailureCount: explicitly simulated report/test issues, excluded from real failure totals.

Successful CRM transport/readback does not close missing-field or approved-payload defects. Keep the append result/external ID and a separate unresolved quality issue linked to the original note; correction requires a new reviewed version, not rewriting the old note or repeating it. A completed review may coexist with such a quality issue. In the owner workflow, upsert the single NoteQuality ExecutionExceptions task defined in [CRM Notes](crm-notes.md). A report-only invocation records any newly observed defect in the report/log and links the next owner-workflow action; it does not create or change tasks. Include known unresolved quality defects in quality/failure counts even if task creation is pending; PendingCount still counts actual tasks only.

Add absent count properties during explicit init upgrade, preserving prior IDs, decisions and historical snapshots. If legacy FailureCount only meant uncorrected provider-write errors, retain that historical value with its original meaning; label the new current metric and migration in the body. Do not silently reinterpret old zeroes as proof of quality. With incomplete coverage show known counts plus unknown coverage, not a fabricated global zero. Test assertions (Passed/Failed/Waiting/Untested) are separate from operational issue counts.

## Links and current presentation

Use real provider URLs for clickable source links and code style for literal names/paths, including bare `project-v1.md`. For Notion uploads use the supported embed/file block syntax or same-file preview fallback from [HTML approval](html-approval.md); a bare upload URI is not a verified preview.

Check the saved Notion summary itself for fake `http://<filename>` links, even if the local Markdown validator passed. Replace only the bad presentation with a literal name or verified source URL. Preserve original evidence and history. Never feed rendered mailto links/escaped property strings into an identity query or a send recipient.

Apply the page-wide [evidence check](evidence-checks.md) to the actual fetched report/task/action page, not just repaired project-file cells. Include script/Skill paths, all table columns, prose, examples and retained history in declared link coverage. Format every local path/file name and invalid URL example as code BEFORE writing; local evidence links usable in Codex become literal paths in Notion. Use explicit native mentions or verified Markdown links rather than bare URLs touching punctuation.

Record the checked page IDs, observation times, pattern scope, approved URL exceptions, truncation and remaining issue groups. Re-fetch after targeted presentation repair when needed to establish the result. A successful tool write, a local Markdown pass, or zero problems in a subset cannot close a page-wide link-quality issue. Remaining suspicious/unverified targets keep a quality issue open and appear in scoped FailureCount/QualityIssueCount. Keep original failures and later correction evidence; do not overwrite a prior report's tested-version or pretend that checking one page validates the whole workspace.

## Canonical outcome projections

Use [outcome state](outcome-state.md) after known provider effects. Derive
current counters from deduplicated immutable outcomes, not handwritten zero
copies in RunSettings.internal_audit. Show historical approval-time unknowns
as historical, distinct from current operator receipt/sender observations.
Preserve provider status exactly. Send owners verify current task/index/action
readbacks before final completion. Reports disclose conflicts and stale views
without fixing business state. End-of-owner Health updates use actual service
observations and can be coalesced; do not probe every unaffected service.

## Compact current reporting

Read the current saved-view snapshot once, then fetch only the open action/outcome or a specific contradictory original needed to decide current counts. Reuse those captures for links, scope checks, body and final verification. Do not read every completed action, entire client history or all Skill documents to refresh an unchanged daily brief. Fetch the current brief once; patch only changed current sections/metadata and label retained prior versions as history. Report writes remain restricted to the frozen report/run/log registry.

Show unacknowledged dispatch attempts, unresolved internal business failures, presentation issues and recovered history separately in the saved language. Group shared-cause page defects by a stable issue key and list affected records, rather than multiplying one defect by every page or retry. Preserve earlier counts with their stated historical definition; do not silently rewrite an old failure metric. A local diagnostic error or a recovered dependency check is not another failed customer send.

For email and SMS, successful provider acceptance counts one completed dispatch. Do not create a
failure/pending item or degrade that result because Delivered or a handset
observation is absent. Preserve the raw status and optional delivery metadata;
actual missing reply-reader or scheduler capabilities are separate observations.
