# API result policy

Before submission validate the target and proposed/approved version once.
After a successful API response plus actual record ID the write is complete,
including Notion, CRM Notes, Gmail drafts and preview uploads. Known-target
updates may return explicit success/204 without a body. Empty/error/unknown is
not success. write.confirm handles acknowledgements; never fetch stored bodies,
raw MIME or saved preview bytes to compare. Local preparation hashes bind our
own package and approval only, not a claimed remote-body verification.

Timeout/error/unknown preserves its original attempt. Resolve original-record
existence by stable ID/request marker before retry; do not duplicate sources,
Notes or sends. Gmail/AndroidSync accepted dispatch finishes at the provider
boundary. Unknown dispatch is not automatically polled or resent. Preserve
actual external status without inventing transport or delivery observations.

Use [the inquiry flow](email-flow.md) for normal mail and [project cache](project-cache.md)
for reusable materials. Only relevant live approvals/stops/attempts need a current
observation before an effect; reuse that observation across local checks.
No successful-write content audits, full schema rediscovery or history sweeps.
Manual communication/CRM fact changes keep their own exact-version Notes review;
an inquiry name or project lookup does not create that separate workflow.
