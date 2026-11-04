# EightDegrees Sales Workflow 0.1.49

New inquiries follow one source capture and CRM match, exact project/lot lookup,
a private project-material cache, one frozen draft/preview and one combined
content-and-send review. A matched CRM name wins; otherwise signature/From or
anonymous fallback is recorded automatically without a name-confirmation task.
Unmatched CRM remains mail-only; no contact is silently created. Missing or
ambiguous project material requests one tailored input.

New email-review-v2 Approve binds exact content/materials, recipients and send
window together. reply-draft prepares this page and remains no-send. run-auto
uses email.accept/dispatch on one current observation and persisted original
attempt; old content-only Confirm is never promoted to send permission. Consumed
submissions resume from the saved accepted decision without asking again. Edits,
stops, expired windows, revoked channels and unknown/accepted attempts block the
actual affected send. Gmail acceptance completes email; CRM and SMS registration
can recover independently, without replaying it. SMS has no per-message review.

The scoped project-cache-v1 stores authorized text, parsed project facts, source
IDs/versions and immutable snapshot identity in private local user state. A
24-hour default TTL, explicit refresh, observed revision or scope change causes
one affected refresh. Warm lookups call no connectors or re-extraction. Project
and exact lot are distinct; different accounts/workspaces/scopes do not share
cached files. No customer records, authority or credentials belong in this cache;
no cache content is distributed. Unavailable local cache falls back to a scoped
source read, without a new backend. Approved packages remain frozen on refresh.

Conflicting normative guides and old transport/preview/phase experience cards
were rewritten, not hidden behind another override. The default CRM body-readback
flag is false and packaging validation enforces the short-flow defaults and
forbidden legacy instructions. Current native entry prints only the compact
current procedure while fingerprinting the actual installed rules/helpers.

This release does not create or change a native task, switch real stop state,
rewrite existing approvals or claim unattended/live timing acceptance. Source,
connector, Notion UI and native scheduled end-to-end behavior still require a
target-host run. Offline fake-provider/cache tests do not prove real delivery.

Validation: 664 offline tests cover the retained workflows plus cold/warm cache,
account/workspace/scope isolation, exact lot matching, expiry/revision refresh,
immutable snapshots, combined approval, payload/window edits, consumed-submission
resume and replay/stop protection. Warm fixture lookups make zero connector
calls; this is not a live mailbox timing benchmark. New draft/intake queue
estimates reflect the short path while original explicitly saved estimates
remain intact. Packaging rejects the obsolete conflicting instruction phrases.
