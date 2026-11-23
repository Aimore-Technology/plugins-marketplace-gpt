# Authorized SMS connector setup

Use [provider handoff completion](provider-boundary.md). A configured authorized
AndroidSync sending tool/device is sufficient for factual notification dispatch;
no live delivery test, phone observation, stability trial or inbound-reader
check is a sending prerequisite.

Create one DataCompletion/PrepareSmsFollowUp action only for actually missing
connection/device, configured sender or recipient information. Prefill known
values and ask only for the missing business input. Preserve cycle/task IDs and
standing permission; do not ask for single-message approval or a test destination
when the ordinary authorized destination is already configured.

Record unavailable inbound capability separately and keep normal customer
reply/stop observation in authorized connected sources. Do not claim two-way
SMS support, and do not turn that capability gap into delivery-verification work.

A successful original request response closes our dispatch, including
AwaitingPhone/PendingApproval. Persist its original ID/status and our result,
Health and used count once. Do not call get_message_status, ask the operator to
check a handset or create a reconciliation task solely to wait for the service.
Only an ambiguous/unacknowledged handoff retains a reserved original attempt;
never issue a replacement request or automatically query it.

The sms.channel-check helper accepts channel_verified=true for an actual saved
configured connector/device and does not require inbound_reader_available.
Its older controlled_sms_test arguments are retained only to interpret an
explicit already-authorized legacy diagnostic scope. They are not required for
new initialization or ordinary dispatch and never reset attempts or pauses.
