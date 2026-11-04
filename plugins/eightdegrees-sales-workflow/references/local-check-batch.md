# Read once, check once, keep one result artifact

Normal phases do not have a separate preserve-originals/save-input/version-log
step. Do not call capture.commit or capture_bundle.py for every response or
phase; these remain legacy diagnostic/recovery adapters only. Do not split a
large original into model-authored append-file calls. Preserve actual tool
objects with the host's supported orchestration/native artifact facility.

## One complete phase

1. Reuse already returned original objects. Collect independent current reads in
   one host orchestration when supported. Preserve errors/warnings/pagination;
   print only IDs, counts and actual failure summaries, not full raw bodies.
2. Run local_checks.py --input <plan.json> --output <phase-result.json> once for
   all ready checks. Inline plan.captures contains named original objects.
   --input - also accepts one complete stdin payload. No preliminary capture
   file is required. The output file itself atomically contains originals,
   plan and actual results, including original errors on failure. Stdout is a
   compact summary. The same phase does not need a second original-record file.
3. Subsequent checks use --captures <phase-result.json> and a small new plan.
   New originals may join plan.captures; existing aliases must match exactly.
   Use a new revision alias for a changed response. Do not retype old page bodies
   into model context or upload them as shell chunks. Identical output is not
   rewritten. Never overwrite the source bundle or plan with result output.
4. Inputs use {"$capture":"name"} and {"$result":"earlier-check"}. Require
   actual helper statuses plus LocalChecksPassed/exit 0. A saved result is not
   permission. Refused batches strip executable result calls. Original proposed
   arguments in captures remain evidence, never an executable approval.

Host support varies. If original tool artifacts are already saved by the host,
reference them directly. If the host cannot preserve/programmatically pass an
original object, report that concrete limitation; do not create a long series
of capture-writing calls or claim a smaller tool count merely by renaming them.
No hidden thread databases, new service or additional native task is needed.

## Read only demanded Notion pages

Reuse the current complete canonical task-list query/view response. Include
url, State, ActionFormVersion, ContentVersion, Consent, ReviewText, SourceKey,
OwnerSkill, ResumeStep and Mode in that existing discovery projection; no extra
query per task. scan.watches input includes the existing current now timestamp, complete tasks
and original index/settings captures. It runs email.consent-read-plan and returns
consent_row_records and only required consent_task_urls. Compare row input
fingerprints to the actual saved actions-feed revisions. Feed consent_row_records
into actions discovery; do not also enqueue a second full-task-observe event for
the same native row. Fetch a full current task only for a changed consent/text,
runnable saved recovery or an incomplete projection. Read that task once and
reuse it for exact acceptance and imminent dispatch. No separate v4 action page.

No changes and no executable backlog means zero full v4 task fetches, not one
fetch for every active row. This is selection, never cached approval authority.
True withdrawals, new versions, edited text, due recovery and incomplete pages
still get their actual current observation. Unchanged complete rows may be
skipped; incomplete task-list coverage cannot justify idle. Missing projected
fields fall back to the original registered task, never guessed values.
Legacy ordinary action forms still require current actual input; do not cache
away unobserved human edits or broaden the configured discovery scope. Respect
known Notion SQL capability/quota; reuse a supported existing saved-view query
when necessary, and do not reprobe a known exhausted query method each scan.

## Durable effect boundaries remain

Persist original Inbox source, accepted decision/AttemptId before dependent
provider actions, and accepted/unknown outcomes immediately. Local phase artifacts
cannot substitute for those business records. Confirm writes from original API
acknowledgements; do not refetch own writes or re-run all checks after each
projection. Coalesce source/task/action outcomes at a real boundary and cycle
metrics once. Do not log file saves, metadata reads or the act of logging.

## Legacy submission projection

Batch `task.submission` for actually submitted task-action-v1 forms using current
original task/action captures, now and language. Persist its observation before
its projected properties; the owning workflow still validates the request.
Repeated queued snapshots produce no writes. `operator.today-views` always plans
task_results from PendingTasks and keeps optional WorkflowRuns as run history.
