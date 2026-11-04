# EightDegrees Sales Workflow 0.1.56

Today now always plans Recent results over the original PendingTasks completed
and cancelled steps. The optional WorkflowRuns view remains Run history. Older
installations retain that view and its history; setup adds/reuses a registered
task_results view rather than cloning tasks or replacing native database blocks.

Legacy ordinary action submissions can be recovered with task.submission in the
existing local batch. It binds the actual original task, action, step, version
and configured operator; captures the checked request; then projects it as
ReadyToValidate. It does not accept facts, complete business work or turn an old
content confirmation into send approval. The owning skill still validates and
continues the original step. Duplicate observations produce no writes; partial
display failure repairs only that display. Changed input retains prior snapshots.

Submitted inputs leave needs-input views and appear under waiting. Successful
steps close on the original task at the same outcome boundary, independently of
later review or SMS timing. Genuine recovery exceptions remain visible with
their real reason. Failed local batches remove proposed writes as well as calls.
Actual Notion query URLs with or without /p/ resolve to the same original ID.

Regressions cover source-correct results, submitted-view predicates, original
queue recovery, idempotence, partial display repair, changed input, literal
checkbox rejection, stale/copied bindings and terminal history. No external
message sending or native timer reliability is claimed by these offline tests.
