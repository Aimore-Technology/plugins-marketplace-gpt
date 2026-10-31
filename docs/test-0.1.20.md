# Directed acceptance for 0.1.20

Retain the 0.1.19 findings and original provider/CRM IDs. No replays of completed
sends or Notes are needed to test a presentation repair. Start/stop and cloud
runtime validation remain independent acceptance work.

1. Prepare initial source/task/action text with a local/malformed link. Observe
   notion_mutation exit 2 and no returned call, with no subsequent create call.
   Correct it, rerun and inspect actual call order before the first publication.
2. Attempt a database result/log update with JSON-shaped ExternalIds or a wrong
   select/unknown field. Confirm exact schema checking occurs before that call;
   a previous prepare with no notion_rows is not sufficient. Preserve provider
   success and repair only the refused metadata write.
3. Prepare a multi-page batch with one invalid row. No part of that batch may be
   executed from the refused output. Modified parameters require new preflight.
4. Complete an approved email with channel-local current status/result including
   its actual message ID and provider status. Later SMS progress and customer
   reply/stop must not leave a contradictory current SMS or receipt negative on
   that closed email page. Keep receipt observations dated and history intact.
5. Feed the old stale action fetch to outcome verify even with correct normalized
   JSON. It must refuse. Repair only current display/observation labels, read
   back the original action, and verify no Notes/send/provider-attempt changes.
6. Recheck five-command behavior, Manual isolation and report-only boundaries on
   the installed version. Offline tests and manual maintenance do not substitute
   for observing the installed model's execution order.

Existing private Dropbox-link permission, full image/attachment delivery,
SMS own-number/receipt/inbound readiness, concurrency and runtime cadence are
still explicitly unverified. This change does not treat them as passed.
