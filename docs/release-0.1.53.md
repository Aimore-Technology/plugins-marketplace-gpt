# EightDegrees Sales Workflow 0.1.53

New inquiry replies use one native Email Review table over original PendingTasks
records. ReviewText contains complete recipients, subject, plain text and sending
window; Consent is the only checkbox. Checking it submits content-and-send
approval; no second Submit, date checkbox, actor field, Return/Pause/Cancel form,
new action page or duplicate task. Wrapped text stays visible alongside Consent.
Checked rows remain visible through delayed sending so consent can be withdrawn.

email.prepare/review defaults text/plain replies to email-review-v4 and publishes
one canonical task projection. Technical bindings/history remain outside view
columns. email.accept/dispatch use that task capture only. Narrative edits require
a synchronized new version with Consent reset. Publication rejects inherited
or workflow-manufactured checks; an unchecked current checkbox defers sending.
Exact-version/current-control/attempt protection and standing SMS remain.

Discovery watches the native task once and emits consent/narrative changes from
the actual previous actions-feed revision. Withdrawing/rechecking gets a new
input occurrence; timestamp-only/log changes do not create work. Completed tasks
produce no new events. Existing v2/v3 forms and approvals preserve their original
scope and are not automatically promoted or checked during upgrade.

email.view-plan plans only missing ReviewText/Consent fields and the original
linked view. Init or the affected enabled owner creates/registers it once and
reuses its saved ID. No new database, native timer or Portal. The current Notion
workspace has the two fields and registered wrapped native view; no old tasks
were converted or approved, so v4 rows appear when new drafts are prepared.

Offline tests cover one-checkbox dispatch without action capture, unchecked and
withdrawn consent, typed checkbox checks, exact narrative edits, canonical task
binding, timing/stop/unknown attempts, repeated acceptance and new-version reset.
Actual checkbox edits through a complete timed send cycle, mobile presentation
and end-to-end latency still need target-host observation.
