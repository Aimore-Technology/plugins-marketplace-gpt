# EightDegrees Sales Workflow 0.1.46

The first actual 0.1.45 scheduled cycle reported six ready events but supplied only two customer-selection candidates to scan.cycle. Draft preparation was then deferred for its 600s estimate while omitted 90s intake work could have fitted in the remaining 100s. The issue was incomplete queue construction, not an idle mailbox or unavailable native identity.

scan.queue now constructs the full candidate set from the saved EventIndex and actual current task/source captures. It accounts for every ready event as ready, waiting, scoped block or original terminal readback. scan.cycle merges missing constructed candidates automatically, retaining original scopes, attempts and estimates. scan.watches exposes stable recovery records for validated Automatic read/draft preparation before idle detection; unchanged ready state remains backlog. Future work and real human waits stay waiting. Send/factual approval is never synthesized.

Original authorized-capture replay: six ready events accounted for, six candidates, remaining100s correctly selects the original90s ReadMessageBody instead of declaring only two600s draft phases deferred. The replay is offline evidence, not a new native run. Native work metrics and source/task receipts remain separate from automated tests.

All original stop, current account scope, exact email/CRM review, SMS standing policy, window/count and accepted/unknown no-resend protections remain. No new scheduled task, unique executor, scheduler-management verification or global serialization prerequisite is introduced. The current rule loader reports its package_root for fresh helper resolution.

Live acceptance remains explicit: verify actual latest-version cycles, complete next pointers, real stop and restart recovery using the original task. No claim of full local reliability merely from release or a passing guard.
