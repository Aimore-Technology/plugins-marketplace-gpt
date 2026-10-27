# Command quickstart

Enable/select EightDegrees Sales Workflow in the host first. The unified entry skill interprets these deliberate prompt aliases; plain text does not install or select an unavailable plugin. Use the host's plugin picker when it requires a real mention token. In Codex, explicit skill selection may use `$eightdegrees-sales-workflow <command>`.

```text
@eightdegrees-sales-workflow init
@eightdegrees-sales-workflow add-communication <message URL or pasted content>
@eightdegrees-sales-workflow run-auto
@eightdegrees-sales-workflow report
@eightdegrees-sales-workflow reply-draft <inquiry URL>
```

Initialize actual operator/account/scope values first. Missing values are requested rather than guessed. `run-auto` runs once and prepares/validates automatic work without sending customer messages or enabling a schedule. Existing approved messages remain pending for a separately requested execution. `report` updates Notion and shows links without sending notifications or changing appointments. `reply-draft` never sends. `add-communication` defaults to manual review before CRM writes.

After reviewing a Manual communication task, explicitly continue it:

```text
@eightdegrees-sales-workflow add-communication continue <PendingTasks URL>
```

The recorded content approval must still be valid; this phrase is not approval. Unknown command or the plugin mention alone shows command help without changing business records. Automatic scanning never takes over Manual tasks.

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
