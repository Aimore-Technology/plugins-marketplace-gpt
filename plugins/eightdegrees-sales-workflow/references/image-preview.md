# Native image preview from frozen HTML

Use when HTML embed display is unavailable or an in-page static preview is more useful. Keep the original HTML download and editable copy beside the image. A PNG is review material, never the email payload. HTML embed and PNG are alternatives; do not call the HTML broken merely because a checker input was incomplete.

## Render the exact version

Freeze the current UTF-8 HTML, authorized images/attachments and version manifest first. Use an available browser renderer, not a model-generated imitation. This package includes an optional local Node/Playwright renderer:

```sh
node <plugin>/scripts/render_preview.cjs --html <frozen.html> --html-sha256 <actual-digest> --version <content-version> --out-dir <new-version-directory>
```

It requires an existing Playwright module and Chromium. Normal module lookup is used; optional `--playwright-module <installed-module>` and `--chromium <installed-executable>` select capabilities actually present in the current environment. It installs nothing. Do not use development-machine absolute paths on another host or assume GPT Work/Cowork supplies a browser. If unavailable, use a genuinely supported host renderer with equivalent provenance and manual checks, or retain a non-approvable implementation exception. The packaged image checker currently accepts the packaged Playwright manifest; another adapter needs its own explicit verification, not a relabeled manifest.

The renderer checks source SHA-256, disables document JavaScript, blocks network and other file dependencies, refuses missing images and preserves existing output directories. First freeze authorized image/font bytes as data URIs in the versioned HTML if necessary; this creates a new HTML version requiring its own stored-draft sync. Never simply hide missing content. Attachments remain separate frozen files. The new directory holds `frozen.html`, `preview.png` and `render-manifest.json`: source and PNG digests/sizes, content version, pixel dimensions, browser version and actual completion/resource state. There is no upload, approval or send operation in this script.

Inspect the actual PNG: complete body, responsive layout, images, labels and readable text must agree with the frozen HTML and editable copy. The helper below checks recorded provenance and bytes; it cannot prove the browser actually rendered the claimed source or inspect its pixels. Preserve the real render command/result and inspection evidence. Retain the same HTML/PNG/assets for the review version; edits produce a new version and blank review decisions.

## Save and verify the actual Notion image

1. Upload the PNG with the current file-upload tool and place its actual returned source in a native image block using current documented syntax. Record upload ID, version and digests in technical history, not operator input fields.
2. Fetch the saved page with `include_file_urls=true`. Preserve the original envelope. Read BOTH `references` and `metadata.references`; a nonempty unrelated top-level map must not hide the nested mapping. Conflicting URLs for the same source require reconciliation.
3. Run `notion_checks.py preview-reference --input <capture.json>` with `page` (the actual fetch) and `source` (the exact saved `notion-file-block://` image source). `DownloadRequired` only supplies the actual mapped URL; it does not pass preview review. Download that URL, keep its exact bytes and actual HTTP outcome, and stop on error. Never guess from upload ID or filename. Refresh an expired mapping with a fresh authorized fetch, not a synthetic URL. Signed URLs stay in short-lived technical captures, never customer-facing links or routine logs.
4. Run `notion_checks.py preview-image --input <capture.json>`. Inputs: `page`, `html_file_id`, `html_sha256`, `download` (actual original UTF-8 HTML upload download), `content_version`, the unmodified `render_manifest`, and `embedded_asset` with `source`, `resolved_url`, `content_base64` from the ACTUAL saved-image download. This checks the native image source/map, original HTML identity, manifest/version, PNG signature/dimensions and exact saved PNG digest/size. A plain file/code block, original upload alone or unrelated screenshot cannot pass.
5. Register its actual `SavedImageAndBytesMatch` result as kind `preview-image` in the owner's frozen completion contract. Its spec contains `entity_id` (saved preview page), `content_version` and `html_sha256`. Include actual integer exit code and invocation/publication version. Existing page-links, task-display, route, copy inspection, stored-draft and send checks still apply. `preview` remains the HTML-only embed check; do not feed a PNG into it.

Publish a usable native image and original HTML link on the review page, together with ordinary copy, recipients and attachments as already required. Content confirmation and send approval remain separate. A proven technical repair does not approve content, revive a superseded decision or release customer Pause/stop. Invalid earlier reviews remain history; prepare a fresh synchronized review with blank choices only when business scope permits.

Evidence boundary: the 2026-10-30 live probe verified both the saved HTML bytes and a native Notion PNG download against the local render. The initial missing-mapping diagnosis was withdrawn: the original fetch already had `metadata.references`, which the test driver omitted when assembling evidence. This proves current-session save/readback, not all email-client rendering, a full EDM acceptance run or browser availability in cloud Work/Cowork.
