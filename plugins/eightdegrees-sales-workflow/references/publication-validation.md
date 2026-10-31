# Validate publication before recording completion

The BEFORE-call half is [notion-mutation](notion-mutation.md), mandatory for
initial creations as well as later text/property writes. Saved-page checks are
the AFTER-call half; neither can retrospectively stand in for the other.

Use the existing offline [notion_checks.py](../scripts/notion_checks.py) with `--input <capture.json>` or JSON on stdin via `--input -`. It performs no connector calls or writes. These checks improve model execution; they are not a host-enforced runtime. Preserve failed observations and original logs even after a later check passes.

All owners additionally follow [owner completion](owner-completion.md) and owner-write; report retains report-write. completion-gate also accepts route (EligibleForOwnerCheck), route-observe (EligibleForInputCheck) reply-draft (StoredReplyVerified, phase=draft) and reply-sent (StoredReplyVerified, phase=sent) evidence, bound to the actual Notion task page. Sent-message evidence cannot stand in for pre-send draft proof.

New owner plans use [execution preflight](execution-preflight.md). Keep its
generated execution-plan check in required_checks and supply the original ready
result plus integer exit. The gate checks the saved plan digest, owning run,
invocation and publication version. It does not prove historical tool order.

## Actual schemas and entity types

Before creating/updating data-source rows, `schema-values` takes the original `data_source` fetch, actual target `data_source_id` and exact proposed `properties`. It reads the JSON data-source-state supplied by the tool, checks source identity and rejects unknown/read-only properties or enum values outside actual options. For a page batch, check each row. Other types still need the actual tool contract. Do not invent a source Status such as NeedsData, add an option to make a request pass or conflate source state with PendingTasks.Category. Use an existing appropriate source status; put the missing-data reason in its task. Reconcile the original page/source after an actual refusal; do not assume intended fields partially saved.

For saved-page link validation use `page-links` with `page` (the original fetch) and optional exact `allowed_urls`. It checks actual page content, excluding tool wrappers/schema descriptions. A database/data-source/view returns ExcludedNonPage, not a clean page. An unknown type or explicit omitted/truncated content blocks the check. Keep excluded entities and coverage limits in the report. Use workflow_checks.py notion-links with raw Markdown only as a labeled pre-publication text check, not proof of saved-page coverage. Never pass an entire mixed fetch collection as reconstructed Markdown or erase a finding by changing its actual entity type.

## All current action text, not only its header

After each owner transition, inspect Current status, Processing result, current input instructions and the hub entry against the same canonical task/version. Update both workflow-owned status AND result sections. Accepted/Pause/completed work must not retain Not submitted, choose-one prompts or live submission controls for that inactive step. Preserve operator answers and checked choices as labeled history. New user input still follows the existing explicit continuation/version rules; a presentation repair supplies no new approval.

`task-display` accepts the original action `page` plus canonical `task` fields State, ContentVersion, Decision and DecisionVersion. It checks the English/Chinese current section names from the packaged layout, current version, and stale unsubmitted/active-input patterns against recorded decisions and terminal states. DisplayConsistentForCheckedPatterns is limited pattern evidence, not semantic approval of all prose. Review remaining current statements manually; source quotes, review material and labeled history are not rewritten to satisfy a pattern. Missing/repeated current sections need a verified owner/setup repair, not another appended current section. For older layouts, establish the distinct owned sections before claiming this check passed.

Do not use section-patch on sections containing native mentions/dates/media references, even when the fetched old_str occurs exactly once. Their rendered text is not a reliable connector match anchor. The helper returns NeedsCorrection for a changed native-reference section. NoChange needs no write. Keep pure text status/result blocks separate from linked queue entries; edit links using an actually supported smaller block operation. Do not invent a block API, retry refused whole-section variants, replace an entire hub by default or drop children/answers. If no safe operation is available, keep a quality-repair finding with existing links and require explicit setup repair. A refused display patch never repeats CRM/sending.

## Completion evidence

For the native image alternative, freeze a `preview-image` requirement with the saved preview `entity_id`, actual `content_version` and original `html_sha256`; use only the actual SavedImageAndBytesMatch result from [image preview](image-preview.md). Completion rejects another HTML/version. Do not relabel image evidence as HTML-only SavedEmbedAndBytesMatch. Independent pixel/copy inspection and ordinary approval remain required.

Before checks start, freeze `invocation_id`, `publication_version` and a nonempty `required_checks` object keyed by meaningful check name. Each value declares `kind` (page-links, task-display, preview or schema-values) and exact `entity_id` from the actual dependency. For report, include every current report/brief target. For an owner, include the changed active action display and its other required publication checks. Record required manual consistency checks separately; this helper does not automate them. If content/version changes or a new issue needs repair, keep the old failure and establish a fresh publication revision before rechecking.

`completion-gate` takes that contract plus `checks`, an array of actual command results. Each entry has name, invocation_id, publication_version, integer exit_code and the parsed result object. Missing/duplicate/unexpected results, exception/malformed output, nonzero exit, wrong status/type/target, unresolved findings or stale invocation/version return NeedsCorrection. A skipped nonpage cannot satisfy a required page check. Capture exit code and JSON separately; never discard a failed process status because its output looks useful. EligibleForCompletion permits the next completion-registration step only; it is not provider delivery or global health evidence. Tool errors still require their own reconciliation.

For report-write, provide the SAME invocation_id/publication_version in the frozen registry. A final own-run Completed or final Success log additionally requires `completion` containing the full current completion-gate input. The helper recomputes it and requires coverage of every registry report page. Do not pass only an invented EligibleForCompletion string. Register newly created report IDs before final checks. Preflight and save the report while its run is InProgress; fetch/check saved output; only then preflight and record completion/final Success. If checks fail, retain InProgress or explicit Error/quality pending and append actual failure evidence. Never mark completed first and rely on a later correction. A previous premature Success remains historical with an appended correction, not overwritten.
