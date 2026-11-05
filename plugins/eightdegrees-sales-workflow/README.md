# EightDegrees Activepieces client

Version 0.2.0 preserves the existing plugin identity and replaces local business orchestration with four client commands: init, add-communication, reply-draft and report. Five small skills provide the command router and these four entries. Activepieces owns workflows, scheduling, queues and current-version approval checks; Notion provides human review.

The host must already have an authorized Activepieces MCP connection. This package has no server or credential store, introduces no duplicate OAuth connection and contains no customer-specific flow/workspace IDs. Bindings are resolved from the connected project's published callable flows. Install/enable the plugin, select it, then request a command or its deliberate natural-language equivalent. See [commands](references/commands.md) and [client protocol](references/activepieces-client.md).

The Python 3 helper validates requests, prepares one allowlisted MCP call and interprets a correlated result. It performs no network operations. An empty dispatch response means queued, not completed. A generated transport request ID identifies the child run; a wrapper run ID never proves the business operation succeeded. Unknown dispatch is not automatically retried.

Communication and draft preparation return the actual Notion review link. This client never sets Consent, appends CRM Notes, creates contacts or sends customer messages. Report only shows the backend's report. Native run-auto handles later eligible work; start/stop/run-auto are not public client commands. Pause future cycles on the backend flow's page. Initialization is still required before business submissions.

The previous 0.1.58 payload remains in the repository's legacy archive for historical tests. It is excluded from this installable package and cannot be loaded as an alternate execution owner. Backend capabilities and known migration gaps are separate from this client release; connected accounts alone do not prove a real customer end-to-end acceptance test.
