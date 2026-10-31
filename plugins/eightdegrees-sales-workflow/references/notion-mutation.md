# Check the exact Notion call before writing

Before EVERY supported Notion page write, including first source/task/action
creation, inert run creation, progress metadata, projection repair and log append,
run `python3 <plugin>/scripts/notion_mutation.py --input <call.json>`.
This combines visible-text link checks and exact proposed property/schema checks
in one local command. It calls no service and does not replace owner/report scope
checks, the real tool schema, saved-page verification or operator approval.

For a large call, add --output <checked-call.json>. It saves the exact result/call
locally and prints only checks/digest/path, avoiding a second whole-page echo.
Load that saved call unchanged for execution; the summary alone is not a call.
Do not overwrite the input/capture file. Without --output the original CLI output
is unchanged. Failed checks still return no executable call in either form.

Input contains `call={tool,args}` with the actual discovered tool and exact args.
For an update, `target` is the original successful complete page fetch. For a
child-page creation it is the original parent-page fetch. Database creation uses
the actual `parent.data_source_id`; database property updates resolve that source
from the original target fetch. Both require `data_source`, the original full
schema fetch for that exact source. Reuse a valid captured schema in this phase;
do not repeat a network read for every helper. Do not remove parent metadata to
make a database row look like an ordinary page. Ordinary pages accept only title;
host-supported private-root creation uses creation_mode=draft and no parent.

The helper checks every created page and proposed new content/patch string. For
database property writes it invokes schema-values on the exact proposed fields,
including ExternalIds on result projections. A content-only update needs no
unrelated schema read. New selects are not added automatically. Icon/cover and
other argument types still need the current host contract.

Require exit 0 AND NotionMutationPrepared. Execute ONLY its returned call.args,
without adding/changing fields; retain call_sha256 with the invocation evidence.
Any changed target/body/property means a new pre-call check. A refusal exits 2
with no executable call, including for a mixed-validity page batch. Do not create
the first page and check it afterwards, use an earlier empty notion_rows array
as approval of a later property update, or replay CRM/email/SMS after a display
write fails. Reconcile the refused Notion write and repair that projection only.

Other Notion mutation types use their actual tool contract and explicit scoped
checks; never invent a tool alias to obtain this helper's pass. Root/teamspace
operations unavailable to the current connector remain setup limitations.
The host still controls actual MCP execution: this is a mandatory Skill step,
not an interceptor or proof of historical call order.
