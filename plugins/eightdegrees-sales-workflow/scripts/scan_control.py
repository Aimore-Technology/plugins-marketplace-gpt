"""Plan/read back the Notion scanning switch; never manage native automations."""
import copy
import hashlib
import json

CONTRACT = 'scan-control-v1'


def enabled(settings):
    if not isinstance(settings, dict):
        raise ValueError('Read actual RunSettings before checking the scan switch')
    if 'scan_control' in settings:
        control = settings['scan_control']
        if (not isinstance(control, dict) or control.get('contract') != CONTRACT
                or type(control.get('enabled')) is not bool):
            raise ValueError('Invalid scan_control; do not infer enabled from text or truthiness')
        return control['enabled']
    # Preserve only previously verified approved scanning on first upgrade.
    # No native task metadata, API or init/rebind is required for this fallback.
    old = settings.get('scheduling') or {}
    if not isinstance(old, dict):
        raise ValueError('Invalid legacy scan configuration')
    return (old.get('enabled') is True and old.get('approved_work_enabled') is True
            and old.get('state') == 'Running' and old.get('desired_state') == 'Running')


def gate(data):
    try:
        running = enabled(data['settings'])
    except (KeyError, ValueError) as exc:
        return {'status': 'ScanControlUnknown', 'reason': str(exc), 'work': [], 'ready': [],
                'persist_required': False, 'external_actions_allowed': False}
    return {'status': 'ScanEnabled' if running else 'ScanStopped', 'work': [], 'ready': [],
            'persist_required': False, 'external_actions_allowed': False,
            'scope': 'Switch read only; stopped cycles perform no discovery, task, log or business I/O'}


def fingerprint(settings):
    return hashlib.sha256(json.dumps(settings.get('scan_control'), sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def plan(data):
    operation, settings = data['operation'], data['settings']
    if operation not in {'start', 'stop'}:
        raise ValueError('Use explicit start or stop for the scanning switch')
    if not isinstance(settings, dict):
        raise ValueError('Read original RunSettings before preparing a switch change')
    target = operation == 'start'
    previous = settings.get('scan_control')
    # Preserve extra control metadata without copying unrelated configuration
    # into a replacement payload. Only this field may be patched.
    control = copy.deepcopy(previous) if isinstance(previous, dict) else {}
    control.update(contract=CONTRACT, enabled=target)
    return {'status': 'ScanControlPlanned', 'operation': operation,
            'patch': {'scan_control': control}, 'previous_sha256': fingerprint(settings),
            'write_required': previous != control, 'native_task_mutation_allowed': False,
            'scope': 'Only scan_control changes; no immediate scan or native task operation'}


def verify(data):
    expected = plan(data)
    actual = data['saved_settings']
    if not isinstance(actual, dict):
        raise ValueError('Use the actual saved RunSettings readback')
    unchanged = {k: v for k, v in data['settings'].items() if k != 'scan_control'}
    current = {k: v for k, v in actual.items() if k != 'scan_control'}
    if actual.get('scan_control') != expected['patch']['scan_control'] or current != unchanged:
        return {'status': 'NeedsCorrection', 'reason': 'Switch readback differs or unrelated settings changed'}
    return {'status': 'ScanningEnabled' if enabled(actual) else 'ScanningStopped',
            'native_task_mutation_allowed': False, 'scope': 'Scanning switch verified; no scheduling claim'}
