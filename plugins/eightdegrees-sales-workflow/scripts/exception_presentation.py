"""Separate operator decisions from system failures without closing failed work."""
import re

from email_presentation import current_patch, properties
from notion_checks import object_result, page_body, page_id


def text(value):
    if (not isinstance(value, str) or not value.strip() or len(value) > 1500
            or re.search(r'```|<[^>]+>|\b(?:record_type|exception_type|resume_step|TaskId|AttemptId|traceback)\b', value, re.I)
            or re.search(r'^\s*[\[{]', value)):
        raise ValueError('Use a short business explanation, not JSON, internal IDs or a stack trace')
    return value.strip()


def plan(data):
    task, owner = data['task'], data['resolution_owner']
    props = properties(task)
    identity = page_id(object_result(task)['id'])
    if props.get('Category') != 'ExecutionExceptions':
        raise ValueError('Classify only this original execution exception')
    if props.get('State') in {'Completed', 'Cancelled'}:
        return {'status': 'ExceptionPresentationUnchanged', 'writes': [], 'send_allowed': False}
    if owner not in {'System', 'Operator'}:
        raise ValueError('Resolve responsibility explicitly; no guessed human task')
    question = text(data['question']) if data.get('question') else ''
    if owner == 'Operator' and (not question or not props.get('ActionPageURL')):
        raise ValueError('A human exception needs a specific question and the actual existing input route')
    if owner == 'System' and question:
        raise ValueError('System maintenance cannot request operator input')
    summary = {k: text(data[k]) for k in ('problem', 'impact', 'next_step')}
    chinese = data.get('language') == 'zh-CN'
    copy = (['\u5f53\u524d\u72b6\u6001', '\u53d1\u751f\u4e86\u4ec0\u4e48', '\u5f71\u54cd\u8303\u56f4', '\u63a5\u4e0b\u6765', '\u4f60\u9700\u8981\u505a\u4ec0\u4e48',
             '\u65e0\u9700\u64cd\u4f5c\u3002\u8fd9\u662f\u7cfb\u7edf\u7ef4\u62a4\u4e8b\u9879\uff0c\u4e0d\u9700\u8981\u4f60\u8865\u8d44\u6599\u6216\u91cd\u590d\u5ba1\u6838\u3002',
             '\u7cfb\u7edf\u7ef4\u62a4\u8bb0\u5f55\uff08\u65e0\u9700\u64cd\u4f5c\uff09']
            if chinese else ['Current status', 'What happened', 'Impact', 'Next step', 'What you need to do',
                             'No action required. This is system maintenance; no information or repeat review is needed.', 'System maintenance records (no action required)'])
    front = '\n\n'.join(['## '+copy[0], summary['problem'], '### '+copy[2]+'\n\n'+summary['impact'],
                          '### '+copy[3]+'\n\n'+summary['next_step'], '### '+copy[4]+'\n\n'+(question or copy[5])])
    expected = {'ResolutionOwner': owner, 'RequiredInputs': question,
                'Result': summary['problem']+' '+summary['impact']}
    writes = []
    if any((props.get(k) or '') != v for k, v in expected.items()):
        writes.append({'page_id': identity, 'command': 'update_properties', 'properties': expected})
    for capture in [task] + ([data['action']] if data.get('action') else []):
        page = object_result(capture)
        target = page_id(page['id'])
        if target != identity and target != page_id(props['ActionPageURL']):
            raise ValueError('Preserve the actual registered result page; no copied-page repair')
        body = page_body(capture)
        if owner == 'Operator':
            patch = current_patch(body, {'current status', '\u5f53\u524d\u72b6\u6001'},
                                  summary['problem']+'\n\n'+summary['impact']+'\n\n'+question+'\n\n'+summary['next_step'])
            if patch:
                writes.append({'page_id': target, 'command': 'update_content', 'content_updates': [patch]})
            continue
        if re.search(r'<(?:page|database|folder|synced-block)\b|^\s*(?:- \[[ xX]\]|<todo\b)', body, re.M):
            raise ValueError('Preserve operator controls and child records with a targeted adaptation')
        titles = (copy[6], 'System maintenance records (no action required)',
                  '\u7cfb\u7edf\u7ef4\u62a4\u8bb0\u5f55\uff08\u65e0\u9700\u64cd\u4f5c\uff09')
        pattern = r'<toggle(?:\s[^>]*)?>\s*(?:'+ '|'.join(re.escape(t) for t in titles)+r')\s*\n'
        match = re.search(pattern, body)
        if match:
            history = body[match.start():].strip()
        else:
            # Keep machine payload bytes intact and old prose behind one native toggle.
            archived = re.sub(r'^## ', '### ', body, flags=re.M)
            history = '<toggle>'+copy[6]+'\n\n'+archived+'\n</toggle>'
        content = front+'\n\n'+history
        if content != body:
            writes.append({'page_id': target, 'command': 'replace_content', 'new_str': content})
    return {'status': 'ExceptionPresentationPlanned' if writes else 'ExceptionPresentationUnchanged',
            'writes': writes, 'resolution_owner': owner, 'operator_action_required': owner == 'Operator',
            'business_complete': False, 'send_allowed': False,
            'scope': 'Responsibility and readable display only; preserve original state, attempts, bindings and failure evidence'}


def system_view(data):
    from operator_experience import _schema
    source, state = _schema(data['pending_source'])
    page = object_result(data['page']); page_body(data['page'])
    if page.get('metadata', {}).get('type') != 'page':
        raise ValueError('Use the actual registered Dashboard page')
    prop = state['schema'].get('ResolutionOwner')
    if prop is not None and prop.get('type') != 'text':
        raise ValueError('Preserve the existing property type')
    return {'status': 'SystemRecoveryViewPlanned',
            'statements': 'ADD COLUMN "ResolutionOwner" RICH_TEXT' if prop is None else '',
            'view': {'parent_page_id': page_id(page['id']), 'data_source_id': source['id'], 'type': 'list',
                'name': '\u7cfb\u7edf\u5f85\u4fee\u590d' if data.get('language') == 'zh-CN' else 'System Recovery',
                'show_data_source_title': False,
                'configure': 'FILTER "Category" = "ExecutionExceptions" AND "State" != "Completed" AND "State" != "Cancelled" AND ("ResolutionOwner" IS EMPTY OR "ResolutionOwner" != "Operator" OR "RequiredInputs" IS EMPTY OR "ActionPageURL" IS EMPTY); SHOW "Name", "Result"'},
            'scope': 'Original task view only; unknown ownership stays visible to maintenance, not a human decision request'}
