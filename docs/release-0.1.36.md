# EightDegrees Sales Workflow 0.1.36

The first live0.1.35 initialization stopped before configuration/business work:
Notion rendered a correct `setup:<invocation>:init` SourceKey as escaped Markdown.
The new identity guard compared that presentation byte-for-byte with canonical
metadata. The failed initialization and original source values remain history.

Readback comparison now decodes exactly one layer of escaped colon, underscore,
dot, hyphen or backslash in generated identity fields, without modifying original
captures or saved properties. New writes still require canonical plain values:
presentation escapes, links, literal backslashes, wrong versions and predecessor
scan keys remain rejected. Frozen plan/body, actual page and role bindings still
have their existing checks. No guessed raw-property API or captured-page rewrite
is needed. Business-source identity rules remain separate.

Both editions pass503 offline tests, including four new readback regressions.
Replay against the actual failed0.1.35 page and original frozen metadata matches
without changing that page/capture. Original0.1.35 work executed zero scans and
no email/SMS/CRM/configuration change; that failure is not counted as a pass.

The0.1.35 budget/discovery/error-capture corrections remain. Public-command live
workflow validation resumes after upgrade; this patch itself sends nothing and
does not extend old windows, reset counters or certify cloud scheduling.
