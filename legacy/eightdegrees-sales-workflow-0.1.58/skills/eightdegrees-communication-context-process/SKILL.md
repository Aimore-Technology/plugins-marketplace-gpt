---
name: eightdegrees-communication-context-process
description: "Process authorized customer email, text or transcripts into reviewed CRM Notes and approved persona changes; P0-A starts manually; submitted reviews resume through the shared queue."
---

# Process customer communication

Apply [API result and minimal-read policy](../../references/api-result-policy.md) before this workflow. Successful writes use acknowledgements/record IDs; do not fetch stored bodies to compare. Reuse initialized workspace metadata.


Use [short communication intake](../../references/communication-fast-path.md) as
this workflow's entry. Run communication.read-plan for the actual source kind
and phase, then only its scoped reads. Provided readable text needs no mailbox,
Dropbox, Calendar, preview, scanner or installation-wide query. A property named
in a transcript does not request a property investigation.

Default Mode=Manual. Match the current scoped CRM customer by email/phone; CRM
name wins over a differing signature after a verified match. Identity conflicts
need the original matching form, never a guessed/new CRM contact. Preserve the
original source, IDs and source/customer archive. Optional unknown fields stay
unknown. Use communication.note to render the standard plain-text Notes once,
then create the exact current-version review. Stop before unapproved CRM facts.

Do not eagerly open every linked reference. The short procedure retains current
phase requirements; run execution.prepare/ready, facts.canonical, exact
notion.mutation, pre-call route and receipt completion checks through the existing
code. Use original captures and compact local-check output. Load detailed docs
for the actual next phase or a concrete failed/unknown contract only.

A submitted current review resumes through the shared queue without another
continue command. Before one approved append, recheck current original task/
action, exact payload/target, attempts and complete scoped duplicate evidence.
Persona changes use persona-update for ONE combined append. Confirm the CRM API acknowledgement/NoteId
and save affected Notion results; unknown effects reconcile, never retry
blindly. A display repair cannot repeat a CRM write. Never adopt another Manual
task or process a sales send as communication Notes.

This skill sends no customer email/SMS, starts no timer, calls no scanner and
creates no Calendar event. Return one current action/result link with the next
operator action. No global report/Health rebuild or repeated status narration.
