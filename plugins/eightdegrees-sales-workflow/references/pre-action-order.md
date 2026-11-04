# Short pre-action order

Normal inquiry work uses [email-flow](email-flow.md): source API acknowledgement,
one scoped CRM match, cached project facts, one prepared plain-text draft, one
combined review and one email.dispatch. It does not write/fetch a second queue
admission or repeat a whole owner preflight for every logical step.

Prepare the exact plain-text draft/version and publish ReviewText plus Consent
on its canonical task. Original draft/task API acknowledgements are sufficient;
no rendering, preview asset or review.prepare is required for new mail.
Before a provider action persist the exact decision and stable attempt once.
Reuse current task/action/control captures across local checks; refresh only
when delayed or an intervening relevant event changes them. Notification SMS
keeps standing authority and current stop/time/count checks without review.

Approved email executes at any hour; clock windows belong only to SMS.
