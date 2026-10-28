"""Pruebas del flujo de entrada y análisis, sin navegador ni servicios externos."""
from pathlib import Path
import unittest
import os
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from analyzer import EXAMPLES


class AppTests(unittest.TestCase):
    def setUp(self):
        # Cualquier intento de usar Gemini desde el modo local hace fallar el test.
        client = self.enterContext(patch('google.genai.Client', side_effect=AssertionError('Red prohibida en tests')))
        self.addCleanup(client.assert_not_called)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()

    def test_empty_input_shows_friendly_error(self):
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('Introduce una consulta', self.app.error[0].value)

    def test_local_mode_works_with_invalid_gemini_model_configuration(self):
        with patch.dict(os.environ, {'GEMINI_MODEL': 'private-test-detail'}):
            self.app.text_area[0].input('SELECT importe / 0 FROM ventas;').run()
            self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertIn('división por cero', self.app.subheader[0].value)

    def test_examples_load_in_both_modes(self):
        for mode in ('Consulta SQL', 'Mensaje de error ETL'):
            self.app.radio[0].set_value(mode).run()
            for label, text in EXAMPLES.items():
                with self.subTest(mode=mode, example=label):
                    self.app.selectbox[0].select(label).run()
                    self.assertEqual(text, self.app.text_area[0].value)
                    self.app.button[0].click().run()
                    self.assertFalse(self.app.exception)
                    expected = 'no encontrada' if label == 'Columna inexistente' else label.lower()
                    self.assertIn(expected, self.app.subheader[0].value.lower())

    def test_edited_example_is_analyzed(self):
        self.app.selectbox[0].select('Error de sintaxis').run()
        self.app.text_area[0].input('SELECT nombre FROM empleados;').run()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual('Revisión general', self.app.subheader[0].value)

    def test_switch_to_custom_text_clears_example(self):
        self.app.selectbox[0].select('Error de sintaxis').run()
        self.app.selectbox[0].select('Escribir mi propio texto').run()
        self.assertEqual('', self.app.text_area[0].value)

    def test_general_review_displays_limits_and_actionable_advice(self):
        self.app.text_area[0].input('SELECT nombre FROM empleados;').run()
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)
        rendered = '\n'.join(element.value for element in self.app.markdown)
        self.assertIn('no permite confirmar', rendered)
        self.assertIn('documentación del motor SQL o de la herramienta ETL', rendered)
        self.assertNotIn('error ficticio', rendered)


if __name__ == '__main__':
    unittest.main()
