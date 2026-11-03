"""Original-capture shape for a completed intake, with no account/network I/O."""

import json

ROOT, SOURCE, CHECKPOINT = (c * 32 for c in '987')
KEY = 'sender@example.invalid:inbound:source-1'


def capture(identity, body, props=None):
    return {'id': identity, 'metadata': {'type': 'page'},
            'text': '<ancestor-3-page url="https://app.notion.com/p/' + ROOT + '"/>\n<properties>'
                    + json.dumps(props or {}) + '</properties>\n<content>\n' + body + '\n</content>'}


def block(value):
    return '```json\n' + json.dumps(value) + '\n```'


def handoff():
    props = {'Account': '[sender@example.invalid](mailto:sender@example.invalid)',
             'Direction': 'Inbound', 'MessageId': 'source-1', 'ThreadId': 'thread-1',
             'ContentVersion': 'source-v1', 'SourceKey': KEY}
    checkpoint = {'record_type': 'scan-checkpoint-v1', 'root_id': ROOT, 'invocation_id': 'original-intake',
                  'items': {'intake': {'source_key': KEY, 'step': 'ReadMessageBody', 'version': 'source-v1',
                                      'state': 'completed', 'receipt_ref': 'https://app.notion.com/p/' + SOURCE}}}
    return {'root_id': ROOT, 'source_key': KEY, 'source_version': 'source-v1',
            'source_page': capture(SOURCE, 'Original customer request.', props),
            'checkpoint_page': capture(CHECKPOINT, block(checkpoint))}
