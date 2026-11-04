# Execution experience

Normal inquiry email uses [the short flow](../references/email-flow.md) and
[project cache](../references/project-cache.md); no extra experience-card sweep.
One combined content-and-send review is the current default. Notification SMS
has no per-message human review. API acknowledgements/IDs complete own writes.

Open only a relevant exception card when an actual problem occurs:

| Observed issue | Card |
| --- | --- |
| Quoting or supported Gmail update contract | [Stored reply](mail-delivery.md) |
| Native preview publication | [Preview](preview-evidence.md) |
| Completed task missing from results or submitted form still requests input | [Task state](task-results-and-submissions.md) |
| Notion targeted edit rejected | [Edits](notion-edits.md) |
| Notion quota/pagination | [Quota](notion-quota.md) |
| Garbled incoming body | [Mail decoding](../references/mail-decoding.md) |
| Wrong pending route or old source identity | [Scoped repair](scoped-recovery.md) |
| Actual provider boundary/unknown request | [Provider](provider-handoff.md) |

Retained old repair helpers/cards describe their own frozen records, not stages
to reinsert into new inquiries. Never replay an accepted/unknown effect or grant
sending from old content-only Confirm. Offline checks are not live unattended
or latency evidence. Keep business data/credentials out of distributed cards.
