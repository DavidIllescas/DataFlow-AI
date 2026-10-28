"""Importación desde fuentes en un proceso aislado, sin red ni secretos."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CleanImportTests(unittest.TestCase):
    def test_app_and_gemini_import_from_fresh_sources(self):
        project = Path(__file__).resolve().parents[1]
        script = r'''
import ast
import importlib
import logging
from pathlib import Path
import socket
import sys
from unittest.mock import patch

logging.disable(logging.CRITICAL)
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
assert 'gemini_analyzer' not in sys.modules
assert 'app' not in sys.modules
gemini = importlib.import_module('gemini_analyzer')
assert Path(gemini.__file__).resolve() == root / 'gemini_analyzer.py'
assert callable(gemini.validate_gemini_input)

# Verificar todos los símbolos locales importados por app.py, no solo el observado.
tree = ast.parse((root / 'app.py').read_text(encoding='utf-8'))
for node in tree.body:
    if isinstance(node, ast.ImportFrom) and node.module in ('analyzer', 'gemini_analyzer', 'gemini_limits'):
        module = importlib.import_module(node.module)
        for symbol in node.names:
            assert hasattr(module, symbol.name), 'Falta un símbolo local requerido'

# La función no puede ser un stub: comprobar límites y los dos tipos de entrada.
for text, kind in (('', 'Consulta SQL'), ('   ', 'Consulta SQL'),
                   ('x' * 4001, 'Consulta SQL'), (' ' * 4000 + 'x', 'Consulta SQL'),
                   ('SELECT 1;', 'Tipo no permitido')):
    try:
        gemini.validate_gemini_input(text, kind)
    except ValueError:
        pass
    else:
        raise AssertionError('La validación dejó pasar una entrada inválida')
gemini.validate_gemini_input('x' * 4000, 'Consulta SQL')
gemini.validate_gemini_input('Mensaje ficticio ETL', 'Mensaje de error ETL')

import streamlit as st
class ForbiddenSecrets:
    def __getattr__(self, name):
        raise AssertionError('No acceder a secretos en la prueba de arranque')

with patch.object(socket.socket, 'connect', side_effect=AssertionError('Red prohibida')), \
     patch.object(st, 'secrets', new=ForbiddenSecrets()), \
     patch.object(gemini, 'get_api_key', side_effect=AssertionError('No leer claves')) as key:
    app = importlib.import_module('app')
    assert Path(app.__file__).resolve() == root / 'app.py'
    key.assert_not_called()

assert gemini.MODEL == 'gemini-3.5-flash-lite'
assert gemini.TIMEOUT_MS == 60000
assert gemini.MAX_ATTEMPTS == 1
assert 'google.genai' not in sys.modules, 'El arranque local no necesita el SDK Gemini'
print('OK: imports locales y validación reales, sin red ni secretos')
'''
        with tempfile.TemporaryDirectory(prefix='dataflow-clean-import-') as folder:
            # -I ignora PYTHONPATH/user-site; el directorio de bytecode nuevo evita
            # reutilizar .pyc previos. -B impide escribirlos durante la prueba.
            result = subprocess.run(
                [sys.executable, '-I', '-B', '-X', f'pycache_prefix={Path(folder) / "pycache"}',
                 '-c', script, str(project)],
                cwd=folder, capture_output=True, text=True, timeout=45,
            )
        self.assertEqual(0, result.returncode, 'Falló la importación aislada; revisar fuentes y símbolos locales. No se vuelca stderr por privacidad.')
        self.assertIn('OK: imports locales', result.stdout)


if __name__ == '__main__':
    unittest.main()
