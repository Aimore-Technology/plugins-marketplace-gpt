# EightDegrees Sales Workflow 0.1.52

Replace per-response save/version-observation shell work with one local phase
batch. local_checks now accepts inline named original captures with its checks;
no preliminary file-save call is required. Existing capture files still work.
New capture.commit/capture_bundle.py atomically saves a whole phase in private
local state, reuses identical original aliases without rewriting and preserves
error/warning layers. A changed original uses a new revision alias; it never
overwrites the evidence used by an earlier phase. Bundles are cycle-scoped,
outside the plugin, and cannot become current approval or stop authority.

Remove contradictory readback and blanket invalidation instructions. Own API
write acknowledgements update local projections without refetching all pages.
Unchanged idle discovery requires no local version-registration checkpoint.
Changed cursors, incomplete pagination and runnable backlog still retain their
recovery state. Persist actual source/decision/AttemptId before dependent
operations and accepted/unknown provider results at the effect boundary.
Batching cannot remove those business protections or retry a completed send.

Current scheduled rules load this phase policy and helper fingerprint on each
wake. No host task is created or changed, no unique executor is introduced,
and no native tool-call suppression is claimed. This removes avoidable workflow
instructions/capture calls; host/model compliance and live latency still need
observation on the next real scan. The prior plain-text single-review path,
project cache and standing SMS behavior remain unchanged.

Offline regressions cover 26 original inputs in one atomic write, repeated
inputs with zero writes and unchanged mtime, immutable aliases, scope boundaries,
original nested failures, interrupted writes, symlink/source protection and
single-invocation inline captures/checks. No live provider action is performed.
