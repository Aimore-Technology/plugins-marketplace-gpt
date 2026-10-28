# 0.1.6 mail decoding, source identity and task presentation

A three-round pilot found corrupted Chinese Gmail full-body reads, display-formatted Notion source identifiers, and stale correction/version prompts in task pages.

- Add a standard-library offline MIME decoder with strict charset/transfer handling, GB2312/GBK-to-GB18030 recovery evidence, multipart text alternatives, source-ID checks and no attachment traversal. The workflow requests raw only within authorized scope and suspends unreadable items. Native connector failure remains separate from raw recovery success; the upstream connector is not changed by this release.
- Query canonical source keys through typed/exact fields, including moved Communications records. Preserve correct stored values; never deduplicate on rendered mailto/escaped Markdown or claim a concurrency lock.
- Maintain one current state/version/difference summary, separate historical evidence and editable inputs, and reuse verified applicable dependencies without taking over Manual setup work.
- Add offline synthetic MIME regression tests to both CI pipelines and require per-command coverage reporting for later live tests.

Validation: run the offline unit suite, marketplace gate, skill validators, archive builder and shared-resource comparison. Local tests do not exercise live mail delivery, connector-native decoding, Notion visual layout, customer approvals/sends or the complete five-command workflow. No customer content or credentials are committed. Existing live task presentation can be repaired separately without changing decisions, business states or input.
