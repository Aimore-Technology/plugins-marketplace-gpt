# EightDegrees Sales Workflow 0.1.57

The email operator journey is Today -> read the complete reply -> check the
native Consent checkbox -> the next scan dispatches. No Actions page, separate
content review, second consent or Submit. Normal mail rows live only in the
native Email Review table; generic action-link review/waiting lists exclude v4.
The table retains checked rows before dispatch so consent can be withdrawn.

Native review publication explicitly sets WaitingForOperator, SendApproval,
ReviewText, unchecked Consent and self ActionPageURL together. Saving a technical
package body alone is not complete publication. Current task rows identify
incomplete native projections; scan.watches provides their original task URLs
and the queue retains publication-only recovery even without new mail or edits.
email.review-repair reconstructs only the saved same-version package's native
properties. It creates no new task/draft, grants no approval, and cannot send.
Existing consent/attempt evidence is preserved; complete/terminal records need
no writes. This does not add a routine full-page sweep.

The existing Today native table remains the email input surface. Preserve native
blocks and the registered view. A scoped connector layout limitation may prevent
moving that table to the top; keep it directly reachable from Today rather than
rebuilding the workspace or routing email to Actions.

Offline regressions cover interrupted publication, original-queue recovery,
one-click acceptance/dispatch without an action capture, no premature dispatch,
idempotence, stale/terminal records and native exclusion from generic lists.
No live mail is sent by those tests, and native timer reliability is not claimed.
