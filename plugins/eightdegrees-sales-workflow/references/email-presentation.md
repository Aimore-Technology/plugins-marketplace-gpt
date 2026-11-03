# Email results and linked completed reviews

Apply [provider handoff completion](provider-boundary.md): successful Gmail/AndroidSync acceptance ends dispatch; verify our own records and CRM, with no post-handoff provider or recipient checks.

After successful project email handoff, synchronize the completed content-review task
and action as well as the original send task/action. A completed review cannot
retain current unsent-draft or send-approval instructions after that email sent.
Keep State, Mode, operator inputs, approval history, frozen HTML/preview and
immutable provider proof unchanged. Historical evidence is not a current summary.

Use `email_presentation.py plan|verify --input <input.json>` or local batch
operations `email.presentation-plan` / `email.presentation-verify`. It performs
no network I/O or business action. Input has `pages={send_task,send_action,
review_task,review_action}` containing complete original MCP fetches, saved
language and timezone-aware observed_at. It derives related IDs from the original
sales-send-package/content_approval and action bindings, and requires matching
email-handoff-proof (or already-saved legacy email-sent-proof). The send may be InProgress after actual Sent, or Completed;
the linked content review must be Completed with the same version.

If the registered RunSettings source index already embeds current_outcome for
this send/version, also supply its complete original capture as index_page.
Register it as an additional publication role. The plan patches only that exact
nested outcome value, preserving all other settings and stop/policy data byte for
byte. Pointer-only indexes need no synthesized outcome. Supply saved_index_page
for verification, even when unchanged; never leave an existing duplicate stale.

For new source-bound packages, supply source_page and declare it as a publication role. The helper matches its original incoming account/message/thread, updates its current text/Result and moves a waiting source to Processing for internal closeout. Supply saved_source_page to verify. Only AFTER presentation and all owner checks pass, prepare and apply the source_completion marker through the final owner-write gate and re-read its Processed marker. No source final marker gates its own presentation proof. Legacy packages may add a verified original source capture without rewriting their frozen package.

The plan supplies only Result properties, plain current-section/navigation
patches, review-history labels and the original current-outcome JSON on task and
action. Use `page_ids[role]` as each update's target;
run exact-call preflight and execute only checked args. Preserve native links,
operator answers and all other fields/body bytes. Retain the original pages and
add saved_pages to verify all four readbacks, plus saved_index_page when supplied,
reusing unchanged captures. Unexpected
collateral changes fail verification. A repeat yields no edits. Do not rerender
or download unchanged HTML/PNG for presentation repair.

At initial SendApprovedReply completion, freeze email-presentation evidence on
that task, with both linked completed review pages as publication roles. Require
EmailPresentationVerified alongside provider-handoff, current outcome, CRM receipt
and material handoff. It does not replace approval or the pre-dispatch draft check.

## Later receipts and legacy display repair

The scanner handles customer reply/stop as normal business input. Do not enqueue
work merely to verify recipient receipt or delivery. A scoped known stale
internal review/result can enqueue Automatic RefreshEmailOutcome for display
repair only, using the saved original dispatch acknowledgement. Reuse one task
per original send/version/presentation revision; no provider calls, new approval,
CRM replay, native schedule or receipt-only workflow.

On upgrade, the registered current DailyBrief's unresolved quality findings can
discover an implicated completed send. Read that scoped current finding and its
originals; do not enumerate all historical pages. Version/processed-work markers
only avoid duplicate discovery, never replace fresh original/provider checks.

Use the normal recovery plan: its own run/task/read-only result and the four
original pages as publication roles. Freeze email-presentation evidence on the
maintenance task; supply maintenance_task_id, distinct from all original pages.
Include the registered settings index when it embeds this result; its fifth
publication role must be covered by the same verified evidence.
Final completion needs the matching verified result and registered page coverage.
This route only updates Notion current results: no email/SMS/CRM/provider writes,
enrollment, stop reset or approval changes. report only records findings and links
run-auto; it cannot dispatch or repair this work.

Preserve existing legacy receipt metadata as history. Do not collect new receipt
proof, query receiving accounts or require any customer acknowledgement. The
legacy receipt input parser exists only for already-captured historical evidence;
new presentation maintenance supplies no receipt input. Customer replies and
stop requests continue through ordinary source/stop processing.

After a partial patch failure, retain the original plan and reconcile only missing
patches/readbacks. Do not resend email or append CRM to repair a view. Closed
legacy records lacking required proof/bindings remain scoped findings.

## Compatible original layouts

Use [record contracts](record-contracts.md). Legacy top-level RFC IDs and
pointer-only content approvals are read from matching original evidence without
rewriting it. Conflicting aliases, wrong raw MIME or missing accepted approval
remain errors; a compatibility adapter is not permission to invent proof.
