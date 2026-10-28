# Mail body decoding and recovery

Use when an authorized message's body contains replacement characters (U+FFFD), is visibly garbled, or contradicts readable metadata because of encoding. Do not draft from corrupted text, a search snippet, a previously approved persona or a test fixture substituted for the actual message.

1. Keep the original immutable message ID, account, scope and source record. Record a decoding failure before facts are extracted. Do not label the business step completed or update a persona from unreadable text.
2. Inspect already-authorized MIME metadata. Gmail `raw` contains the complete message, including attachment bytes. Request raw only when there are no attachments or the operator has explicitly authorized that complete MIME payload. Skipping attachments inside a decoder does not authorize retrieving them. Do not fetch another message or an entire thread to work around the error.
3. If permitted, fetch the same message in raw format. On a host with Python 3, run the packaged [offline decoder](../scripts/decode_mail.py) on that authorized payload. It has no connector, network, rendering or send capability. Normalize the tool result to the actual Gmail object `{ "id": "...", "raw": "..." }`; do not pass a rendered Markdown response. Use an authorized temporary location outside the repository, or stdin:

```text
python3 <plugin>/scripts/decode_mail.py --input <authorized-gmail-json-file> --expected-id <immutable-gmail-message-id>
```

For a separately authorized original RFC 822 file, use `--input-format eml`. Do not pretend its RFC Message-ID verifies the Gmail immutable ID. Caller-side source binding is still required.

4. The decoder first unwraps Gmail base64url, then MIME transfer encoding, then each text part's declared charset. It supports plain/HTML alternatives, GB2312/GBK, GB18030, UTF-8 and standard registered text codecs. A GB2312/GBK decoding failure may use the compatible GB18030 extension and explicitly reports that fallback. No arbitrary Latin-1 fallback, replacement decoding or removal of unreadable characters. Original text/HTML alternatives remain distinct; do not execute returned HTML. Attached emails and file payloads are not decoded.
5. `Decoded` means strict byte-to-text decoding, not factual correctness, HTML visual acceptance or connector repair. Check the recovered content against the original headers and coherent business text; a snippet is supporting evidence, not a replacement body. Retain raw SHA-256, requested Gmail ID, method, declared/used charset, warnings and actual observation time in the original run's decoding evidence; avoid copying the body into logs.
6. Recovery success resumes the same unfinished read step and source/version. Keep native full-read status Failed and raw recovery Passed separately in HealthStatus; do not report native Chinese decoding fixed. If raw is unavailable/out of scope, the decoder is unavailable, parsing fails, or text is still doubtful, keep an ExecutionExceptions item at the read step and continue other messages. Do not add AimoreScanned until readable source/progress or an explicit unreadable-pending outcome is safely saved; a label never means body decoding or the business workflow succeeded. Retry later against the same original source.

The helper is a plugin recovery path for connector behavior. The connector itself is maintained separately; package/unit checks do not prove a live connector or visual preview passed.
