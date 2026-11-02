# Avoid slow idle work and one-second handover stalls

Trigger: run-auto appears idle for minutes, a successor remains queued after its
predecessor succeeds, or run/report metadata is incomplete.

The 0.1.34 live rehearsal completed seven cycles. Its idle turn still took
210.823s and read metadata for 15 registered files. Maple mail was accepted by
Gmail, but its automatically registered notification deferred at179/180s; the
original customer cap remained0/1. Four saved-cycle timings exceeded the900s
budget. Error diagnostics for one failed discovery call were lost by serializing
an Error object as ordinary JSON. Scan SourceKey reused an old invocation, and
the report run omitted SkillVersion. These are recorded failures/limits, not
evidence of delivery trouble or permission to resend.

Apply [the short execution procedure](../references/scan-fast-path.md).
scan.watches computes active forms/current project dependencies from actual
settings, complete task rows and retained source events; mail coverage stays
unchanged. run.record and execution.prepare generate current run metadata;
exact Notion creation/update guards reject missing version or stale scan keys.
connector.capture retains both original result layers and explicit thrown-error
messages, then scan.probe preserves the diagnostic pointer through recovery.
scan.cycle now uses bounded estimate slack and next fitting independent work;
stops, unknowns and intake precede factual notifications, which precede optional
maintenance. No send is authorized by these local results.

Use one directly saved capture per response and small local check plans. Avoid
many model turns just to write/reload large capture JSON. Complete required own
records, acknowledge/register the next event, and continue before optional
monitoring publication. Actual future public-command tests must measure idle and
active elapsed time; offline replay does not establish a time/token improvement
or prove the queued live SMS was sent.
