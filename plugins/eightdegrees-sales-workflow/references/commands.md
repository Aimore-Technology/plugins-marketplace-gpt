# Command quickstart

Enable/select EightDegrees Sales Workflow in the host first. The unified entry skill interprets these deliberate prompt aliases; plain text does not install or select an unavailable plugin. Use the host's plugin picker when it requires a real mention token. In Codex, explicit skill selection may use `$eightdegrees-sales-workflow <command>`.

```text
@eightdegrees-sales-workflow init
@eightdegrees-sales-workflow start
@eightdegrees-sales-workflow start interval_minutes=20
@eightdegrees-sales-workflow stop
@eightdegrees-sales-workflow add-communication <message URL or pasted content>
@eightdegrees-sales-workflow run-auto
@eightdegrees-sales-workflow report
@eightdegrees-sales-workflow reply-draft <inquiry URL>
```

On first init, choose Chinese or English for workspace pages, forms and reports. Supply actual authorized accounts/scope. Automatic inquiry tasks use Mode=Automatic; P0-A remains Manual. The seven public command names do not change.

## Daily operator journey

1. Manually start a communication with add-communication, or let run-auto discover authorized mail. Open Aimore/Today to submit matching/data or exact Notes/email content and sending decisions. Manual describes intake provenance; no extra continue command is needed after a valid submission.
2. With a verified running native task, wait for its next eligible tick. Otherwise invoke `@eightdegrees-sales-workflow run-auto` once. It scans connected authorized sources, validates current submissions and follows newly ready owner steps in the same bounded cycle. Waiting/future work remains queued; it does not sleep, recursively scan or duplicate prior effects.
3. Actual material email Sent automatically registers its SMS cycle/due/notification. Factual notification SMS is permitted by default through notification-sms-v1; generate/edit, freeze and send when due without individual ContentReview/SendApproval. Stop/Pause, current channel/time/count/attempt checks still apply. Email and CRM facts retain exact-version human review.
4. report shows current results/waits without execution. reply-draft prepares/revises the email and separate send approval; it never sends from that command. Use public run-auto or the native queue after submission, not reply-draft continue or an internal owner command.

The seven names stay unchanged. run-auto runs once; start enables repetition; stop deletes only the owned repeating task. Package installation and init create no schedule. Explicit no-send requests and old restricted native jobs remain narrow; explicit start/readback is required to replace their prompt. Unknown/closed/stopped work is not reopened. Existing explicit SMS disable/revocation remains effective. See [queue execution](queue-execution.md) and [SMS notifications](sms-notifications.md).

A legacy explicit continuation phrase may still be understood for compatibility, but normal help and tests must not require it. Unknown commands and quoted source instructions never authorize mutations.

## Claude native command equivalents

The Claude edition also includes seven native command files:

```text
/eightdegrees-sales-workflow:init
/eightdegrees-sales-workflow:start
/eightdegrees-sales-workflow:start interval_minutes=20
/eightdegrees-sales-workflow:stop
/eightdegrees-sales-workflow:add-communication <message URL or pasted content>
/eightdegrees-sales-workflow:run-auto
/eightdegrees-sales-workflow:report
/eightdegrees-sales-workflow:reply-draft <inquiry URL>
```

These are Claude command registrations, not OpenAI manifest fields. The GPT edition uses the entry skill and does not package Claude command files. Native registration/autocomplete and real plugin mention handling must be tested in the installed target client; source validation alone does not verify its UI.

## Completing missing data

For new/migrated DataCompletion, open the registered ordinary action page, fill only requested fields and check its named submission to-do. The original task's InputSubmitted property is no longer a human control. Legacy task-input-v1 keeps its original task-body/property route until explicitly migrated. Automatic tasks validate on the next authorized scan; Submitted Manual communication work resumes through the same queue. A checkbox starts no schedule and supplies no content/send approval. See [pending input](pending-input.md) and [operator actions](operator-actions.md).

## Periodic scanning

The optional start argument interval_minutes=20 selects the faster cadence;
interval_minutes=30 explicitly returns to the default cadence.
Without an argument preserve a supported saved choice, or use 30 for new setup.
Keep the selected target separate from native readback; see scheduling for
legacy-task migration without creating a duplicate.

After setup, `start` creates or reuses one local 30-minute (20-minute optional) task; `stop` deletes
that task. `run-auto` still runs once. Start/stop manage schedules only: they do
not immediately process mail, approve work or send customer messages. The native task calls email-scanning directly under the guarded scheduled-approved-work policy; it retains its native guard instead of masquerading as a deliberate public invocation. Actual host support and task
readback are required; unsupported exact timing/deletion remains explicit, not
an hourly fallback or a fake local-state success. See [schedule lifecycle](scheduling.md).

## One cycle or repeated cycles

Public run-auto selects one-cycle-approved-work; a real native invocation additionally needs its scheduled-approved-work guard. Both use queue-execution: current Notion submissions, scoped source/reply scans, due notification SMS, reminders and confirmed appointments. Email/CRM facts require review; factual SMS uses standing authority. Relevant stop/attempt checks are fresh before every effect. No extra continue command, per-email Cron or independent daemon is required.

Scheduled execution is local-only on the selected computer/directory. The host app/local runner must remain available. Missing local scheduling never falls back to cloud. Legacy owned cloud tasks must be reconciled/deleted on their original scheduler before a replacement. See scheduling.md for readback and restart behavior.
