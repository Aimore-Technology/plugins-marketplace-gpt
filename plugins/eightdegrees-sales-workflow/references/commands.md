# Command quickstart

Enable/select EightDegrees Sales Workflow in the host first. The unified entry skill interprets these deliberate prompt aliases; plain text does not install or select an unavailable plugin. Use the host's plugin picker when it requires a real mention token. In Codex, explicit skill selection may use `$eightdegrees-sales-workflow <command>`.

```text
@eightdegrees-sales-workflow init
@eightdegrees-sales-workflow add-communication <message URL or pasted content>
@eightdegrees-sales-workflow run-auto
@eightdegrees-sales-workflow report
@eightdegrees-sales-workflow reply-draft <inquiry URL>
```

On first init, choose Chinese or English for workspace pages, input forms, guidance and reports. The saved choice is reused; it does not select the language of customer replies. Initialize actual operator/account/scope values first. Missing values are requested rather than guessed. `run-auto` runs once and prepares/validates automatic work without sending customer messages or enabling a schedule. Existing approved messages remain pending for a separately requested execution. `report` updates Notion and shows links without sending notifications or changing appointments. `reply-draft` never sends. `add-communication` defaults to manual review before CRM writes.

After reviewing a Manual communication task, explicitly continue it:

```text
@eightdegrees-sales-workflow add-communication continue <PendingTasks URL>
```

The recorded content approval must still be valid; this phrase is not approval. Unknown command or the plugin mention alone shows command help without changing business records. Automatic scanning never takes over Manual tasks.

For new/migrated tasks, use the ordinary page linked from `Aimore/Actions` to fill missing information or submit a specific content/send decision. Technical task properties are workflow detail. A Manual continuation may take that registered action-page URL instead of the original task URL; the workflow verifies its backlink and active binding before processing it. A bare action URL is not a continuation request.

## Claude native command equivalents

The Claude edition also includes five native command files:

```text
/eightdegrees-sales-workflow:init
/eightdegrees-sales-workflow:add-communication <message URL or pasted content>
/eightdegrees-sales-workflow:run-auto
/eightdegrees-sales-workflow:report
/eightdegrees-sales-workflow:reply-draft <inquiry URL>
```

These are Claude command registrations, not OpenAI manifest fields. The GPT edition uses the entry skill and does not package Claude command files. Native registration/autocomplete and real plugin mention handling must be tested in the installed target client; source validation alone does not verify its UI.

## Completing missing data

For new/migrated DataCompletion, open the registered ordinary action page, fill only requested fields and check its named submission to-do. The original task's InputSubmitted property is no longer a human control. Legacy task-input-v1 keeps its original task-body/property route until explicitly migrated. Automatic tasks validate on the next authorized scan; Manual work still requires its owner's explicit continuation. A checkbox starts no schedule and supplies no content/send approval. See [pending input](pending-input.md) and [operator actions](operator-actions.md).
