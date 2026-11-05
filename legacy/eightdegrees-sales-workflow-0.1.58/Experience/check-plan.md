# Freeze checks before their work

Evidence: controlled 0.1.18 run, F02. Return produced a correct new review, but
the required-check list was saved late. Functional recovery and order acceptance
are separate; the old failure remains open pending a new live regression.

Generate the full affected-role list with [execution preflight](../references/execution-preflight.md),
persist the generated plan, and verify the original saved plan before input
consumption. Predeclare new action/preview slots; bind actual returned IDs before
dependent use. Each child owner prepares its own affected scope.

Verify that a missing or late-added dependency is refused against the original
saved plan. Do not backdate a plan, transfer old approval or drop checks to pass.
