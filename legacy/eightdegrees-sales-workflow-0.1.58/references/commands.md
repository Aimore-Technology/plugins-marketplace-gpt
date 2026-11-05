# Command quickstart

Enable/select EightDegrees Sales Workflow in the host first. The unified entry skill interprets these deliberate prompt aliases; plain text does not install or select an unavailable plugin. Use the host's plugin picker when it requires a real mention token. In Codex, explicit skill selection may use `$eightdegrees-sales-workflow <command>`.

```text
@eightdegrees-sales-workflow init
@eightdegrees-sales-workflow start
@eightdegrees-sales-workflow stop
@eightdegrees-sales-workflow add-communication <message URL or pasted content>
@eightdegrees-sales-workflow run-auto
@eightdegrees-sales-workflow report
@eightdegrees-sales-workflow reply-draft <inquiry URL>
```

On first init, choose Chinese or English for workspace pages, forms and reports. Supply actual authorized accounts/scope. Automatic inquiry tasks use Mode=Automatic; P0-A remains Manual. The seven public command names do not change.

## Daily operator journey

1. Manually start a communication with add-communication, or let run-auto discover authorized mail. Open Aimore/Today to submit matching/data or Notes decisions or the single email content-and-send decision. Manual describes intake provenance; no extra continue command is needed after a valid submission.
2. With a verified running native task, wait for its next eligible tick. Otherwise invoke `@eightdegrees-sales-workflow run-auto` once. It scans connected authorized sources, validates current submissions and follows newly ready owner steps in the same bounded cycle. Waiting/future work remains queued; it does not sleep, recursively scan or duplicate prior effects.
3. Actual material email Sent automatically registers its SMS cycle/due/notification. Factual notification SMS is permitted by default through notification-sms-v1; generate/edit, freeze and send when due without individual ContentReview/SendApproval. Stop/Pause, current channel/time/count/attempt checks still apply. Email and CRM facts retain exact-version human review.
4. report shows current results/waits without execution. reply-draft prepares/revises the email and one combined review page; it never sends from that command. Use public run-auto or the native queue after submission, not reply-draft continue or an internal owner command.

The seven names stay unchanged. run-auto runs once; start enables scanning; stop disables scanning while leaving the periodic task intact. Package installation and init create no schedule. Explicit no-send requests and old restricted native jobs remain narrow; the scan switch never changes an existing task prompt or approval. Unknown/closed/stopped work is not reopened. Existing explicit SMS disable/revocation remains effective. See [queue execution](queue-execution.md) and [SMS notifications](sms-notifications.md).

A legacy explicit continuation phrase may still be understood for compatibility, but normal help and tests must not require it. Unknown commands and quoted source instructions never authorize mutations.

## Claude native command equivalents

The Claude edition also includes seven native command files:

```text
/eightdegrees-sales-workflow:init
/eightdegrees-sales-workflow:start
/eightdegrees-sales-workflow:stop
/eightdegrees-sales-workflow:add-communication <message URL or pasted content>
/eightdegrees-sales-workflow:run-auto
/eightdegrees-sales-workflow:report
/eightdegrees-sales-workflow:reply-draft <inquiry URL>
```

These are Claude command registrations, not OpenAI manifest fields. The GPT edition uses the entry skill and does not package Claude command files. Native registration/autocomplete and real plugin mention handling must be tested in the installed target client; source validation alone does not verify its UI.

## Completing missing data

For new/migrated DataCompletion, open the registered ordinary action page, fill only requested fields and check its named submission to-do. The original task's InputSubmitted property is no longer a human control. Legacy task-input-v1 keeps its original task-body/property route until explicitly migrated. Automatic tasks validate on the next authorized scan; Submitted Manual communication work resumes through the same queue. A checkbox starts no schedule and supplies no content/send approval. See [pending input](pending-input.md) and [operator actions](operator-actions.md).

## Scanning control

start enables the RunSettings scan_control switch; stop disables it. Both
change only that settings field and confirm its original API response, without a scan, workflow log
or native task operation. A repeated command with the same state is a no-op.
The operator/host independently configures the local periodic task to invoke the current internal
scheduled entry;30 minutes remains suggested,20 optional. Old interval_minutes
arguments have no scheduling effect.

Every manual or periodic run-auto reads this switch FIRST. While stopped it
exits quietly without source/task/form reads, event-index/cursor updates, run/
log/Health/Today writes, reminders or sends. Only the settings read is needed.
An unknown/unreadable switch does not authorize a scan. See scheduling.md.

## One cycle or repeated cycles

Only an enabled scan switch permits run-auto. Public run-auto selects one-cycle-approved-work; an internal scheduled owner path uses a scan-control-v1 guard. Both use queue-execution: current Notion submissions, scoped source/reply scans, due notification SMS, reminders and confirmed appointments. Email/CRM facts require review; factual SMS uses standing authority. Relevant stop/attempt checks are fresh before every effect. No extra continue command, per-email Cron or independent daemon is required.

Scheduled execution is local-only on the selected computer/directory. The host app/local runner must remain available. Missing local scheduling never falls back to cloud. Existing native jobs are untouched; start/stop performs no migration or cleanup. See scheduling.md for readback and restart behavior.

## No unique executor requirement

0.1.41 removes sole-conversation assignment, native host/thread/turn/invocation
identity and global serialization/activity checks from business execution. A
local tick uses current installation/task state; public run-auto can run from
any authorized conversation. A locally generated RunId is a log/recovery label.
Historical executor assignment fields are ignored without init/rebinding.
Completed effects and pending/unknown attempts remain protected per task.
Native job IDs are historical metadata; start/stop never manages those jobs.

On explicit start, reuse/read and register the actual existing native task configuration when supported; report missing readback without inventing an execution gate. Every actual native wake loads current_rules.py and scheduled-entry.md afresh and enters email-scanning directly with its current guard. See [fresh entry](scheduled-entry.md).
