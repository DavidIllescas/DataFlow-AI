"""Flujos de Studio con datos ficticios y acceso al proveedor bloqueado."""
import os
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from analyzer import EXAMPLES, MAX_INPUT_CHARS, analyze_local
from gemini_limits import SessionUsage


PROJECT = Path(__file__).resolve().parents[1]


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.client = self.enterContext(patch('google.genai.Client', side_effect=AssertionError('Red prohibida')))
        self.key = self.enterContext(patch('gemini_analyzer.get_api_key', side_effect=AssertionError('Lectura de secretos prohibida')))
        self.addCleanup(self.client.assert_not_called)
        self.addCleanup(self.key.assert_not_called)
        environment = self.enterContext(patch.dict(os.environ))
        environment.pop('GEMINI_MODEL', None)
        self.app = AppTest.from_file(str(PROJECT / 'app.py')).run()

    def test_workspace_has_editor_results_and_accessible_navigation_targets(self):
        self.assertFalse(self.app.exception)
        self.assertEqual('Reglas locales', self.app.radio(key='engine').value)
        self.assertEqual(MAX_INPUT_CHARS, self.app.text_area(key='input_text').max_chars)
        self.assertEqual(2, len(self.app.get('column')))
        self.assertEqual(['analisis', 'ejemplos', 'proyecto'], [item.proto.anchor for item in self.app.header])
        self.assertEqual(4, len([item for item in self.app.button if str(item.key).startswith('library_')]))

    def test_library_cases_load_and_keep_original_local_diagnoses(self):
        cases = list(EXAMPLES.items()) + [('Conversión ETL', (PROJECT / 'examples/error_etl_ficticio.txt').read_text(encoding='utf-8'))]
        for index, (_, sample) in enumerate(cases):
            with self.subTest(example=index):
                self.app.button(key=f'library_{index}').click().run()
                kind = 'Mensaje de error ETL' if index == 3 else 'Consulta SQL'
                self.assertEqual(sample, self.app.text_area(key='input_text').value)
                self.assertEqual(kind, self.app.radio(key='input_kind').value)
                self.app.button(key='analyze').click().run()
                self.assertFalse(self.app.exception)
                self.assertEqual(analyze_local(sample, kind)['categoria'], self.app.subheader[0].value)

    def test_loading_library_revokes_consent_without_resetting_usage(self):
        self.app.radio(key='engine').set_value('Gemini (opcional)').run()
        self.app.session_state['gemini_usage'] = SessionUsage(used=2, last_request_at=100.0)
        self.app.checkbox(key='gemini_permission').check().run()
        self.app.button(key='library_3').click().run()
        self.assertFalse(self.app.exception)
        self.assertFalse(self.app.checkbox(key='gemini_permission').value)
        self.assertEqual('Mensaje de error ETL', self.app.radio(key='input_kind').value)
        self.assertEqual(2, self.app.session_state['gemini_usage'].used)
        self.assertTrue(any('gemini-3.5-flash-lite' in item.value for item in self.app.info))
        self.app.button(key='analyze').click().run()
        self.assertTrue(any('Autoriza' in item.value for item in self.app.warning))

    def test_clear_library_text_removes_result_and_consent(self):
        self.app.button(key='library_1').click().run()
        self.app.button(key='analyze').click().run()
        self.assertTrue(self.app.subheader)
        self.app.button(key='clear_input').click().run()
        self.assertEqual('', self.app.text_area(key='input_text').value)
        self.assertFalse(self.app.subheader)
        self.assertFalse(self.app.session_state['gemini_permission'])

    def test_input_cannot_become_studio_html(self):
        payload = '<img src="https://invalid.example/private" onerror="alert(1)">'
        self.app.text_area(key='input_text').input(payload).run()
        self.app.button(key='analyze').click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(payload, self.app.text_area(key='input_text').value)
        self.assertTrue(self.app.get('html'))
        for element in self.app.get('html'):
            self.assertNotIn(payload, element.proto.body)

    def test_local_sections_do_not_invent_structured_findings(self):
        self.app.button(key='library_2').click().run()
        self.app.button(key='analyze').click().run()
        headings = '\n'.join(item.value for item in self.app.markdown)
        for section in ('Diagnóstico', 'Observaciones', 'Hipótesis', 'correcciones', 'Recomendaciones'):
            self.assertIn(section, headings)
        self.assertTrue(any('no genera hipótesis' in item.value for item in self.app.text))


class StudioThemeTests(unittest.TestCase):
    def test_default_dark_theme_and_local_styles_are_deployable(self):
        config = tomllib.loads((PROJECT / '.streamlit/config.toml').read_text(encoding='utf-8'))
        self.assertEqual('dark', config['theme']['base'])
        self.assertEqual('#0B1220', config['theme']['backgroundColor'])
        self.assertEqual('#111D30', config['theme']['secondaryBackgroundColor'])
        self.assertEqual('#F8FAFC', config['theme']['textColor'])
        css = (PROJECT / 'assets/studio.css').read_text(encoding='utf-8')
        self.assertNotIn('url(', css)
        self.assertNotIn('@import', css)
        self.assertNotIn('data-testid', css)
        self.assertNotIn('st-emotion-cache', css)
        self.assertIn(':focus-visible', css)


if __name__ == '__main__':
    unittest.main()
