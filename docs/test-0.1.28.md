# 0.1.28 verification

Run python3 -m unittest discover -s tests -v, check-marketplace.py and package.py.
Regressions reproduce missing client_id/localized headings, top-level Sent RFC,
pointer-only approvals, distinct recovery targets, stale input-digest candidates,
changed-version unknowns, budget admission and the single controlled SMS slot.
Negative cases preserve foreign-customer/thread/version rejection, quoted-only
receipt rejection, conflicting RFC rejection, unknown/expired slots and NoSend.

Three original private 0.1.26/0.1.27 capture replays now return successful plans
without editing original proof. This is local evidence only. Live fresh-install
coverage uses public init/add-communication/reply-draft/run-auto/report, ordinary
Notion inputs and five scheduled-equivalent scans. No start/stop; old stopped or
unknown attempts stay intact. Separate mail/CRM/network/handset and native-cloud
results, actual timings, open failures and version transitions in the final log.
