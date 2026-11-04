"""Load this installed package's scheduled rules afresh; no scheduler or chat binding."""
import argparse
import hashlib
import json
from pathlib import Path

FILES = ('scripts/capture_bundle.py', 'scripts/local_checks.py', 'references/local-check-batch.md', 'references/email-flow.md', 'references/project-cache.md', 'scripts/email_flow.py', 'scripts/reply_transport.py', 'scripts/provider_handoff.py', 'assets/email-review-labels.json', 'scripts/project_cache.py', 'references/api-result-policy.md', 'scripts/api_result.py', 'references/inquiry-intake.md', 'scripts/inquiry_intake.py', 'scripts/current_rules.py', 'skills/eightdegrees-email-scanning/SKILL.md', 'references/scheduled-entry.md',
         'references/scheduled-work.md', 'references/schedule-execution.md',
         'scripts/schedule_checks.py', 'scripts/scan_control.py', 'scripts/event_probe.py',
         'scripts/backlog_recovery.py', 'scripts/queue_construction.py', 'scripts/scan_cycle.py', 'scripts/cycle_metrics.py')
ENTRY_FILES = ('references/email-flow.md', 'references/scheduled-entry.md', 'references/api-result-policy.md', 'skills/eightdegrees-email-scanning/SKILL.md')


def load(data=None):
    data = data or {}
    if type(data.get('include_code', False)) is not bool:
        raise ValueError('include_code must be an explicit boolean')
    root = Path(__file__).resolve().parents[1]
    manifest = next((p for p in (root/'plugin.json', root/'.claude-plugin/plugin.json',
                                root/'skill-pack.json') if p.is_file()), None)
    if manifest is None:
        raise ValueError('Current installed manifest is unavailable')
    version = json.loads(manifest.read_text(encoding='utf-8'))['version']
    captures = {name: (root/name).read_text(encoding='utf-8') for name in FILES}
    digest = hashlib.sha256(json.dumps(captures, sort_keys=True,
                          separators=(',', ':')).encode()).hexdigest()
    visible = FILES if data.get('include_code') else ENTRY_FILES
    return {'status': 'CurrentScheduledRulesLoaded', 'package_root': str(root), 'rule_version': version,
            'rule_sha256': digest, 'rules': {name: captures[name] for name in visible},
            'rule_files': {name: {'sha256': hashlib.sha256(body.encode()).hexdigest(),
                                  'bytes': len(body.encode()), 'path': str(root/name)}
                           for name, body in captures.items()},
            'code_output': bool(data.get('include_code')),
            'email_policy': {'contract': 'email-flow-v3', 'approval_contract': 'email-review-v3',
                             'mime_type': 'text/plain', 'preview_required': False,
                             'technical_records_on_action_page': False,
                             'human_reviews': 1, 'crm_write_readback_required': False,
                             'project_cache_ttl_seconds': 86400},
            'capture_io_policy': {'contract': 'phase-capture-v1', 'batch_per_phase': True,
                                  'per_response_save_calls': False, 'unchanged_writes': False,
                                  'api_write_readback': False, 'new_execution_gate': False},
            'owner': 'eightdegrees-email-scanning', 'policy': 'scheduled-approved-work',
            'scope': 'Actual installed files read on this wake; no approval or scheduler identity requirement'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='Include Python source for explicit debugging only')
    args = parser.parse_args()
    print(json.dumps(load({'include_code': args.full}), ensure_ascii=False))
