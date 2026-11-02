# EightDegrees Sales Workflow 0.1.31

The 0.1.30 local simulation accepted content and sending decisions but could not
send the email: its content-review completion plan also listed the future send
as an executing task. The final guard consequently demanded Sent/presentation
evidence before review could finish, while sending required a completed review.
This release corrects the phase contract, retaining strict send-result checks.

New execution-v2 plans freeze one canonical ResumeStep per completion unit.
Every task declares its actual step/version; preparation validates its owner and
invocation scope, rejects mixed phases and generates phase-specific minimum
evidence. ReviewReplyDraft completes with the exact stored draft and reviewed
content without Sent/CRM receipt/SMS proof. Sending remains a separate phase
with original completed review, exact approval, current stops/window/attempts,
draft and actual Sent MIME, outcome, CRM receipt, material handoff and linked
presentation evidence. SMS notification sending has its own standing-authority
and exact request-outcome checks; SentToNetwork remains a completed send.

The completion gate binds actual execution routes to their frozen steps. Final
owner-write refuses mixed legacy routes and missing/wrong phase evidence.
Opaque legacy multi-task plans are refused at ready before dependent work;
single-task execution-v1 plan readback is retained. Recovery preserves the old
plan/refusal and original approvals, records the defect, and starts a linked
prospective phase run for the original unfinished step. It does not rewrite past
evidence, recreate reviews or resend an already accepted provider operation.

New phases also check the canonical task's current saved properties/body through
notion.task-summary, separately from the registered action display. Both detect
current instructions that still ask for an already accepted review/send approval.
Labeled history, submitted answers and frozen content stay unchanged.

Regression coverage includes the mixed-plan failure topology, review completion
with an unsent draft, forbidden future evidence, generated obligations for every
registered route, wrong owners/steps/policies, frozen version/route binding,
independent review -> email -> notification completion using real offline helper
outputs, missing/deleted send proof and English/Chinese stale approval text.
Existing send/receipt/handoff, permissions, scheduling and no-replay tests remain.

Both editions receive identical business changes and the packaged phase-boundary
Experience card. Default cadence stays 30 minutes (20 optional), with the same
900-second soft budget and 120-second publication reserve. This release makes
no performance improvement claim and does not alter live schedules/accounts,
customer decisions or the 0.1.30 failure report.

Offline unit discovery, marketplace/schema checks, deterministic ZIP inspection
and shared-file comparison are release gates. No live email/SMS resend, customer
record recovery, GPT task or Claude Cowork recurrence was performed as part of
this repair. Those remain a separate post-upgrade integration verification.

Verified before publication: 415 offline tests passed in each edition, including
16 focused phase-ordering regressions. Marketplace/schema gates and archive
inspection passed; all 100 shared business files match byte-for-byte.
