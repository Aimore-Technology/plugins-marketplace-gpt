# Record adapter regressions

Trigger: a live0.1.26/0.1.27 simulation persisted an approved persona without
client_id, a Sent proof with top-level RFC ID, and a distinct handoff recovery
task. Later helpers assumed another shape and failed despite real Sent.

Read [record contracts](../references/record-contracts.md) before producing or
refreshing these records. Use original settings binding for legacy persona,
accept consistent original RFC layouts and pass saved_recovery_task to
material.verify. Never edit approved/provider proof to satisfy a helper.
Include every frozen page-links/task-display result, not just a later passing
subset. Record corrected behavior and remaining failures separately.

Source: development simulation2026-11-02. Synthetic replay tests cover these
shapes and negative identity/approval cases; they do not prove native cloud
runtime or live completion. Budget selection now admits one fitting step;
unchanged compatibility failures cannot justify endless repair before intake.
