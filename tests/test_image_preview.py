"""Frozen HTML -> saved PNG evidence regressions, without connector writes."""
import base64
import copy
import hashlib
import json
import subprocess
import sys
import unittest

from test_notion_checks import CHECKS, HTML, REPORT, SCRIPTS, page, preview

SOURCE = 'notion-file-block://saved-block/image'
URL = 'https://files.example.invalid/saved.png?signature=fixture'
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a6uoAAAAASUVORK5CYII=')


def image_preview():
    data = preview(f'<image source="{SOURCE}" />')
    data['page']['metadata']['references'] = {SOURCE: URL}
    data['content_version'] = 'reply-v2'
    data['embedded_asset'] = {'source': SOURCE, 'resolved_url': URL, 'content_base64': base64.b64encode(PNG).decode()}
    data['render_manifest'] = {
        'source_html_sha256': data['html_sha256'], 'source_bytes': len(HTML.encode()),
        'preview_png_sha256': hashlib.sha256(PNG).hexdigest(), 'preview_bytes': len(PNG),
        'width': 1, 'height': 1, 'content_version': 'reply-v2',
        'renderer': 'playwright-chromium', 'browser_version': 'offline-fixture',
        'completed': True, 'javascript_enabled': False, 'blocked_resources': []}
    return data


class ReferenceTests(unittest.TestCase):
    def test_nested_mapping_survives_unrelated_nonempty_top_level_map_and_wrappers(self):
        data = image_preview()
        data['page']['references'] = {'other': 'https://files.example.invalid/other'}
        for captured in (data['page'], {'structuredContent': data['page']},
                         {'content': [{'type': 'text', 'text': json.dumps(data['page'])}]}):
            self.assertEqual(CHECKS.preview_reference({'page': captured, 'source': SOURCE})['resolved_url'], URL)

    def test_missing_download_bytes_does_not_mean_mapping_is_absent(self):
        data = image_preview()
        del data['embedded_asset']
        result = CHECKS.preview_reference({'page': data['page'], 'source': SOURCE})
        self.assertEqual(result['status'], 'DownloadRequired')
        self.assertNotIn('sha256', result)

    def test_conflicting_mappings_are_not_silently_chosen(self):
        data = image_preview()
        data['page']['references'] = {SOURCE: URL + '-other'}
        self.assertEqual(CHECKS.preview_reference({'page': data['page'], 'source': SOURCE})['status'], 'NeedsCorrection')

    def test_mapping_from_another_page_or_unsafe_url_cannot_pass(self):
        data = image_preview()
        data['page'] = page('<image source="notion-file-block://other" />')
        self.assertEqual(CHECKS.preview_reference({'page': data['page'], 'source': SOURCE})['status'], 'NeedsCorrection')
        for url in ('http://files.example.invalid/x', 'https://user:secret@files.example.invalid/x'):
            data = image_preview(); data['page']['metadata']['references'][SOURCE] = url
            with self.assertRaises(ValueError):
                CHECKS.preview_reference({'page': data['page'], 'source': SOURCE})

    def test_existing_html_path_also_uses_nested_map_when_top_level_has_other_references(self):
        data = preview(f'<embed source="{SOURCE}" />')
        data['page']['references'] = {'unrelated': URL + '-other'}
        data['page']['metadata']['references'] = {SOURCE: URL}
        data['embedded_asset'] = {'source': SOURCE, 'resolved_url': URL, 'content_base64': base64.b64encode(HTML.encode()).decode()}
        self.assertEqual(CHECKS.check_preview(data)['status'], 'SavedEmbedAndBytesMatch')


class ImagePreviewTests(unittest.TestCase):
    def test_saved_image_and_rendered_bytes_match_original_html(self):
        result = CHECKS.check_image_preview(image_preview())
        self.assertEqual(result['status'], 'SavedImageAndBytesMatch')
        self.assertEqual(result['entity_id'], REPORT)
        self.assertIn('no approval', result['scope'])

    def test_changed_html_png_version_dimensions_or_render_failure_reject(self):
        changes = {'source_html_sha256': '0' * 64, 'source_bytes': 1,
                   'preview_png_sha256': '0' * 64, 'preview_bytes': 1, 'width': 720, 'height': 800,
                   'content_version': 'reply-v1', 'completed': False, 'javascript_enabled': True,
                   'blocked_resources': ['https://external.invalid/image.png'], 'renderer': 'model-redraw', 'browser_version': ''}
        for key, value in changes.items():
            with self.subTest(key=key):
                data = image_preview(); data['render_manifest'][key] = value
                self.assertEqual(CHECKS.check_image_preview(data)['status'], 'NeedsCorrection')
        data = image_preview(); data['download']['content'] += 'changed'
        self.assertEqual(CHECKS.check_image_preview(data)['status'], 'NeedsCorrection')

    def test_actual_saved_download_identity_and_bytes_required(self):
        for key, value in (('resolved_url', URL + '-guessed'), ('content_base64', base64.b64encode(b'not png').decode())):
            data = image_preview(); data['embedded_asset'][key] = value
            self.assertEqual(CHECKS.check_image_preview(data)['status'], 'NeedsCorrection')
        data = image_preview(); data['embedded_asset']['content_base64'] = 'invalid-base64'
        with self.assertRaises(ValueError):
            CHECKS.check_image_preview(data)

    def test_code_file_link_or_embed_is_not_a_saved_native_image(self):
        for body in (SOURCE, f'<file source="{SOURCE}" />', f'<embed source="{SOURCE}" />',
                     f'```text\n<image source="{SOURCE}" />\n```'):
            data = image_preview(); data['page']['text'] = page(body)['text']
            self.assertEqual(CHECKS.check_image_preview(data)['status'], 'NeedsCorrection')

    def test_capture_errors_and_truncation_remain_errors(self):
        for key, value in (('isError', True), ('truncated', True)):
            data = image_preview(); data['page'][key] = value
            with self.assertRaises(ValueError):
                CHECKS.check_image_preview(data)

    def test_completion_binds_image_to_frozen_content_version_and_html(self):
        data = image_preview()
        gate = {'invocation_id': 'probe', 'publication_version': 'publication-v2',
                'required_checks': {'saved-image': {'kind': 'preview-image', 'entity_id': REPORT,
                                                   'content_version': 'reply-v2', 'html_sha256': data['html_sha256']}},
                'checks': [{'name': 'saved-image', 'invocation_id': 'probe', 'publication_version': 'publication-v2',
                            'exit_code': 0, 'result': CHECKS.check_image_preview(data)}]}
        self.assertEqual(CHECKS.completion_gate(gate)['status'], 'EligibleForCompletion')
        for key, value in (('content_version', 'reply-v3'), ('html_sha256', '0' * 64)):
            changed = copy.deepcopy(gate); changed['required_checks']['saved-image'][key] = value
            self.assertEqual(CHECKS.completion_gate(changed)['status'], 'NeedsCorrection')
        del gate['required_checks']['saved-image']['content_version']
        self.assertEqual(CHECKS.completion_gate(gate)['status'], 'NeedsCorrection')

    def test_cli_returns_failure_for_missing_actual_download(self):
        data = image_preview(); data['embedded_asset']['content_base64'] = ''
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'notion_checks.py'), 'preview-image', '--input', '-'],
                                input=json.dumps(data), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'NeedsCorrection')


if __name__ == '__main__':
    unittest.main()
