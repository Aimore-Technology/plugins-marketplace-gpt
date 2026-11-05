#!/usr/bin/env python3
"""Validate this repository's skills-only marketplace and portable payload."""
from pathlib import Path
import json
import re
import sys
import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'eightdegrees-initialization', 'eightdegrees-communication-context-process',
    'eightdegrees-sales-reply', 'eightdegrees-daily-brief-and-handover',
    'eightdegrees-sales-workflow',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def contained(base, relative):
    require(isinstance(relative, str) and relative.startswith('./'), f'Invalid local path: {relative}')
    target = base / relative
    require(not target.is_symlink(), f'Symlink: {target}')
    require(target.resolve().is_relative_to(base.resolve()), f'Escaping path: {relative}')
    require(target.exists(), f'Missing path: {relative}')
    return target

def check():
    claude = ROOT / '.claude-plugin/marketplace.json'
    gpt = ROOT / '.agents/plugins/marketplace.json'
    require(claude.exists() != gpt.exists(), 'Expected exactly one platform catalog')
    platform = 'claude' if claude.exists() else 'gpt'
    catalog = read_json(claude if platform == 'claude' else gpt)
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', catalog.get('name', '')), 'Invalid catalog name')
    if platform == 'claude':
        require(bool(catalog.get('owner', {}).get('name')), 'Missing marketplace owner')
    entries = catalog.get('plugins')
    require(isinstance(entries, list) and entries, 'Marketplace has no plugins')
    names = set()
    for entry in entries:
        name = entry.get('name')
        require(name not in names, f'Duplicate plugin: {name}')
        names.add(name)
        if platform == 'claude':
            plugin = contained(ROOT, entry.get('source'))
            manifest = read_json(plugin / '.claude-plugin/plugin.json')
        else:
            source = entry.get('source', {})
            require(source.get('source') == 'local', 'Only local sources supported by this gate')
            plugin = contained(ROOT, source.get('path'))
            manifest = read_json(plugin / 'plugin.json')
            jsonschema.Draft202012Validator(read_json(ROOT / 'schemas-plugin.json')).validate(manifest)
            ext = manifest['extensions']['com.openai']
            interface = ext['interface']
            require(0 < len(interface['shortDescription']) <= 30, 'Listing subtitle exceeds 30 characters')
            require(0 < len(interface['displayName']) <= 30, 'Listing name exceeds 30 characters')
            require(interface['category'] == 'Business & Operations', 'Unexpected category')
            require(isinstance(interface['capabilities'], list), 'Capabilities must be an array')
            contained(plugin, ext['onboardingSkill'])
            prompts = interface['defaultPrompt']
            require(isinstance(prompts, list) and 1 <= len(prompts) <= 3, 'Invalid starter prompts')
            require(all(isinstance(p, str) and 0 < len(p) <= 128 and '\n' not in p for p in prompts), 'Invalid prompt')
        require(manifest.get('name') == name == plugin.name, 'Manifest/source identity mismatch')
        require(re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')), 'Expected strict release SemVer')
        require(bool(manifest.get('author', {}).get('name')), 'Missing author')
        skills = sorted((plugin / 'skills').glob('*/SKILL.md'))
        require({p.parent.name for p in skills} == EXPECTED, 'Unexpected/missing skills')
        for skill in skills:
            text = skill.read_text(encoding='utf-8')
            require(text.startswith('---\n'), f'Missing frontmatter: {skill}')
            parts = text.split('---\n', 2)
            require(len(parts) == 3, f'Invalid frontmatter delimiters: {skill}')
            meta = yaml.safe_load(parts[1])
            require(meta['name'] == skill.parent.name, f'Skill name mismatch: {skill}')
            require(isinstance(meta['description'], str) and meta['description'].strip(), f'Missing description: {skill}')
            require(len(text.encode('utf-8')) < 1024*1024, 'Skill exceeds portable size limit')
            require(len(parts[2].split()) >= 80, f'Incomplete instructions: {skill}')
        for path in ROOT.rglob('*'):
            rel = path.relative_to(ROOT)
            if '.git' in rel.parts or 'dist' in rel.parts or '__pycache__' in rel.parts:
                continue
            require(not path.is_symlink(), f'Symlink not allowed: {rel}')
            if not path.is_file():
                continue
            require(path.name not in {'.env', '.app.json', '.mcp.json', 'mcp.json', 'hooks.json'}, f'Unexpected runtime wiring/secret file: {rel}')
            if path.suffix in {'.md', '.json', '.yml', '.yaml', '.py', '.txt'}:
                text = path.read_text(encoding='utf-8')
                require(not re.search(r'[\u3400-\u9fff\uf900-\ufaff]', text), f'Non-English CJK text: {rel}')
                require(not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', text), f'Credential pattern: {rel}')
            if path.suffix == '.json':
                read_json(path)
            if path.suffix in {'.yml', '.yaml'}:
                yaml.safe_load(path.read_text(encoding='utf-8'))
        for path in plugin.rglob('*.md'):
            # Relative Markdown resource links must resolve inside the installed plugin.
            for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if link.startswith(('https://', 'http://', '#')):
                    continue
                target = (path.parent / link.split('#')[0]).resolve()
                require(target.is_relative_to(plugin.resolve()), f'Unpackaged dependency: {path}: {link}')
                require(target.exists(), f'Broken reference: {path}: {link}')
        routes = read_json(plugin / 'references/commands.json')
        require(set(routes) == {'init', 'add-communication', 'report', 'reply-draft'}, 'Command inventory mismatch')
        for alias, route in routes.items():
            require(route['skill'] in EXPECTED - {'eightdegrees-sales-workflow'}, f'Invalid command target: {alias}')
            require((plugin / 'skills' / route['skill'] / 'SKILL.md').is_file(), f'Missing command target: {alias}')
            require(all(isinstance(route.get(k), str) and route[k].strip() for k in ('description', 'policy', 'instructions')), f'Incomplete command policy: {alias}')
        if platform == 'claude':
            command_files = sorted((plugin / 'commands').glob('*.md'))
            require({p.stem for p in command_files} == set(routes), 'Native command inventory mismatch')
            for command in command_files:
                command_text = command.read_text(encoding='utf-8')
                require(command_text.startswith('---\n'), f'Missing command frontmatter: {command}')
                parts = command_text.split('---\n', 2)
                require(len(parts) == 3, f'Invalid command frontmatter: {command}')
                metadata = yaml.safe_load(parts[1])
                require(metadata['description'] == routes[command.stem]['description'], f'Command metadata drift: {command}')
                require('$ARGUMENTS' in parts[2], f'Command arguments not forwarded: {command}')
                require(f'Dispatch `{command.stem}`' in parts[2], f'Wrong command dispatch: {command}')
        else:
            require(not (plugin / 'commands').exists(), 'Do not ship Claude commands as an OpenAI runtime component')
        client = plugin / 'scripts/activepieces_client.py'
        require(client.is_file(), 'Missing offline Activepieces request client')
        require({p.name for p in (plugin / 'scripts').glob('*.py')} == {'activepieces_client.py'},
                'Business executors must not ship in the client package')
        require(not (plugin / 'legacy').exists(), 'Do not package archived owners')
        for document in (plugin / 'skills').glob('*/SKILL.md'):
            text = document.read_text()
            require('Activepieces' in text and 'client' in text.lower(), 'Skill does not declare client ownership')
        require('waitForResponse=false' in (plugin / 'references/activepieces-client.md').read_text(),
                'Document asynchronous action-runner boundary')
        print(f'PASS {platform}: {name} {manifest["version"]}; five English client skills; four routes, references and payload checked')
    return platform

if __name__ == '__main__':
    try:
        check()
    except (ValueError, KeyError, OSError, jsonschema.ValidationError, yaml.YAMLError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
