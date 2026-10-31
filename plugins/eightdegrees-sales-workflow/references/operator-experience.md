# Today, short reviews and an explicit next step

The primary human entry is Aimore/Today. Actions remains storage for the existing
ordinary input/review pages and history; PendingTasks is still the only task
database. English entry names and stable schema keys remain, while copy uses the
saved en/zh-CN language. No Portal, custom widget or new background service.

## Setup and upgrade

Explicit init/upgrade reuses registered Today/views, or performs complete scoped
discovery before creating them. Preserve the existing Actions ID and every task,
action, answer, approval and child page. Do not rename or rebuild their records.
Create one ordinary Today page under Aimore using [the layout](../assets/today.md).
Publish only the short introduction before creating native views, then append
help using insert_content at end. Let each native view name label its group;
do not duplicate outer headings that can drift from the actual view. Never use
replace_content to rearrange database tags: the observed connector can scramble
their order even when every ID survives. On upgrades retain actual native order
and use small text-only edits; unsupported positioning remains a layout limit.
No placeholder text or copied rows. Today contains timeless navigation/help only: do not add static current-readiness or waiting-for-approval claims that can outlive the actual task. Current business state comes from verified linked views and dated original outcomes. Explicit init upgrade removes only stale owned help text using exact text edits, preserving all native blocks and history.
With actual source/page fetches, run `operator_experience.py today-views` to plan
native linked views: Needs my review, Needs my information, Needs my attention,
Waiting and paused, and optional original Business results/daily summaries.
Use the actual create_view schema and documented view DSL, then read back each
view's source/filter/show fields. Registration follows verified results; an
uncertain creation is reconciled by its returned ID before retry.

On explicit setup/upgrade, the planned task_page_layout may hide technical
properties on task-detail pages while retaining the title/editor. Read the actual
database-page-layouts specification and source first, apply only the supported
page_layout operation, and read back the layout. No DDL/property deletion, row
value change or access-control claim. The original database remains the technical
view; ordinary action pages remain the input authority. If unsupported, retain
the direct ActionPageURL and label this layout portion incomplete.

Save operator_experience.version=operator-ui-v1, today_page_id, today_view_ids and
today_mode=linked-views in RunSettings. Do NOT replace saved_view_ids used for
complete execution discovery with these narrower display views. If view creation
is unavailable, provide one verified manual link list and label partial setup;
do not claim live/native views or build another database.

Link Today first from the root, report and ordinary action pages. Existing Actions
navigation receives a short move-to-Today notice and historical headings; its
children stay intact. Canonical Name/ActionPageURL updates make the native lists
follow current versions. In verified linked-view mode, owners no longer copy a
new queue snapshot to Actions/Today on every transition: persist canonical state
and bindings, then verify affected records. Do not register unchanged Today as an
owner publication target. Legacy installations retain their one verified queue
until explicit upgrade succeeds. A native row title still opens the task record;
the visible action-page URL is the direct processing link.

## Review before deciding

Use [the action layout](../assets/task-action.md). Its first screen contains the
customer/topic, three short lines (request, proposed response, decision needed),
and current observed status/next action. `operator_experience.py review` emits
these lines and explicit field-level before/after differences for a revision.
These are a guide; preserve full exact-version copy/Notes and the matching saved
preview BEFORE decision controls. No summary-only approval, new inherited checks,
or silent change to approved bytes. Keep content and send decisions separate.

Show already verified applicable values once with provenance, not repeated
editors. The helper returns only missing/invalid/unverified fields as editable,
preserving any typed draft answer. Include business labels, required/optional
markers and examples that are clearly examples, not submitted values. Unsubmitted
answers, an unrelated setup source or an old project version are not verified
prefill. Actual validation and acceptance stay with the original owner.

## Saving, requesting, accepting and executing differ

`operator_experience.py feedback` produces honest stage copy and a copyable
continuation. Read canonical fields plus the current version-bound accepted
snapshot when claiming acceptance. A checked submit to-do only requests processing;
an unobserved edit never means accepted or sent. The helper does not execute.

- Manual P0-A requires the documented public add-communication continuation after submission.
- Automatic data/content/send work uses the next verified native tick, or the single public `@eightdegrees-sales-workflow run-auto` command. It may consume an independently approved exact-version/window send without another chat permission question. Missing approval or changed scope stays pending. Never print an internal owner invocation or an invented continue subcommand.
- Manual P0-A uses only `@eightdegrees-sales-workflow add-communication continue <action URL>`. Legacy Manual sales/SMS tasks remain Manual and receive an explicit capability/migration limitation; a scanner cannot silently take them over.
- Promise scheduled checking only from enabled, verified native task evidence;
  do not invent a countdown or infer a next run from the target 15-minute cadence.
- Paused/cancelled/completed tasks do not offer an old submission as a new action.
  Expired windows preserve the draft/answers and require a newly approved window.
  Unknown outcomes require original-attempt reconciliation, never blind resend.

UI text can change when the owner observes new evidence; Notion edits do not
trigger an instant callback. Before that observation show the last check time
and the static explanation of request vs acceptance. Status feedback must not
require an extra Notion write for every internal read/check.

## Results and waiting

Use [the short daily layout](../assets/daily-brief.md) and original Business-run summaries, with observation
times and direct original links. Keep email Sent, customer receipt, SMS network
acceptance/delivery and customer stop distinct under [outcome state](outcome-state.md).
Do not copy another channel's state into every closed action. Detailed logs and
history remain accessible rather than repeated above the user's controls.

operator_experience.py results derives localized rows and deduplicated counts
from existing verified outcome events using outcome_checks. Supply explicit
coverage_complete; partial observations never claim global zero. Render result,
receipt and observation time; keep message/task IDs behind original links.

During longer work give concise chat progress at meaningful stages: scope checked,
source/version resolved, draft ready, or result awaiting reconciliation. Save
only real required checkpoints/outcomes. Reuse captures and [local batches](local-check-batch.md)
to reduce repeated reads, serialization and shell calls; measure new live latency
before claiming a speed improvement.

## Timeless scaffolding and current facts

Create Today help and report-run body as timeless procedure/history scaffolding. Do not seed phrases such as currently waiting, generating, not yet verified or ready now that require later unauthorized body repairs. Run State/Summary and dated linked task outcomes carry the current status. Initial plan headings are explicitly historical. Report updates only its permitted properties/report/log targets; it does not repair Today or business actions. An owner or explicit init upgrade may remove stale owned Today help with exact text edits while preserving native blocks.
