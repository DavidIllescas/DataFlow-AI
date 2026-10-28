"""Cuota de interfaz con SDK y claves simulados: cero llamadas reales."""
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from google.genai import errors
from streamlit.testing.v1 import AppTest

from gemini_limits import Limits, RequestLimiter, SessionUsage
from test_gemini_analyzer import EXAMPLE_RESULT


class AppLimitTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {
            'DATAFLOW_GEMINI_SESSION_LIMIT': '2',
            'DATAFLOW_GEMINI_GLOBAL_LIMIT': '3',
            'DATAFLOW_GEMINI_COOLDOWN_SECONDS': '0',
        }))
        self.now = 100.0
        self.limiter = RequestLimiter(clock=lambda: self.now)
        self.enterContext(patch('gemini_limits.get_limiter', return_value=self.limiter))
        self.factory = self.enterContext(patch('google.genai.Client'))
        self.client = self.factory.return_value.__enter__.return_value
        self.client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(EXAMPLE_RESULT))
        self.key = self.enterContext(patch('gemini_analyzer.get_api_key', return_value='unit-test-placeholder'))
        self.app = self.new_session()

    def new_session(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertEqual('Reglas locales', app.radio[1].value)
        app.radio[1].set_value('Gemini (opcional)').run()
        app.text_area[0].input('SELECT importe / 0 FROM ventas;').run()
        app.checkbox[0].check().run()
        return app

    def click(self, app=None):
        target = self.app if app is None else app
        target.button[0].click().run()
        self.assertFalse(target.exception)

    def test_session_limit_blocks_before_key_or_sdk_and_local_fallback_works(self):
        self.click()
        self.click()
        self.click()
        self.assertTrue(any('límite de intentos' in item.value for item in self.app.warning))
        self.assertEqual(2, self.key.call_count)
        self.assertEqual(2, self.client.models.generate_content.call_count)
        self.app.button[1].click().run()
        self.assertIn('división por cero', self.app.subheader[0].value)
        self.assertEqual(2, self.client.models.generate_content.call_count)

    def test_cooldown_blocks_and_exact_boundary_allows(self):
        with patch.dict(os.environ, {'DATAFLOW_GEMINI_COOLDOWN_SECONDS': '30'}):
            self.click()
            self.now = 129.0
            self.click()
            self.assertTrue(any('Espera 1 s' in item.value for item in self.app.warning))
            self.assertEqual(1, self.key.call_count)
            self.now = 130.0
            self.click()
        self.assertEqual(2, self.client.models.generate_content.call_count)

    def test_fresh_session_cannot_bypass_shared_budget(self):
        self.click()
        other = self.new_session()
        self.click(other)
        self.click(other)
        fresh = self.new_session()
        self.click(fresh)
        self.assertEqual(0, fresh.session_state['gemini_usage'].used)
        self.assertEqual(1, self.app.session_state['gemini_usage'].used)
        self.assertEqual(2, other.session_state['gemini_usage'].used)
        self.assertTrue(any('presupuesto Gemini compartido' in item.value for item in fresh.warning))
        self.assertEqual(3, self.key.call_count)
        self.assertEqual(3, self.client.models.generate_content.call_count)

    def test_api_failures_still_consume_admitted_attempts(self):
        self.client.models.generate_content.side_effect = errors.ServerError(503, {'message': 'private-test-detail'})
        self.click()
        self.click()
        self.click()
        self.assertEqual(2, self.limiter.used)
        self.assertEqual(2, self.app.session_state['gemini_usage'].used)
        self.assertEqual(2, self.client.models.generate_content.call_count)

    def test_missing_key_does_not_consume_budget(self):
        self.key.return_value = ''
        self.click()
        self.factory.assert_not_called()
        self.assertEqual(0, self.limiter.used)
        self.assertEqual(0, self.app.session_state['gemini_usage'].used)

    def test_invalid_input_does_not_read_key_or_consume_budget(self):
        self.app.text_area[0].input('   ').run()
        self.app.checkbox[0].check().run()
        self.click()
        self.assertIn('Introduce una consulta', self.app.error[0].value)
        self.key.assert_not_called()
        self.factory.assert_not_called()
        self.assertEqual(0, self.limiter.used)

    def test_invalid_limits_fail_closed_without_leaking_configuration(self):
        with patch.dict(os.environ, {'DATAFLOW_GEMINI_GLOBAL_LIMIT': 'private-test-detail'}):
            self.click()
            self.assertTrue(any('configuración de límites' in item.value for item in self.app.warning))
            self.assertFalse(any('private-test-detail' in item.value for item in self.app.warning))
            self.app.button[1].click().run()
            self.assertIn('división por cero', self.app.subheader[0].value)
        self.key.assert_not_called()
        self.factory.assert_not_called()

    def test_clear_does_not_reset_session_budget(self):
        self.click()
        next(item for item in self.app.button if item.label == 'Borrar texto y resultado').click().run()
        self.assertEqual(1, self.app.session_state['gemini_usage'].used)
        self.app.text_area[0].input('SELECT importe / 0 FROM ventas;').run()
        self.app.checkbox[0].check().run()
        self.click()
        self.click()
        self.assertEqual(2, self.client.models.generate_content.call_count)

    def test_local_mode_is_unlimited_even_when_gemini_is_disabled(self):
        with patch.dict(os.environ, {'DATAFLOW_GEMINI_GLOBAL_LIMIT': '0', 'DATAFLOW_GEMINI_SESSION_LIMIT': '0'}):
            self.app.radio[1].set_value('Reglas locales').run()
            for _ in range(8):
                self.click()
                self.assertIn('división por cero', self.app.subheader[0].value)
        self.factory.assert_not_called()
        self.key.assert_not_called()
        self.assertEqual(0, self.limiter.used)

    def test_reservation_rechecks_after_another_session_takes_last_slot(self):
        with patch.dict(os.environ, {'DATAFLOW_GEMINI_GLOBAL_LIMIT': '1'}):
            def key_lookup(_secrets):
                self.limiter.reserve(SessionUsage(), Limits(2, 0, 1))
                return 'unit-test-placeholder'
            self.key.side_effect = key_lookup
            self.click()
        self.factory.assert_not_called()
        self.assertEqual(1, self.limiter.used)
        self.assertEqual(0, self.app.session_state['gemini_usage'].used)


if __name__ == '__main__':
    unittest.main()
