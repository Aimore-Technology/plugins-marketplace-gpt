# Fresh rules on every native wake

This is an internal entry, not another public command. A native heartbeat goes
directly to eightdegrees-email-scanning with scheduled-approved-work. Do not
route it through automation-control, start/stop, or the public run-auto policy.

1. Resolve the currently installed package, not a version path cached in old
   chat text. Run `scripts/current_rules.py` from that package on every wake;
   read its current files and retain actual rule_version/rule_sha256. Load the
   current scanner and scheduled guard even in a long-running upgraded chat.
   Historical chat advice and legacy fields cannot supersede these rules.
2. Read original RunSettings FIRST. scan.entry and the current schedule guard
   determine execution from scan_control and current root/operator/mailbox.
   Explicit stop and actual account revocation remain effective. If stopped,
   exit without discovery or business/log writes. A task being ACTIVE never
   overrides a real stop. Native management availability, executor identity,
   bound thread/host, global serialization, native_runtime_verified and other
   management acceptance flags are not execution gates. Report an actual
   failing guard result, not a new prerequisite invented from old context.
3. Discover current scoped mail, submitted actions, control, due scheduled
   work, recovery pointers and necessary source metadata. Retain complete
   pagination evidence. Use scan.probe with all real observations. Commit its
   candidate index and baseline projection together. Complete/NeedsBaseline
   comes from coverage, never from a permanent setup latch. Missing coverage
   gets its feed, exact failure and recovery action; work independent of that
   gap still proceeds. Preserve original backlog, cursors and provider attempts.
4. Always consider pending events, even with unchanged mail/index/task status.
   Run scan.queue on the original saved EventIndex plus current complete task/source captures. Pass its entire result as queue_plan to every scan.cycle; never hand-select just the first owner's tasks. All pending mail, submissions, due and recovery events must be accounted for as ready, actual human wait, scoped block or original terminal readback. Enqueue validated automatic preparation from scan.watches.ready_task_records even when its row did not change; pass those records and ready_task_blocks to scan.probe.
   Run backlog.recover over complete original source/task captures. Reuse saved
   source pages; RecoverSourceHandoff repairs a missing successor separately
   from an already completed ReadMessageBody. Read only sources not yet saved.
   Use intake.plan on a prospective current checkpoint, persist/read back and
   intake.verify before dependent sales preparation. Register/reuse the original
   successor task and its review/input wake pointer before acknowledging mail.
   Continue matching, authorized project parsing and draft preparation to the
   exact review or missing-information boundary within this cycle's budget.
   No additional continue command. Failed, waiting or completed unrelated
   customer/channel/project work never becomes a global blocker.
5. Sending windows limit dispatch only. Intake, project facts and review
   preparation can run outside a window. Preserve exact email/CRM version
   approval, standing factual-SMS authority, channel/stop/time/count checks and
   original AttemptId. Accepted/unknown effects cannot be sent again. Reconcile
   our records and CRM; do not poll Gmail/AndroidSync delivery status.
6. Save cycle.metrics using actual receipts, clocks, waits, concrete blocks and
   next recovery pointers. Separate timer_trigger_verified, guard_passed and
   business_progress. No ready progress means a concrete scoped blocker and
   resume action, never silent no-change. Deduplicate fault notification by
   source/code/resume/revision, saving notice keys only after actual notification.
   ScanIdle requires complete discovery and no ready work; genuine human waits
   and future due work wait on their actual saved pointers.

After restart, run one current discovery/recovery cycle from saved checkpoints;
do not replay each missed interval. Old native tasks are reused, never cloned.
If a host cannot load the fresh entry, record that deployment limitation and do
not claim cross-version or native-cycle acceptance from an offline helper test.

A large draft phase that does not fit must not hide fitting mail or a due brief. scan.queue constructs the full candidate set and scan.cycle merges missing candidates automatically, preserving scopes/attempts. Save every remaining checkpoint pointer, not only the current owner's next task. Previously admitted Gmail pending IDs remain demand if an unchanged UNREAD filter no longer lists them; recover the saved source/original ID within its still-authorized scope. Explicit stop/revocation remains binding.

Use the actual package_root returned by current_rules.py for this wake's local helpers, not a cached path from an older chat. Re-resolve the current package on the next native wake. Execute ordinary package upgrades between active cycles when practical; do not rewrite frozen business approvals or existing attempt records.

Apply the current [inquiry intake rules](inquiry-intake.md) to newly admitted mail: add the inquiry classification label after content discovery, without requiring it for reads. Resolve names by matched CRM, current signature, From name, then anonymous Dear Customer plus a name question. Name-only differences cannot block a uniquely verified CRM association.
