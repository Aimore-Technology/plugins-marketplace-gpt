# Confirm writes without reading their bodies again

Policy: api-result-v1. Validated by offline acknowledgement, error/unknown,
phase-completion, approval-scope and duplicate-protection regressions in 0.1.48;
live performance is not measured by those tests.

Check the intended recipient/customer, proposed payload and approved version
before submission. Then API success plus the actual record ID completes the
write, including CRM Notes, Notion pages, Gmail drafts and preview uploads.
Do not download raw MIME, stored Notes or preview bytes to compare again.

An empty/error/unknown response is not success. Preserve the original attempt;
resolve that record's existence before any retry. An acknowledged provider
request is never sent again because a later page or receipt failed.

Use write.confirm and execution-api-v1 completion. Keep current approval,
stop/window/count and source-scope safeguards. Reuse initialized workspace
IDs/schemas/templates until relevant change or an actual API failure.
