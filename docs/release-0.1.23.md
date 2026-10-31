# EightDegrees Sales Workflow 0.1.23

The 0.1.22 live review found that actual email/SMS results had needed private
owner invocations and free-text continuation hints. Those results remain real,
but public self-service and automatic email-to-SMS handoff were not accepted.

## Behavior

- The seven public command names remain unchanged. Public run-auto now uses
  one-cycle-approved-work: it can continue independently approved Automatic
  email/SMS work after the ordinary fresh checks, without scheduling. Explicit
  no-send requests and legacy restricted native jobs retain their narrower scope.
- Post-submission guidance emits public run-auto or documented Manual P0-A
  add-communication continue. It does not invent reply-draft continue or expose
  private owner commands. New inquiry reply tasks are Automatic; legacy Manual
  tasks keep their mode. reply-draft remains draft-only.
- Verified material Sent requires automatic cycle/due/draft or blocked/stopped
  registration before final email-owner completion. One native executor handles
  due work; there is no per-email Cron. The new offline planner/readback and
  material-handoff completion evidence bind the original task/version/message.
  RecordMaterialHandoff recovery never re-sends the email. A verified nonmaterial
  reply records NotApplicable without a cycle. A disabled gateway still gets
  observable pending work, while its dispatch remains disabled.
- Exact Notion-call preflight rejects display markup in canonical machine fields
  before either first-create or update, preserving exact IDs and ordinary titles.
- Today help/report-run body use timeless scaffolding with dated current fields
  and native views. Feedback requires the actual Running approved-work lifecycle,
  rather than the obsolete Active label. Existing stale pages are changed only
  by their permitted owner or explicit init upgrade; report repair scope stays
  narrow. Capture reuse guidance avoids repeating large serialized history.

## Verification and limits

Both editions have 300 passing offline tests, marketplace checks, clean diffs
and inspected deterministic archives. Shared business files/tests are identical;
platform manifests/native wrappers/runtime guidance retain their own identity.
The added regressions cover public routing, Manual isolation, legacy no-send,
verified scheduling copy, first-write ID markup refusal, partial handoff saving,
resends/caps/stops/unknown results, original page/message/version binding and
handoff recovery without another send.

No live email/SMS, native schedule or customer Notion mutation was performed for
this maintenance. The new public path and automatic handoff still require live
acceptance; no 15-minute runtime, own-number/two-way gateway, measured speed gain,
Claude runtime or independent Beta readiness is claimed by these offline checks.
After upgrade, use explicit init only if applying the presentation/setup upgrade;
old native tasks require explicit start and actual readback for approved-work
scope. Existing provider results, pauses, approvals, counts and history remain.
