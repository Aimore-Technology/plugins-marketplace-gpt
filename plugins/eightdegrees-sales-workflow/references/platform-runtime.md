# OpenAI runtime

This is a skills-only Agent Plugins 1.0 package for ChatGPT/Codex. It carries no MCP server, connector credentials, hook, scheduler or cloud worker. Use the customer's separately authorized Notion, Gmail, Dropbox, CRM and optional SMS/Calendar tools only when available in the current host. Installing these skills does not install or authorize those services.

Default to manual/on-demand execution: initialization, manual P0-A, one scan cycle, approved replies, due follow-up checks and brief updates. A manual invocation may process eligible Automatic tasks for that cycle; it does not create a background service. The operator explicitly continues existing Manual P0-A tasks.

Cowork Scheduled tasks are the established Claude execution option, not an OpenAI capability. Keep scheduling disabled in the OpenAI installation until the actual host exposes an authorized scheduler with access to these skills and connectors, and cadence/recovery are verified. Do not claim that GPT can create Cowork jobs or silently substitute ChatGPT reminders for a connector-enabled workflow. Record unavailable timing and notifications honestly; manual tests can proceed independently.

Invoke packaged skills through the host's supported invocation interface. If none is provided, read the target SKILL.md and relevant references and follow it in the current session with the same IDs/version/mode; do not invent a tool name. Helpers never start a second scanner.

If Claude already owns the scheduled workflows for the same customer Notion, GPT may prepare/review work but must not compete to send or resume owned actions. Save a single executor choice in RunSettings; ownership uncertainty pauses that action for reconciliation. Notion is not an atomic lock.
