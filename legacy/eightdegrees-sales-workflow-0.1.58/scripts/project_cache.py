"""Account/workspace-scoped local project materials; never contacts or authority."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
import re
from functools import wraps
from datetime import datetime, timezone

CONTRACT = 'project-cache-v1'
DEFAULT_TTL = 86400


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def instant(value=None):
    now = datetime.fromisoformat(value.replace('Z', '+00:00')) if value else datetime.now(timezone.utc)
    if now.utcoffset() is None:
        raise ValueError('Cache time needs an explicit offset')
    return now.astimezone(timezone.utc)


def remote_path(value):
    if not isinstance(value, str) or not value.startswith('/') or '\\' in value or '..' in value.split('/'):
        raise ValueError('Use a concrete authorized Dropbox display path')
    return str(PurePosixPath(value)).casefold()


def location(data):
    scope = data['scope']
    if any(not isinstance(scope.get(k), str) or not scope[k].strip() for k in ('workspace_id', 'account_id')):
        raise ValueError('Actual workspace and Dropbox account/namespace identity are required')
    roots = sorted(set(remote_path(v) for v in scope['authorized_roots']))
    if not roots:
        raise ValueError('Current authorized roots are required; root access is not inferred')
    key = digest({'contract': CONTRACT, 'workspace': scope['workspace_id'],
                  'account': scope['account_id'], 'roots': roots})
    base = Path(data.get('cache_root') or Path.home()/'.local/state/eightdegrees/project-cache')
    if base.is_symlink() or base.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError('Cache belongs in private host state, outside the distributed plugin')
    if (base/key).is_symlink():
        raise ValueError('Do not follow cache scope symlinks')
    return base/key, key, roots


def project_key(project):
    if any(not isinstance(project.get(k), str) or not project[k].strip() for k in ('name', 'lot')):
        raise ValueError('Project name and exact lot are required')
    return digest([project['name'].strip().casefold(), project['lot'].strip().casefold()])


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.parent.is_symlink() or path.is_symlink():
        raise ValueError('Do not follow cache symlinks')
    fd, name = tempfile.mkstemp(prefix='.cache-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=True, allow_nan=False)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def read_json(path):
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Do not follow cache symlinks')
    return json.loads(path.read_text(encoding='utf-8'))


def cache_io(function):
    @wraps(function)
    def guarded(data):
        try:
            return function(data)
        except OSError as exc:
            return {'status': 'ProjectCacheUnavailable', 'reason': str(exc),
                    'connector_calls': 0, 'send_authority': False,
                    'fallback': 'Use the already authorized fresh project sources for this inquiry'}
    return guarded


@cache_io
def put(data):
    directory, scope_key, roots = location(data)
    project, files = data['project'], data['files']
    key, now = project_key(project), instant(data.get('now'))
    ttl = data.get('ttl_seconds', DEFAULT_TTL)
    if type(ttl) is not int or not 60 <= ttl <= 604800:
        raise ValueError('Cache TTL must be 60 seconds to seven days')
    if not isinstance(files, list) or not files:
        raise ValueError('Cache actual successfully read source materials, not a guessed project')
    seen = set()
    normalized = []
    for source in files:
        path = remote_path(source['path'])
        if not any(path == root or path.startswith(root.rstrip('/')+'/') for root in roots):
            raise ValueError('Project file is outside the current authorized roots')
        if source.get('status', 'Current') != 'Current':
            raise ValueError('Only current, non-conflicting project material can warm the active cache')
        if not source.get('id') or source['id'] in seen or not source.get('version'):
            raise ValueError('Actual unique file IDs and source versions are required')
        if not isinstance(source.get('text'), str) or not source['text'].strip():
            raise ValueError('Do not cache an unread, missing or failed source as empty content')
        seen.add(source['id'])
        normalized.append({k: source.get(k) for k in ('id', 'path', 'version', 'rev', 'effective_date', 'status', 'text')})
    facts = data.get('facts', {})
    forbidden = {'operator_id', 'contact_id', 'client_id', 'customer_name', 'email', 'phone', 'approval', 'send_approval', 'stop', 'attempts', 'sms_permission', 'scan_enabled', 'credentials', 'token'}
    if isinstance(facts, dict) and forbidden & {str(k).casefold() for k in facts}:
        raise ValueError('Do not cache customer records, credentials or execution authority as project facts')
    if not isinstance(facts, dict) or not isinstance(data.get('fact_sources', {}), dict):
        raise ValueError('Project facts and their original file references must be objects')
    for field in facts:
        refs = data.get('fact_sources', {}).get(field)
        if not isinstance(refs, list) or not refs or not set(refs) <= seen:
            raise ValueError('Every extracted fact needs its actual original file reference')
    aliases = project.get('aliases', [])
    if not isinstance(aliases, list) or any(not isinstance(v, str) or not v.strip() for v in aliases):
        raise ValueError('Use explicit project aliases, not fuzzy guesses')
    snapshot = {'contract': CONTRACT, 'scope_key': scope_key, 'project': project,
                'files': normalized, 'facts': facts, 'fact_sources': data.get('fact_sources', {})}
    snapshot_id = digest(snapshot)
    # Immutable content snapshots preserve the exact source package used by a review.
    write_json(directory/'snapshots'/(snapshot_id+'.json'), snapshot)
    index = {'contract': CONTRACT, 'scope_key': scope_key, 'project': project,
             'snapshot_id': snapshot_id, 'fetched_at': now.isoformat(), 'ttl_seconds': ttl}
    write_json(directory/'projects'/(key+'.json'), index)
    return {'status': 'ProjectCacheStored', 'scope_key': scope_key, 'snapshot_id': snapshot_id,
            'project': project, 'file_count': len(files), 'connector_calls': 0}


@cache_io
def get(data):
    directory, scope_key, roots = location(data)
    path = directory/'projects'/(project_key(data['project'])+'.json')
    if not path.is_file():
        return {'status': 'ProjectCacheMiss', 'reason': 'No current snapshot in this authorized account/workspace scope', 'connector_calls': 0}
    try:
        index = read_json(path)
        if index.get('contract') != CONTRACT or index.get('scope_key') != scope_key:
            raise ValueError('Cache schema/scope changed')
        if not re.fullmatch(r'[a-f0-9]{64}', index.get('snapshot_id', '')):
            raise ValueError('Invalid snapshot identity')
        age = (instant(data.get('now'))-instant(index['fetched_at'])).total_seconds()
        if age < 0 or age >= index['ttl_seconds']:
            return {'status': 'ProjectCacheRefreshRequired', 'reason': 'TTL expired or clock changed', 'connector_calls': 0}
        snapshot = read_json(directory/'snapshots'/(index['snapshot_id']+'.json'))
        if digest(snapshot) != index['snapshot_id']:
            raise ValueError('Local cache is incomplete or changed')
        expected = data.get('expected_revisions', {})
        if any(source['id'] in expected and source.get('rev') != expected[source['id']] for source in snapshot['files']):
            return {'status': 'ProjectCacheRefreshRequired', 'reason': 'Observed source revision changed', 'connector_calls': 0}
        fields = data.get('fields', list(snapshot['facts']))
        selected = data.get('include_file_ids', [])
        if not set(fields) <= snapshot['facts'].keys() or not set(selected) <= {f['id'] for f in snapshot['files']}:
            raise ValueError('Requested material is not present in this snapshot')
        return {'status': 'ProjectCacheHit', 'scope_key': scope_key, 'snapshot_id': index['snapshot_id'],
                'project': snapshot['project'], 'fetched_at': index['fetched_at'], 'age_seconds': age,
                'facts': {k: snapshot['facts'][k] for k in fields},
                'fact_sources': {k: snapshot['fact_sources'][k] for k in fields},
                'files': [{k: v for k, v in f.items() if k != 'text' or f['id'] in selected} for f in snapshot['files']],
                'connector_calls': 0, 'send_authority': False}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'ProjectCacheRefreshRequired', 'reason': str(exc), 'connector_calls': 0}


@cache_io
def catalog(data):
    directory, scope_key, _ = location(data)
    projects = []
    for path in sorted((directory/'projects').glob('*.json')):
        try:
            row = read_json(path)
            if row['scope_key'] == scope_key:
                projects.append({'project': row['project'], 'snapshot_id': row['snapshot_id'],
                                 'fetched_at': row['fetched_at']})
        except (OSError, ValueError, KeyError):
            continue
    return {'status': 'ProjectCatalogLoaded', 'projects': projects, 'connector_calls': 0}


@cache_io
def match(data):
    candidates = []
    name, lot = data['name'].strip().casefold(), str(data.get('lot', '')).strip().casefold()
    registered = data.get('registered_projects', [])
    known = {project_key(row['project']): row['project'] for row in catalog(data).get('projects', [])}
    for project in registered:
        known[project_key(project)] = project
    for project in known.values():
        names = [project['name'], *project.get('aliases', [])]
        if name in [v.strip().casefold() for v in names] and (not lot or lot == project['lot'].strip().casefold()):
            candidates.append(project)
    return {'status': 'ProjectMatched' if len(candidates) == 1 else 'NeedsProjectSelection',
            'project': candidates[0] if len(candidates) == 1 else None, 'candidates': candidates,
            'connector_calls': 0, 'send_authority': False}


@cache_io
def invalidate(data):
    directory, _, _ = location(data)
    path = directory/'projects'/(project_key(data['project'])+'.json')
    if path.is_symlink():
        raise ValueError('Do not follow cache symlinks')
    path.unlink(missing_ok=True)
    return {'status': 'ProjectCacheInvalidated', 'snapshots_preserved': True, 'connector_calls': 0}
