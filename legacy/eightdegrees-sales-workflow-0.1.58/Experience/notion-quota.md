# Retain capability degradation

Evidence: controlled 0.1.18 run, scan 4. SQL/rows returned usage_limit_reached;
supported complete saved views recovered source identity/dedup coverage. That
did not restore SQL. No customer IDs or mailbox contents are needed for this tip.

Use registered saved views for normal recurring discovery. After an actual
SQL/rows quota refusal, retain that capability's error in Health/logs and avoid
the same blocked route on later cycles. Use supported view pagination and exact
original-page reads with an explicit coverage record. Reprobe only on provider
reset timing or a deliberate capability recheck, not every 15 minutes.

An access error is not a quota reset. Incomplete views block absence-dependent
creation and complete-scan claims; missing latest-reply coverage blocks sends.
Verify recovered coverage separately from the still-Degraded capability.
