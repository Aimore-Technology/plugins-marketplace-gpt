"""Save original phase inputs in one private local bundle; no connector calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from notion_checks import page_id
from connector_capture import normalize
from scan_cycle import timestamp

CONTRACT = 'capture-bundle-v1'
PLUGIN = Path(__file__).resolve().parents[1]


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def unpack(value):
    """Keep plain legacy capture dictionaries usable by the same local checks."""
    if isinstance(value, dict) and value.get('record_type') == CONTRACT:
        if not isinstance(value.get('captures'), dict):
            raise ValueError('Malformed original capture bundle')
        return value['captures']
    if not isinstance(value, dict):
        raise ValueError('Use named original capture objects')
    return value


def commit(data):
    target = Path(data['bundle_path']).expanduser()
    if not target.is_absolute() or target.resolve().is_relative_to(PLUGIN):
        raise ValueError('Capture bundles belong in private local state outside the plugin')
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError('Do not write capture data through a symlink')
    root = page_id(data['root_id'])
    if len(root) != 32 or any(c not in '0123456789abcdef' for c in root):
        raise ValueError('Use the actual Notion installation root')
    cycle = data['cycle_key']
    if not isinstance(cycle, str) or not cycle.strip():
        raise ValueError('Keep one local bundle per cycle; this key is not execution identity')
    observed_at = data['observed_at']; timestamp(observed_at)
    incoming = data['captures']
    if (not isinstance(incoming, dict) or not incoming
            or any(not isinstance(k, str) or not k or not isinstance(v, dict) or not v
                   for k, v in incoming.items())):
        raise ValueError('Submit one nonempty batch of exact original response/exception objects')
    original = {'record_type': CONTRACT, 'root_id': root, 'cycle_key': cycle,
                'captures': {}, 'flush_count': 0}
    if target.exists():
        original = json.loads(target.read_text(encoding='utf-8'))
        if (not isinstance(original, dict) or original.get('record_type') != CONTRACT or original.get('root_id') != root
                or original.get('cycle_key') != cycle):
            raise ValueError('Do not overwrite another cycle or installation bundle')
    previous = unpack(original)
    additions = {}
    for name, response in incoming.items():
        if name in previous:
            if encoded(previous[name]) != encoded(response):
                raise ValueError('Original capture alias changed: '+name+'; use a new phase/revision alias')
        else:
            additions[name] = response
    # Inspect all returned error/warning layers before any mutation. Failure is
    # retained as evidence; saving that evidence does not make the feed complete.
    observations = {name: normalize({'response': response, 'observed_at': observed_at,
                    'capture_ref': str(target)+'#'+name}) for name, response in incoming.items()}
    if additions:
        updated = {**original, 'captures': {**previous, **additions},
                   'flush_count': original['flush_count']+1}
        payload = encoded(updated)
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temp_name = tempfile.mkstemp(dir=target.parent, prefix='.'+target.name+'.')
        try:
            with os.fdopen(fd, 'wb') as output:
                if hasattr(os, 'fchmod'):
                    os.fchmod(output.fileno(), 0o600)
                else:
                    os.chmod(temp_name, 0o600)
                output.write(payload); output.flush(); os.fsync(output.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    return {'status': 'CaptureBundleSaved' if additions else 'CaptureBundleUnchanged',
            'bundle_path': str(target), 'captures_added': len(additions),
            'captures_reused': len(incoming)-len(additions), 'write_count': int(bool(additions)),
            'total_captures': len(previous)+len(additions),
            'flush_count': original['flush_count']+int(bool(additions)),
            'observations': {name: {k: v for k, v in value.items() if k != 'original'}
                             for name, value in observations.items()},
            'failures': {name: value for name, value in observations.items() if value['failed']},
            'external_actions_allowed': False,
            'scope': 'Private cycle inputs only; no Notion write, permission cache, readback or send authority'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='One phase batch JSON path, or - for stdin')
    args = parser.parse_args()
    try:
        value = json.loads(sys.stdin.read() if args.input == '-' else Path(args.input).read_text())
        result = commit(value)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'NeedsCorrection', 'issues': [str(exc)]}
    print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    return 0 if result['status'] in {'CaptureBundleSaved', 'CaptureBundleUnchanged'} else 2


if __name__ == '__main__':
    sys.exit(main())
