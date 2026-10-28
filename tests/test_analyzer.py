import unittest
from analyzer import EXAMPLES, analyze_local

class AnalyzerTests(unittest.TestCase):
    def test_typo(self):
        self.assertIn('sintaxis', analyze_local('SELEC nombre FROM empleados;')['categoria'])
    def test_zero(self):
        self.assertIn('división', analyze_local('SELECT total / 0 FROM ventas;')['categoria'])
    def test_unknown(self):
        self.assertIn('No se ha detectado', analyze_local('SELECT nombre FROM empleados;')['explicacion'])

    def test_general_review_expresses_uncertainty_in_both_modes(self):
        for text, kind in (('SELECT nombre FROM empleados;', 'Consulta SQL'), ('Proceso finalizado', 'Mensaje de error ETL')):
            with self.subTest(kind=kind):
                result = analyze_local(text, kind)
                self.assertEqual('Revisión general', result['categoria'])
                self.assertIn('no permite confirmar', result['explicacion'])
                self.assertIn('No se puede determinar', result['confianza'])
                self.assertNotIn('error ficticio', ' '.join(result['sugerencias']).lower())
                self.assertNotIn('gemini', ' '.join(result['sugerencias']).lower())
    def test_empty(self):
        with self.assertRaises(ValueError): analyze_local('  ')
    def test_length(self):
        with self.assertRaises(ValueError): analyze_local('x' * 4001)
    def test_unknown_column(self):
        self.assertIn('no encontrada', analyze_local('Unknown column salary')['categoria'])

    def test_length_includes_surrounding_whitespace(self):
        with self.assertRaisesRegex(ValueError, '4000'):
            analyze_local(' ' * 4000 + 'x')

    def test_length_boundary(self):
        self.assertEqual('Revisión general', analyze_local('x' * 4000)['categoria'])

    def test_nonzero_denominators(self):
        for denominator in ('0.5', '0.01', '00.5', '10', '0e-3col'):
            with self.subTest(denominator=denominator):
                self.assertEqual('Revisión general', analyze_local(f'SELECT total / {denominator} FROM ventas;')['categoria'])

    def test_zero_numeric_literals(self):
        for denominator in ('0', '0.0', '00', '.0', '-0', '+0.00', '0e3'):
            with self.subTest(denominator=denominator):
                self.assertIn('división', analyze_local(f'SELECT total / {denominator} FROM ventas;')['categoria'])

    def test_examples_match_their_labels(self):
        for label, text in EXAMPLES.items():
            with self.subTest(example=label):
                expected = 'no encontrada' if label == 'Columna inexistente' else label.lower()
                self.assertIn(expected, analyze_local(text)['categoria'].lower())

    def test_etl_error_messages(self):
        for text in ('division by zero', 'División por cero'):
            with self.subTest(text=text):
                self.assertIn('división', analyze_local(text, 'Mensaje de error ETL')['categoria'])

if __name__ == '__main__': unittest.main()
