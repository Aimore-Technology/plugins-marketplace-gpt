# One view and one consent click

Use the original PendingTasks database. New email-review-v4 needs only two added
properties: ReviewText (rich text) and Consent (native checkbox). Do not create
a new database, task, ordinary action form, separate copy or Submit control.
The canonical task is also its ActionPageURL. Technical package/binding and
accepted decision history stay in that task's body, outside the view columns.

## Setup once

email.view-plan takes pending_source (the original schema capture), page (actual
Today capture) and language. It emits ADD statements for missing properties and
a native linked table view spec. Never change existing property types. Reuse
RunSettings.operator_experience.email_review_view_id if registered. Otherwise
finish complete Today/view discovery before creating one view. Apply supported
DDL, create the view and register its original response ID once. A failed setup
is a scoped input-surface issue; do not create another view on each scan.
Explicit init installs/upgrades it; an enabled owner may finish a missing view
once without repeating full init. A stopped scan does no setup or migration.

The view shows Consent, ReviewText and the identifying Name, with wrapped full
text and no technical columns. It filters v4, SendApproval, sales-reply and
nonterminal records. Do not filter checked rows away: approved consent
must remain visible so the operator can uncheck before dispatch. Existing
manual Notes/data forms and their views remain separate business workflows.
A view is presentation, never access control or the scanner's coverage scope.

## Publish and process

email.prepare defaults new text/plain replies to v4 and makes task/action IDs
identical. email.review returns properties plus task_records. Save them together
on the canonical task; properties include ReviewText, Consent=__NO__, version,
route and self ActionPageURL. Do not put a checkbox inside ReviewText. A new
package/version must atomically publish its new narrative with Consent reset;
publication checks reject inherited checks or workflow-manufactured consent.

The operator reads the complete narrative and checks Consent once. Native save
is the submission. No second Submit, content-only confirmation, date checkbox,
actor field or repeated chat permission. Keeping it unchecked waits. Unchecking
before provider dispatch withdraws only this email approval; no global SMS stop.
If text/recipients change, email.accept returns EmailRevisionRequired.
The owner synchronizes the actual Gmail draft, publishes a new version and
clears Consent; the user then checks the final updated reply. Never send changed
content using an earlier check or silently overwrite their requested edit.

Reuse the complete current task-list properties for native consent discovery.
scan.watches selects changed/demanded v4 consent_task_urls with
email.consent-read-plan, returning consent_row_records for the actions feed.
Unchanged unsubmitted or already observed rows without ready recovery need no
full page fetch. Fetch only affected task pages once; reuse those originals for
email.accept/dispatch. Missing list fields fall back to a current original page;
incomplete coverage cannot establish idle. Full email.consent-observe remains a
legacy/direct-input adapter; do not emit both row and full-page triggers for the
same new submission. Package/input acceptance still reads the actual task on
runnable demand; no cached decision is promoted to new authority.

email.accept/dispatch accept the task capture only for v4; no action capture is
required. Approval binds the exact displayed narrative/package/version. Persist
accepted decision and stable attempt before send. Keep checked Consent visible
through an interrupted send; do not clear a consumed checkbox as though it were
withdrawn. Existing accepted snapshots avoid repeated business execution.
Stop/channel/attempt controls still apply. Successful Gmail handoff
ends email, with no delivery polling. In email.complete reuse the same original
task-write acknowledgement for task and action roles, not a second write.

New email packages contain no window, and new review text states that sending
happens at any hour on the next scan. Old windowed narrative may remain exact
historical evidence or be repaired to the same payload with the current timing
explanation; no copy edit or new approval is needed just to remove clock gating.
Clear only mail's obsolete date fields; SMS quiet hours remain independent.

## Today is the complete operator journey

The only normal email journey is Today -> read the full ReviewText -> check
Consent -> the next scan dispatches. Do not route a customer email through an
Actions page, a content confirmation or a second consent. Email reviews stay
in the native Email Review table, including checked rows before dispatch; they
are excluded from generic review/waiting lists that open technical task bodies.
A pending unchecked review is WaitingForOperator, Category=SendApproval, never
ScheduledWork merely because sending has not happened. Keep the real table
reachable from Today with a native reference; preserve existing native layout
when the connector cannot safely reposition linked database blocks.

Publish the exact email.review properties together with the saved package and
binding; saved technical body alone is not a usable review. On interruption,
scan.watches selects review_publication_task_urls and ready records tagged
review_publication_only. Reuse the original task/package with email.review-repair
to finish its missing native properties, then wait for the user's one Consent.
No action-page lookup, duplicate task, new draft, inherited old confirmation or
synthetic approval. This local repair cannot send. Complete current reviews
are not rewritten, and existing consent/attempt evidence is never reset.
