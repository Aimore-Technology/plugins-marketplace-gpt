"""Load this installed package's scheduled rules afresh; no scheduler or chat binding."""
import hashlib
import json
from pathlib import Path

FILES = ('scripts/current_rules.py', 'skills/eightdegrees-email-scanning/SKILL.md', 'references/scheduled-entry.md',
         'references/scheduled-work.md', 'references/schedule-execution.md',
         'scripts/schedule_checks.py', 'scripts/scan_control.py', 'scripts/event_probe.py',
         'scripts/backlog_recovery.py', 'scripts/queue_construction.py', 'scripts/scan_cycle.py', 'scripts/cycle_metrics.py')


def load(data=None):
    root = Path(__file__).resolve().parents[1]
    manifest = next((p for p in (root/'plugin.json', root/'.claude-plugin/plugin.json',
                                root/'skill-pack.json') if p.is_file()), None)
    if manifest is None:
        raise ValueError('Current installed manifest is unavailable')
    version = json.loads(manifest.read_text(encoding='utf-8'))['version']
    captures = {name: (root/name).read_text(encoding='utf-8') for name in FILES}
    digest = hashlib.sha256(json.dumps(captures, sort_keys=True,
                          separators=(',', ':')).encode()).hexdigest()
    return {'status': 'CurrentScheduledRulesLoaded', 'package_root': str(root), 'rule_version': version,
            'rule_sha256': digest, 'rules': captures,
            'owner': 'eightdegrees-email-scanning', 'policy': 'scheduled-approved-work',
            'scope': 'Actual installed files read on this wake; no approval or scheduler identity requirement'}


if __name__ == '__main__':
    print(json.dumps(load(), ensure_ascii=False))
