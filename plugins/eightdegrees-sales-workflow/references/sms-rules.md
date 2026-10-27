# SMS cycle rules

- First due: actual material send +30 minutes. Second due: first actual follow-up +24 hours, never first planned time.
- Default customer window: Mon-Fri 10:00-17:00 Australia/Adelaide, respecting DST and configured no-send dates. Outside the window, roll to the next permitted day 10:00; do not send early to fit the window.
- No verified holiday list: require the operator's confirmation that the specific approved sending date is allowed. Each approval has an explicit earliest/latest datetime and timezone. Expiry/window changes require a new approval.
- Each SMS needs its own version-bound approval. Manual and AI related follow-ups count together toward TWO per cycle; internal operator reminders do not count.
- One active cycle/customer. Duplicate material events or resend do not reset it. Unknown send result/count suspends later sends and reserves the attempt until reconciled.
- Store CycleId, material event/source/version, actual material time, each manual/AI send time/AttemptId/provider result, current count, earliest next due, approved window, last reply check, pause/cancel/stop reason and handover status in the communication/task record.
- Reply/rejection/complaint stops unsent cycle messages before processing the reply. Do-not-contact blocks future enrollment. Read the operator's manual pause immediately before sending. Unconnected-channel replies are not observed automatically.
- Gate automatic SMS on actual own-number display, stable send, and replies visible in the operator's ordinary message app/inbox. Unverified: draft + the operator manual send/log only; do not substitute a service sender ID.
