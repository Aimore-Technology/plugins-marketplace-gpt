# EightDegrees Sales Workflow 0.1.48

Native rule loading still reads and fingerprints all current governing files on every wake, but defaults to current operational Markdown plus file paths/digests. Python implementation text is only printed for explicit --full debugging. Fresh helper execution, scope/stop checks and current-rule adoption are unchanged; no permission cache is added.

Manual communication intake now has a short phase procedure and deterministic communication.read-plan. Provided transcripts need no Gmail, project-folder, Calendar, preview or global dashboard scan. A customer asking about price is recorded as a request, without investigating a property unless explicitly requested. communication.note reuses the strict existing plain-text CRM renderer; the model selects business content while code formats it.

The communication entry stops eagerly loading the entire general reference graph. Existing execution plans, exact mutation preflights, current approvals/routes/versions, CRM attempt deduplication/API acknowledgements, persona one-append and owner completion remain mandatory. Detailed documents load for the affected phase or a concrete failure, not every step. Both editions share these changes.

Automated payload/read-plan measurements are not live runtime or token-billing benchmarks. Real communication latency still depends on model, connectors and Notion writes. No CRM/email/customer data is mutated by performance tests, and native task cadence is not changed.

API-result-v1 replaces routine post-write body/readback comparisons for Notion, CRM, draft and preview writes. New completion plans require original successful API acknowledgements/record IDs, current pre-call routes and actual dispatch receipts. Timeout/unknown attempts retain scoped existence reconciliation and no blind retries. Static workspace IDs/schemas/templates are reused until relevant change or actual provider error; dynamic stop/approval checks stay current.

Validation: 639 offline tests pass in each edition; marketplace payload/reference checks and deterministic ZIP inspection pass. The compact rule output measures about 38 KB versus 114 KB for full code output (66.8% less); both modes use the same current-file fingerprint. This is output size, not measured token billing or end-to-end latency. No actual native-cycle acceptance is claimed for 0.1.48.
