# EightDegrees Sales Workflow 0.1.18

Make saved email previews easier to verify and add a native Notion PNG option rendered from the exact frozen HTML.

- Resolve saved native sources from both top-level references and metadata.references, including when an unrelated top-level map exists. Reject conflicting mappings. The original 0.1.17 checker already supported the nested map; the live test driver omitted it while assembling evidence. Withdraw that diagnosis rather than describe it as a Notion capability failure.
- Add preview-reference to produce an actual download plan and preview-image to verify original HTML, render manifest/version, native saved image/map and exact downloaded PNG bytes/dimensions. Image results have a separate completion kind bound to HTML digest and content version.
- Package an optional Node/Playwright renderer that uses existing local capabilities, freezes source/output digests, disables document JavaScript, refuses incomplete/external assets and protects earlier output versions. It does not install dependencies, upload, approve or send. Cloud Work/Cowork browser availability remains unverified.
- Route sales-reply to concise Experience and image-preview guidance. Preserve original HTML, inspect actual PNG/copy/assets and retain customer Pause, invalid approval history and exact stored-draft transport. Technical repair does not grant approval.
- Record current Notion command-specific payload lessons and preserve failed history separately from follow-up recovery. A projection repair never repeats a CRM write or customer send.

## Verification

- 210 offline unit tests passed in each edition, including 12 new mapping/image/version/failure regressions.
- Seven local browser scenarios passed: frozen source/PNG manifest, earlier version protection, wrong digest, external resource refusal, other local file refusal, broken image refusal and valid inline image rendering with document JavaScript disabled.
- Marketplace/frontmatter/reference gates and deterministic archive inspection passed for both editions. Shared changed business sources are identical; platform manifests/runtime guidance remain distinct.
- The preceding live 2026-10-30 probe verified native Notion PNG save/download identity and the original saved HTML bytes; the original missing-mapping diagnosis was corrected. It was a targeted follow-up, not a rerun of all commands. The packaged renderer was then exercised locally for this release.
- No new live customer sends, CRM mutations, native schedules or approval decisions were made by this release work. Full cloud runtime, received EDM/assets and all email-client visuals remain separate acceptance.
