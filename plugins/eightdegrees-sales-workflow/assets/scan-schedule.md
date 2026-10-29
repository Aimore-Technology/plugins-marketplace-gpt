@eightdegrees-sales-workflow run-auto

EightDegreesOwnerKey: {owner_key}
InstallationRoot: {root_url}
OperatorId: {operator_id}
Mailbox: {mailbox}
ScheduleGeneration: {generation}

Run exactly one scan using the installed EightDegrees plugin and the current
RunSettings in this Notion installation. This is a scheduled invocation, not
permission to start another schedule. Before business work and between steps,
check the saved scheduling enabled/desired state, generation, actual task ID
and single executor. If stopped, superseded, busy or ownership is uncertain,
exit without taking over another run. Never catch up by launching parallel scans.

Use CustomerSendAllowed=false throughout. Process only eligible Automatic
tasks; Manual tasks require an explicit operator continuation. Preserve source
deduplication, accepted input, approved versions, stop conditions and prior
attempts. Unknown external results need reconciliation, not another send.
Do not create schedules, approve your own work, send customer email/SMS or
broaden connected accounts or mailbox scope. Use only configured internal
notifications. Stay quiet when nothing actionable has changed. Surface new
operator actions, meaningful failures and recovery with original Notion links.
Save actual run/checkpoint/log evidence; do not claim success for unavailable
tools, missing sources or incomplete coverage.
