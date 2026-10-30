# Notion edits

## Command-specific payloads and actual outcomes

The 2026-10-30 current connector accepted `insert_content` with `content`, required `replace_content` with `new_str`, and used `content_updates` containing exact old_str/new_str pairs for `update_content`. Do not generalize one command's key to another. Recheck current schema/documentation and actual error envelopes. A successful wrapper can still contain an APIResponseError/status/error_code; inspect the real outcome, then fetch the original affected record. A refused projection update never repeats a CRM Note or customer send. These are observed adapter details, not a promise that future connector contracts stay identical.

Scope: saved Notion text versus connector match behavior. Evidence: B113 hub-native-legacy-small-edit, report-summary-anchor, report-filename-link; the native-section refusal was also observed in 0.1.12.

## Small is not the same as safe

A legacy queue row containing two native mentions still failed exact matching. Splitting a native-reference section into a shorter native-reference line is not a verified recovery. Named and self-closing mentions may serialize differently from their displayed fetch text. The section helper refuses changed native-reference sections, but an agent can still bypass that check by constructing another raw update; do not do so.

Use an existing uniquely matched plain-text heading/adjacent line or an actually available supported block operation. Keep workflow-owned text status separate from native links when creating new layouts. If no safe operation is available, retain the original links and record the unresolved presentation issue; use explicit setup repair instead of inventing a block API or defaulting to whole-page replacement. Preserve original answers and exact native child tags. B113 recovered one queue projection through a unique plain-text anchor and an isolated current row; that does not prove every legacy queue can be edited by the same recipe.

Verify: fetch after the actual rejected call, check the precise current section and child preservation, and update only the missing projection. No Notes append or send is repeated for display repair.

## Current and historical summaries must have distinct anchors

Appending the old paragraph to history can make the old paragraph match twice. Match the current heading AND its adjacent latest saved text. Re-fetch after a mismatch; do not reuse a cached unescaped string when Notion has escaped braces or punctuation. Do not brute-force variants, replace all matches or erase history.

## File names are literal text

Notion auto-linked the bare name REPORT.md to a fake HTTP host. Code-format file/Skill names before publication. Use native references for Notion entities and explicit external links. Run the proposed-text check, then typed page-links on the actual saved page body. In B113 the real saved-page finding blocked completion until the report-owned text was corrected. A repaired report is not evidence that business tasks were executed or all historical pages were checked.
