# Actionable SMS channel setup

An unverified channel needs ONE DataCompletion/PrepareSmsFollowUp task under
the SMS owner, with a task-input-v2 ordinary action page. Link it from the
blocked notification result and Today; a read-only reason/settings link alone
is insufficient. Preserve the original notification/cycle and deduplicate by
setup scope/version. Standing notification authority is not asked again.

Show only prefilled sending phone, authorized check destination, normal-phone
inbox reply visibility (yes/no/unknown plus observation time), connected reply
reader (actual tool or unavailable), multiline observations, and setup choice:
keep blocked / save connector details / run one controlled channel check.
Workflow supplies exact device/CRM/task/version bindings. User answers cannot
set a verified flag or certify an unavailable inbound tool. run-auto validates
the actual submission and continues the same named phase.

If init context already explicitly requests the check, register that original
authorization and prefill the choice; do not ask again. Save controlled_sms_test
with original authorization/input reference, enabled=true, exact configured
recipient/device/sender, context_key, max_messages=1, expires_at and original
attempt/result pointers. Bind its actual frozen notification to verified material
Sent. Keep >=Sent+30m unless an explicit diagnostic timing waiver is recorded;
that waiver never changes production delay defaults.

run-auto executes through the normal SMS owner/standing authority and actual
Trusted device route. Only the disclosed stable-send/inbound-read capability
requirement may remain unverified for this bounded check. Fresh stop/reply/Pause,
device ownership, exact recipient/body, count, window/expiry and unknown-attempt
guards still apply. Reserve the ONE slot before request; Unknown reserves it
and never creates a replacement send. Never release an abandoned old request.
No private Skill/continue, native task or extra approval is required.

Record network acceptance, delivery and actual handset receipt separately.
Ordinary channel readiness stays unverified until demonstrated; one phone
observation cannot create an automatic inbound reader or permit a second SMS.
This is a controlled channel check, not unattended-channel acceptance.

## Local check arguments

Run sms.channel-check with invocation_policy, context_key, now, actual
channel_verified/inbound_reader_available, payload={recipient,device_id,sender_number},
guards={stop,manual_pause,unknown_attempt,customer_replied}, and the saved
controlled_sms_test. Its used_slots is an actual integer0/1, unknown_attempt is
explicit, and authorization_ref points to original setup input. A newly reserved
slot can continue only with matching attempt_id/reserved_attempt_id and
provider_result_present=false. After any provider result, reconcile rather than
requesting again. The check has no I/O, no host lock and cannot validate its own
normalized observations; the owner must read their originals.
