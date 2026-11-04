# EightDegrees Sales Workflow 0.1.47

Inquiry names follow a unique verified CRM match first, then the current author signature, From display name and anonymous fallback. A display-name difference alone no longer requests customer matching. Anonymous drafts begin Dear Customer, answer the supported questions and then ask for a name. No guessed CRM contact, factual write or sending approval is introduced.

Inquiry labels are classifier output. New scoped inbound mail, including unknown senders, is classified after discovery and receives AimoreInquiry when applicable. Init creates/reuses the separate label mapping; existing installs resolve it without changing their authorized UNREAD/time scope. AimoreScanned remains progress only. Local inquiry.name and inquiry.label checks preserve provenance and additive, idempotent message-level changes. Labeling failure is isolated to its source.

Both current rule loader and scheduled scanner load these rules fresh. Existing queue recovery, stops, scope, exact email/CRM approval and accepted/unknown no-resend protections remain. Automated checks do not establish actual native-cycle, Gmail label modification or anonymous dispatch acceptance. Those require original runtime/provider evidence.
