"""Generate and check current run identities; offline, never repair old history."""

import json
from pathlib import Path
import re

PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = PLUGIN / 'plugin.json'
if not MANIFEST.exists():
    MANIFEST = PLUGIN / '.claude-plugin/plugin.json'
VERSION = json.loads(MANIFEST.read_text(encoding='utf-8'))['version']
OWNERS = set(json.loads((PLUGIN / 'references/owner-completion-profiles.json').read_text()))


def validate(properties, creating=False):
    """Run rows are recognizable by RecordType, not a guessed database name."""
    if properties.get('RecordType') not in {'Scan', 'Business', 'Initialization'}:
        return
    for field in ('RunId', 'Skill', 'SkillVersion', 'SourceKey'):
        value = properties.get(field)
        if not isinstance(value, str) or not value.strip() or re.search(r'[\r\n`*<>]|\[[^\]]*\]\(', value):
            raise ValueError('Run metadata needs a plain nonempty ' + field)
    if properties['Skill'] not in OWNERS:
        raise ValueError('Run metadata has an unknown owner')
    if creating and properties['SkillVersion'] != VERSION:
        raise ValueError('New run must record the installed package version')
    if properties['RecordType'] == 'Scan':
        if properties['Skill'] != 'eightdegrees-email-scanning' or properties['SourceKey'] != 'scan:' + properties['RunId']:
            raise ValueError('Scan SourceKey must identify this invocation, not its checkpoint predecessor')
    if properties['Skill'] == 'eightdegrees-daily-brief-and-handover' and properties.get('Workflow') == 'DailyBrief':
        if properties['SourceKey'] != 'report:' + properties['RunId']:
            raise ValueError('Report SourceKey must identify this invocation')


def prepare(data):
    owner, invocation, operation = data['owner_skill'], data['invocation_id'], data['operation']
    if owner not in OWNERS or not isinstance(invocation, str) or not invocation.strip():
        raise ValueError('Use the actual current invocation and registered owner')
    prefix = {'scan': 'scan', 'report': 'report', 'setup': 'setup'}.get(operation, 'run')
    props = {'Skill': owner, 'SkillVersion': VERSION, 'RunId': invocation,
             'SourceKey': prefix + ':' + invocation,
             'RecordType': 'Scan' if operation == 'scan' else 'Initialization' if operation == 'setup' else 'Business'}
    if operation == 'report':
        props['Workflow'] = 'DailyBrief'
    validate(props, creating=True)
    return {'status': 'RunRecordPrepared', 'properties': props,
            'scope': 'Current run metadata only; merge before exact-call/schema preflight; no history rewrites'}
