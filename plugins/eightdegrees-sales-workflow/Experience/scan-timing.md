# Scan timing and cadence

Trigger: choose a recurring cadence or explain a slow completed scan.

The seven-cycle 0.1.29 local simulation observed dispatch-to-saved-completion
times of 350, 224, 113, 96, 547, 493 and 669 seconds. Their average was 356 seconds;
the three active processing/sending cycles averaged 570 seconds. Executor log
snapshots used a different boundary and averaged 328 seconds. Label the clock
scope, queue/publication overhead and waiting versus active work separately.

New configuration defaults to a 30-minute native scan, with explicit 20-minute
selection, and a 900-second soft cycle budget including a 120-second result
publication reserve. These are operational choices, not measured speed gains.
Keep 12 owner steps and one fresh admission at a time. Stop new work at minute
13, persist the checkpoint and let the next tick resume; do not interrupt or
resend an in-flight effect to meet the interval. A longer interval never proves
exclusive execution or resolves an unknown outcome.

Verify the selected native cadence and prompt on the same owned task ID. Preserve
an operator's saved 20-minute choice and explicit custom budget. Package upgrade
does not edit a live schedule; explicit init/start adopts defaults and reconciles
legacy tasks. Keep historical 480-second overrun evidence under its actual old
limit. Timing issues and confirmed business outcomes remain distinct.

Verification: offline scheduler transition/readback and admission-boundary tests
cover both runtime names, exact 20/30 selection, old-task deletion/update, new
publication reserve, overlap deferral and preserved unknown/completed results.
No live native GPT task or Cowork cron cadence is certified by these tests.
