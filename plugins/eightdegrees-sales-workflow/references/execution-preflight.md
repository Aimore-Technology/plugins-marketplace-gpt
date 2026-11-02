# Prepare, persist, then execute

Apply [phase ordering](phase-ordering.md): new plans are execution-v2, with one
current ResumeStep per plan. Each task resource includes resume_step. Preparation
rejects mixed phases and derives their minimum evidence; do not enumerate future
send tasks in a current content-review completion plan.

Use `python3 <plugin>/scripts/execution_preflight.py prepare --input <capture.json>`
before the owner's first dependent write. This is the shared entry for fact,
Notion property and stored-reply parameter checks. It derives the completion
check list from the affected resources instead of asking the model to assemble
that list from memory. It calls no connector and cannot intercept direct MCP calls.

For every actual Notion page write, including provisioning before ready, apply
[exact-call Notion preflight](notion-mutation.md). Its combined links/properties
check runs BEFORE that call and returns the exact permitted arguments; an earlier
prepare/schema pass does not validate a later modified body or property object.

## Input and generated plan

New plans include execution_plan.run_properties generated from the installed
manifest and actual invocation. Merge those exact fields into the initial
WorkflowRun; do not copy identity/version from a previous run/checkpoint.
execution.ready rejects missing/different metadata in its actual saved run.
Use local run.record when preparing a run outside an owner-plan path. Exact
Notion mutation checks reject omitted metadata before new run creation, including
reports. Retain old frozen plans/history; do not blanket-upgrade old versions.

Supply owner_skill, actual policy, invocation_id, publication_version, operation,
resources and the actual proposed inputs. Operations are content, review, scan,
setup, schedule, report, recovery and reply-patch. They describe this phase;
they do not widen the command policy. Content requires facts. Every actual
customer-fact projection includes facts even in another operation. Reply-patch
requires reply: the actual reply_transport manifest wrapper. It preserves the
current scalar header contract and exact frozen bytes, never joins a guessed list.

For each proposed Notion row/property write, notion_rows contains role,
data_source (the original schema fetch), data_source_id and exact properties.
Reuse the same schema capture within this phase; do not invent select values.
An empty notion_rows list does not mean future property writes are validated:
check their exact current properties with schema-values before those calls.

Each resource has a unique lowercase role, type and entity_id (actual ID, or
null for an explicitly planned creation). Types generate these checks:

| Type | Checks and bindings |
| --- | --- |
| run | page-links; exactly one owning run |
| task | page-links + route + task-summary; content_version and resume_step required |
| action | page-links + task-display; task_role points to this owner's task |
| publication | page-links |
| html-preview | page-links + preview |
| image-preview | page-links + preview-image; frozen content_version and html_sha256 |

Minimum evidence is generated from the current resume_step. A task may additionally declare compatible evidence: reply-draft, reply-sent, outcome, crm-receipt and material-handoff,
as required by its actual route. These are obligations, not fabricated successes.
Include every affected task/action/publication role and required send evidence.
The owner profile supplies minimum coverage, not discovery of omitted resources.
Declare the returned-new-action and preview roles before a Return revision;
downstream owners make their own plan before mutating their records.

For example, a no-send reply's resource slots are:

```json
[
  {"role":"run","type":"run","entity_id":null},
  {"role":"review","type":"task","entity_id":null,"content_version":"reply-v2","resume_step":"ReviewReplyDraft"},
  {"role":"review-input","type":"action","entity_id":null,"task_role":"review"},
  {"role":"html","type":"html-preview","entity_id":null}
]
```

Include a PNG role only when producing that optional preview, with its real
frozen HTML digest. Add the task's reply-draft evidence when preparing a real
stored draft. Do not introduce fake resources to satisfy a profile.

## Fixed sequence and refusal handling

1. Inspect the actual source/state/schema; generate content locally as needed.
   Run prepare and inspect BOTH process exit and JSON status. Only integer exit
   0 plus PreflightPrepared is a successful preparation. On failure it returns
   no execution_plan or usable outputs: stop dependent calls, preserve the
   refusal and correct the source input before rerunning. A failed check must
   not be followed by creating the next run/task/draft first. Recording the
   failure in the existing own run/log is allowed; it is not business progress.
2. Persist exactly execution_plan and plan_sha256 in one JSON fenced block in
   the owning WorkflowRun. For a new run, include it in the initial inert run
   creation after preparation passes. Register only the declared new resource
   slots, checking exact schema/tool inputs before each creation. Do not make
   review controls actionable, accept inputs or execute CRM/sending in this
   provisioning phase. Log actual returned IDs before their dependent use.
3. Fetch the actual saved run once. Run `execution_preflight.py ready --input
   <readback.json>` with prepared (the original prepare output), saved_plan
   (the original successful Notion fetch), and bindings (role to returned ID
   for predeclared null slots). Only exit 0 plus ExecutionPlanReady permits the
   dependent phase. It rejects missing/ambiguous/different saved plans, omitted
   results, incomplete captures, added roles, existing-ID replacement and
   unresolved slots. Keep the generated registry/required_checks for the owner
   completion gate, including its execution-plan evidence kind with this ready
   result and actual exit code. The final gate binds it to this saved plan digest,
   run, invocation and publication version; do not drop that generated check.
   Add actual log source IDs and required schedule evidence
   without weakening scope. Report retains its narrower report-write registry.
4. Consume only the current permitted input/owner step. Execute the named checks
   on actual captures, then apply owner-write or report-write and read back the
   affected final results. ExecutionPlanReady is not route approval, completion
   evidence, a send permit or proof that historical tool calls were ordered well.

A schema/input/affected-target change invalidates its preparation. Unexpected
new dependencies stop the phase: preserve the missing-plan finding, prepare and
persist a new scoped invocation/phase before that new work. Never replace the
old plan to make past actions appear compliant, or regenerate a plan merely to
remove a failed obligation. A later passing plan does not clear an earlier
order failure. Acceptance examines actual tool order and original saved plans.

Use the package helpers rather than an improvised multi-command driver. When
host scripting is needed, use Python 3 and standard serializable JSON objects;
do not assume JavaScript structuredClone or catch a failed assertion and then
continue to a mutation. Missing Python support leaves this path unverified;
do not pretend checks ran. The host still controls connector execution.

For a sales material-send plan include `material-handoff` in the original task's evidence array before execution. This binds downstream registration to the same completion contract; run [material handoff](material-handoff.md) verify on actual saved pages before final completion. Plan the downstream SMS owner separately; a blocked channel still gets an observable registration/task, never another email.
