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

1. Open Aimore/Today and the current action-page link. Fill requested data, or review full same-version material and submit a decision. Content confirmation and sending approval are separate.
2. With a verified running native task, wait for its next eligible tick. Otherwise use `@eightdegrees-sales-workflow run-auto`. This one cycle checks new mail and continues independently approved Automatic work, including eligible email/SMS sends. No extra owner command or chat send confirmation is needed for an unchanged approved package.
3. After a verified material email Sent event, the workflow automatically registers/reuses the SMS cycle, first due time and draft/review or blocking reason. SMS still needs its own exact-message approval and a verified enabled channel. Follow-up registration creates no per-email Cron job. The one shared executor checks due work.
4. `report` shows current results/waits without execution or notifications. `reply-draft <inquiry or current action URL>` only prepares/revises content and separate send approval. There is no `reply-draft continue` subcommand; use run-auto after an Automatic submission.

`run-auto` runs once; `start` enables repetition. Neither supplies content/send approval or turns on an unverified SMS channel. An explicit no-send request stays restricted for that entire invocation. Old cached/no-send native jobs do not gain send scope on package upgrade: explicit start plus actual native readback is still required. The 0.1.23 public run-auto behavior deliberately replaces the old preparation-only shortcut.

For Manual communication only, after submitting the original review:

```text
@eightdegrees-sales-workflow add-communication continue <registered action URL>
```

That phrase is not approval. The owner checks the active binding/version and resumes only approved unfinished Notes/persona steps. Automatic scans never adopt Manual tasks. New reply-draft tasks use Automatic mode; legacy Manual sales/SMS records keep their mode and cannot be silently migrated into sending.

Unknown command or the plugin mention alone shows help without business writes. A bare link is not execution authorization. Native selection/autocomplete remains a host capability.

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

For new/migrated DataCompletion, open the registered ordinary action page, fill only requested fields and check its named submission to-do. The original task's InputSubmitted property is no longer a human control. Legacy task-input-v1 keeps its original task-body/property route until explicitly migrated. Automatic tasks validate on the next authorized scan; Manual work still requires its owner's explicit continuation. A checkbox starts no schedule and supplies no content/send approval. See [pending input](pending-input.md) and [operator actions](operator-actions.md).

## Periodic scanning

After setup, `start` creates or reuses one native 15-minute task; `stop` deletes
that task. `run-auto` still runs once. Start/stop manage schedules only: they do
not immediately process mail, approve work or send customer messages. The native task calls email-scanning directly under the guarded scheduled-approved-work policy; it retains its native guard instead of masquerading as a deliberate public invocation. Actual host support and task
readback are required; unsupported exact timing/deletion remains explicit, not
an hourly fallback or a fake local-state success. See [schedule lifecycle](scheduling.md).

## Same business gates, different repetition

Public run-auto selects one-cycle-approved-work. A real native invocation selects scheduled-approved-work only after its lifecycle/operator guard passes. Both check Automatic inputs and each owner's exact approval/version/window/stop/count/channel/attempt evidence. Neither takes over Manual P0-A. Explicit no-send contexts remain one-cycle-no-customer-send through all helpers. No per-email schedule, independent daemon or private owner command is required.

GPT targets a cloud Work GPT task; Claude targets Cowork native cron. Account scheduling and future ticks remain unverified until observed. See [schedule lifecycle](scheduling.md) and [material handoff](material-handoff.md).
