"""Flujo Gemini y recuperación local con clientes simulados."""
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
from google.genai import errors
from streamlit.testing.v1 import AppTest

from test_gemini_analyzer import EXAMPLE_RESULT
from gemini_limits import RequestLimiter


class GeminiAppTests(unittest.TestCase):
    def setUp(self):
        environment = self.enterContext(patch.dict(os.environ))
        environment.pop('GEMINI_MODEL', None)
        for name in ('DATAFLOW_GEMINI_SESSION_LIMIT', 'DATAFLOW_GEMINI_GLOBAL_LIMIT', 'DATAFLOW_GEMINI_COOLDOWN_SECONDS'):
            environment.pop(name, None)
        self.limiter = RequestLimiter()
        self.enterContext(patch('gemini_limits.get_limiter', return_value=self.limiter))
        self.factory = self.enterContext(patch('google.genai.Client'))
        self.client = self.factory.return_value.__enter__.return_value
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(EXAMPLE_RESULT))
        self.key = self.enterContext(patch('gemini_analyzer.get_api_key', return_value='unit-test-placeholder'))
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.app.radio[1].set_value('Gemini (opcional)').run()
        self.app.text_area[0].input('SELEC nombre FROM empleados;').run()

    def authorize(self):
        self.app.checkbox[0].check().run()

    def test_selection_and_missing_consent_do_not_send(self):
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.factory.assert_not_called()
        self.key.assert_not_called()
        self.assertTrue(any('Autoriza' in element.value for element in self.app.warning))

    def test_success_renders_structured_analysis(self):
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.client.models.generate_content.assert_called_once()
        self.assertEqual('Resultado de Gemini', self.app.subheader[0].value)
        self.assertTrue(any('pueden ser incorrectas' in item.value for item in self.app.caption))

    def test_configured_model_is_visible_and_used(self):
        with patch.dict(os.environ, {'GEMINI_MODEL': 'gemini-3.8-flash'}):
            self.app.run()
            self.assertTrue(any('gemini-3.8-flash' in item.value for item in self.app.info))
            self.authorize()
            self.app.button[0].click().run()
        self.assertEqual('gemini-3.8-flash', self.client.models.generate_content.call_args.kwargs['model'])
        self.client.models.generate_content.assert_called_once()

    def test_default_lite_functional_sql_flow(self):
        result = copy.deepcopy(EXAMPLE_RESULT)
        result['categoria'] = 'Posible división por cero'
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(result))
        self.app.text_area[0].input('SELECT importe / 0 FROM ventas;').run()
        self.assertTrue(any('gemini-3.5-flash-lite' in item.value for item in self.app.info))
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(0, len(self.app.error))
        self.assertEqual('Resultado de Gemini', self.app.subheader[0].value)
        self.assertTrue(any('división por cero' in item.value for item in self.app.text))
        request = self.client.models.generate_content.call_args.kwargs
        self.assertEqual('gemini-3.5-flash-lite', request['model'])
        self.assertIsNotNone(request['config'].response_json_schema)
        self.client.models.generate_content.assert_called_once()

    def test_error_offers_local_analysis_without_resending(self):
        self.client.models.generate_content.side_effect = ConnectionError('private-test-detail')
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('conectar', self.app.error[0].value)
        self.assertNotIn('private-test-detail', self.app.error[0].value)
        self.app.button[1].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('sintaxis', self.app.subheader[0].value)
        self.client.models.generate_content.assert_called_once()

    def test_missing_key_does_not_create_client(self):
        self.key.return_value = ''
        self.authorize()
        self.app.button[0].click().run()
        self.assertIn('Falta configurar', self.app.error[0].value)
        self.factory.assert_not_called()

    def test_technical_diagnostic_is_hidden_by_default(self):
        self.enterContext(patch('gemini_analyzer.local_diagnostics_enabled', return_value=False))
        self.client.models.generate_content.side_effect = errors.ServerError(503, {'message': 'private-test-detail'})
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('503', self.app.error[0].value)
        self.assertEqual(0, len(self.app.json))
        self.assertNotIn('gemini_diagnostic', self.app.session_state)

    def test_local_diagnostic_shows_only_safe_metadata(self):
        self.enterContext(patch('gemini_analyzer.local_diagnostics_enabled', return_value=True))
        self.client.models.generate_content.side_effect = errors.ServerError(500, {'message': 'private-test-detail'})
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        data = json.loads(self.app.json[0].value)
        self.assertEqual(500, data['http_status'])
        self.assertEqual('ServerError', data['exception_class'])
        self.assertNotIn('private-test-detail', self.app.json[0].value)
        self.assertNotIn('unit-test-placeholder', self.app.json[0].value)
        self.app.text_area[0].input('SELECT nombre FROM empleados;').run()
        self.assertEqual(0, len(self.app.json))
        self.assertNotIn('gemini_diagnostic', self.app.session_state)

    def test_timeout_then_local_fallback_for_reported_query(self):
        self.app.text_area[0].input('SELECT importe / 0 FROM ventas;').run()
        self.client.models.generate_content.side_effect = httpx.ReadTimeout('private-test-detail')
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('recibir la respuesta', self.app.error[0].value)
        self.assertIn('podría seguir procesándose', self.app.error[0].value)
        self.assertNotIn('private-test-detail', self.app.error[0].value)
        self.app.button[1].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('división por cero', self.app.subheader[0].value)
        self.client.models.generate_content.assert_called_once()

    def test_edited_text_revokes_consent(self):
        self.authorize()
        self.app.text_area[0].input('SELECT nombre FROM empleados;').run()
        self.assertFalse(self.app.checkbox[0].value)
        self.app.button[0].click().run()
        self.factory.assert_not_called()

    def test_input_type_change_revokes_consent(self):
        self.authorize()
        self.app.radio[0].set_value('Mensaje de error ETL').run()
        self.assertFalse(self.app.checkbox[0].value)
        self.factory.assert_not_called()

    def test_model_output_is_plain_text(self):
        result = copy.deepcopy(EXAMPLE_RESULT)
        payload = '![imagen](https://example.invalid/pixel) <script>demo</script>'
        result['explicacion'] = payload
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(result))
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any(payload == item.value for item in self.app.text))
        self.assertFalse(any(payload in item.value for item in self.app.markdown))

    def test_clear_button_removes_input_result_and_permission_without_request(self):
        self.authorize()
        self.app.button[0].click().run()
        clear_button = next(item for item in self.app.button if item.label == 'Borrar texto y resultado')
        clear_button.click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual('', self.app.text_area[0].value)
        self.assertEqual('Escribir mi propio texto', self.app.selectbox[0].value)
        self.assertFalse(self.app.checkbox[0].value)
        self.assertEqual(0, len(self.app.subheader))
        self.assertEqual(1, self.app.session_state['gemini_usage'].used)
        self.assertNotIn('gemini_error', self.app.session_state)
        self.assertNotIn('gemini_diagnostic', self.app.session_state)
        self.client.models.generate_content.assert_called_once()

    def test_two_sessions_keep_inputs_consent_and_outputs_separate(self):
        first_result = copy.deepcopy(EXAMPLE_RESULT)
        first_result['explicacion'] = 'Resultado ficticio de la sesión A.'
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(first_result))
        self.app.text_area[0].input('Texto ficticio de la sesión A').run()
        self.authorize()
        self.app.button[0].click().run()

        other = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertEqual('', other.text_area[0].value)
        other.radio[1].set_value('Gemini (opcional)').run()
        self.assertFalse(other.checkbox[0].value)
        other.text_area[0].input('Texto ficticio de la sesión B').run()
        second_result = copy.deepcopy(EXAMPLE_RESULT)
        second_result['explicacion'] = 'Resultado ficticio de la sesión B.'
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(second_result))
        other.checkbox[0].check().run()
        other.button[0].click().run()
        self.assertFalse(other.exception)
        self.assertTrue(any(first_result['explicacion'] == item.value for item in self.app.text))
        self.assertFalse(any(first_result['explicacion'] == item.value for item in other.text))
        self.assertTrue(any(second_result['explicacion'] == item.value for item in other.text))

        next(item for item in self.app.button if item.label == 'Borrar texto y resultado').click().run()
        self.assertEqual('', self.app.text_area[0].value)
        self.assertEqual('Texto ficticio de la sesión B', other.text_area[0].value)
        self.assertEqual(2, self.client.models.generate_content.call_count)
        for app in (self.app, other):
            for field in ('api_key', 'GEMINI_API_KEY', 'result', 'response'):
                self.assertNotIn(field, app.session_state)
            for group in (app.text, app.markdown, app.caption, app.info, app.warning, app.error):
                self.assertFalse(any('unit-test-placeholder' in item.value for item in group))

    def test_fictitious_etl_example_with_spanish_structured_output(self):
        text = (Path(__file__).resolve().parents[1] / 'examples' / 'error_etl_ficticio.txt').read_text(encoding='utf-8')
        result = copy.deepcopy(EXAMPLE_RESULT)
        result.update(categoria='Posible error de conversión',
                      explicacion='El mensaje indica que N/D no se pudo convertir a decimal.',
                      hechos=['Se intenta convertir el campo importe.'],
                      hipotesis=['N/D podría representar un dato ausente.'],
                      correcciones=['Valida el formato y trata los registros rechazados explícitamente.'],
                      recomendaciones=['No conviertas el marcador automáticamente en cero.'])
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(result, ensure_ascii=False))
        self.app.radio[0].set_value('Mensaje de error ETL').run()
        self.app.text_area[0].input(text).run()
        self.authorize()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any(result['explicacion'] == item.value for item in self.app.text))
        self.assertTrue(any('Hipótesis por validar' in item.value for item in self.app.markdown))
        request = self.client.models.generate_content.call_args.kwargs
        self.assertEqual('Mensaje de error ETL', json.loads(request['contents'])['tipo'])
        self.assertEqual(text, json.loads(request['contents'])['texto_no_confiable'])
        self.client.models.generate_content.assert_called_once()


if __name__ == '__main__':
    unittest.main()
