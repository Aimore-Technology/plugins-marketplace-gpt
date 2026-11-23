# 0.2.1 — Portal review client

Initialization no longer collects Notion IDs. Communication and draft results now require the matching backend reviewId and HTTPS workbench URL. The helper validates the task query parameter and keeps asynchronous exact-run correlation. Approval remains in the Portal workbench; this plugin never submits it or sends customer messages. No customer-specific Portal host is embedded in the client.

Seventeen client tests pass. Package validation and deterministic ZIP content/CRC checks pass. The installed payload remains eleven files; archived 0.1.58 orchestration is excluded. Backend deployment and customer business acceptance are separate checks.
