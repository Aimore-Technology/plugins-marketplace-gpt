# Important reminders

Important by default: rejection/complaint/do-not-contact; unknown send/wrong customer/CRM write failure; appointment or committed action within two hours needing action; approved send blocked. The operator may mark another item important. Normal drafts waiting for review stay in the daily brief.

Use verified SMS to the operator first, then the configured operator email address, then an available verified host-task notification. Skip unconfigured/failed channels; if SMS is unverified, start with Gmail. Do not assume WhatsApp/Telegram/Hub access.

Persist ReminderKey, original task, reason, actual first notification time/channel/result, 19-minute checkpoint, escalation result, 24-hour deadline, acknowledgement evidence/time and last notice state. Reminder email subject: `Aimore reminder - <task short ID>`. Separate it from customer inquiries; use only the configured internal-reminder read scope. Never widen customer-mail access to track acknowledgements.

At 19 minutes after actual first notification, if not acknowledged, switch to another usable channel ONCE. With one usable channel, repeat once there and record "degraded: no cross-channel escalation". At 24 hours without explicit receipt, keep overdue/unacknowledged and send one overdue notice. No repeating every scan. All channels unavailable means notification failure, shown in the current session/Dashboard; do not pretend notification succeeded.

The operator can explicitly acknowledge in the current session, on a legacy original task, or through the separately labeled receipt to-do on its registered [action page](operator-actions.md); bind that receipt internally to the original ReminderKey. Observe it only within the current workflow's mode/policy, then record actual acknowledgement evidence. Do not ask the user to fill technical reminder timestamps. Page opens, read receipts and "sent" are not acknowledgement. Receipt stops only reminder chasing; it does not submit business input, approve email sends, update personas or finish the action. Notification SMS uses the standing policy, not a reminder receipt.

Record planned and actual times. A 15-minute polling target alone cannot ensure 19-minute escalation. Verify host scheduling; late checks/manual fallback are degraded and do not pass automatic timing acceptance. Independent ordinary workflows can still be tested. Do not add a separate backend to hide the limit.

Internal reminders and 08:30 daily briefs may run outside customer sending windows. Deduplicate by ReminderKey + phase (initial/escalation/overdue); a catch-up invocation does not send every missed reminder phase at once. Send only the currently applicable unsent phase, preserve missed-phase evidence, and reconcile unknown notification results before retrying.
