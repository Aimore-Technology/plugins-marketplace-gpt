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
    'eightdegrees-initialization', 'eightdegrees-email-scanning',
    'eightdegrees-communication-context-process', 'eightdegrees-client-persona-update',
    'eightdegrees-sms-follow-up', 'eightdegrees-sales-reply',
    'eightdegrees-daily-brief-and-handover', 'eightdegrees-sales-workflow', 'eightdegrees-automation-control',
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
        require(set(routes) == {'init', 'start', 'stop', 'add-communication', 'run-auto', 'report', 'reply-draft'}, 'Command inventory mismatch')
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
        task_routes = read_json(plugin / 'references/task-routes.json')
        require(bool(task_routes), 'Missing task resume routes')
        for step, route in task_routes.items():
            require(re.fullmatch(r'[A-Za-z][A-Za-z0-9]+', step), f'Invalid resume step: {step}')
            require(route.get('owner') in EXPECTED - {'eightdegrees-sales-workflow'}, f'Unknown task owner: {step}')
            require(bool(route.get('categories')) and set(route['categories']) <= {'ClientMatching', 'DataCompletion', 'ContentReview', 'SendApproval', 'ExecutionExceptions', 'ScheduledWork'}, f'Invalid task category: {step}')
            require(route.get('effect') in {'read', 'crm', 'checkpoint', 'draft', 'customer-send', 'setup', 'report', 'calendar', 'internal-notification', 'presentation'}, f'Unknown task effect: {step}')
        owner_profiles = read_json(plugin / 'references/owner-completion-profiles.json')
        require(set(owner_profiles) == EXPECTED - {'eightdegrees-sales-workflow'}, 'Owner completion profile inventory mismatch')
        for owner, kinds in owner_profiles.items():
            require(bool(kinds) and set(kinds) <= {'page-links', 'task-display', 'route'}, f'Unknown owner completion checks: {owner}')
        defaults = read_json(plugin / 'references/pilot-defaults.json')
        require(defaults['configuration_version'] == 'pilot-v1', 'Configuration version drift')
        require(defaults['settings_schema_version'] == 2, 'Settings schema drift')
        setup = defaults['customer_setup']
        require(all(setup[k] is None for k in ('operator_id', 'operator_name', 'operator_email', 'operator_sms_number')), 'Do not ship a fixed operator identity/destination')
        require('operator_gmail' in defaults['important_reminders']['priority'], 'Operator reminder channel missing')
        require(defaults['data']['sensitive_originals'] == 'operator_manual_only', 'Manual-handling role drift')
        for resource in plugin.rglob('*'):
            if resource.is_file() and resource.suffix in {'.md', '.json'} and resource.name != 'operator-setup.md':
                require(not re.search(r'john|vivian', resource.read_text(encoding='utf-8'), re.I), f'Fixed pilot person in runtime payload: {resource.relative_to(plugin)}')
        require(defaults['timezone'] == 'Australia/Adelaide', 'Pilot timezone drift')
        require(defaults.get('scan_control') == {'contract': 'scan-control-v1', 'enabled': False}, 'Package must default to stopped scanning')
        require(defaults['scheduling']['enabled'] is False, 'Package must not enable schedules')
        require(defaults['scheduling']['target_scan_minutes'] == 30
                and defaults['scheduling']['allowed_scan_minutes'] == [20, 30], 'Scan cadence defaults drift')
        require(defaults['queue_execution']['cycle_budget_seconds'] == 900
                and defaults['queue_execution']['publication_reserve_seconds'] == 120, 'Cycle budget defaults drift')
        require(defaults['queue_execution']['cycle_budget_seconds'] < min(defaults['scheduling']['allowed_scan_minutes']) * 60,
                'Soft cycle budget must leave room before the shortest supported interval')
        require(defaults['customer_setup']['allowed_label_ids'] == [], 'Do not ship a customer mail scope')
        require(defaults['customer_setup']['notion_root_id'] is None, 'Do not ship a developer Notion root')
        require(defaults['sms_follow_up']['max_messages_per_cycle_including_manual'] == 2, 'SMS cap drift')
        require(defaults['sms_follow_up']['automatic_sending_enabled'] is True, 'Notification SMS permission defaults enabled; capability gates stay separate')
        require(defaults['sms_notifications']['enabled'] is True and defaults['sms_notifications']['per_message_review_required'] is False, 'Standing notification authority drift')
        require(defaults['queue_execution']['continue_commands_required'] is False, 'Queue must not require extra continuation commands')
        require(defaults['data']['deliberate_redaction'] is False, 'Pilot data policy drift')
        require(defaults['send_completion'] == {'policy': 'provider-handoff-v1', 'email': 'successful_gmail_dispatch_response', 'sms': 'successful_androidsync_request_response', 'provider_status_polling': False, 'recipient_verification': False, 'crm_write_readback_required': False}, 'Provider handoff boundary drift')
        require(defaults.get('email_workflow', {}).get('approval_contract') == 'email-review-v4'
                and defaults['email_workflow'].get('human_reviews_per_email') == 1,
                'New mail must have one combined review')
        require(defaults['email_workflow'].get('mime_type') == 'text/plain'
                and defaults['email_workflow'].get('preview_required') is False
                and defaults['email_workflow'].get('technical_records_on_action_page') is False,
                'New inquiry review must be readable plain text without previews or technical JSON')
        require(defaults['email_workflow'].get('review_surface') == 'canonical-task-view'
                and defaults['email_workflow'].get('consent_checkbox') is True
                and defaults['email_workflow'].get('separate_submit') is False,
                'One native consent checkbox must submit without a separate action form')
        require(defaults.get('project_cache', {}).get('ttl_seconds') == 86400
                and defaults['project_cache'].get('storage') == 'private-local-user-state'
                and defaults['project_cache'].get('cache_permissions') is False,
                'Project cache scope/default drift')
        forbidden = ('Keep content and send decisions separate.',
                     'Content confirmation and send approval remain separate.',
                     'Submit ContentReview and separately SendApproval',
                     'read_email(format=raw)',
                     'download the returned URL and supply exact bytes',
                     'saved-result readback remains required', 'CRM writes retain readback')
        for document in plugin.rglob('*.md'):
            text = document.read_text()
            require(not any(phrase in text for phrase in forbidden),
                    f'Conflicting obsolete runtime rule: {document.relative_to(plugin)}')
        print(f'PASS {platform}: {name} {manifest["version"]}; nine English skills (eight workflows + command entry); command routes, references, defaults and payload checked')
    return platform

if __name__ == '__main__':
    try:
        check()
    except (ValueError, KeyError, OSError, jsonschema.ValidationError, yaml.YAMLError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
