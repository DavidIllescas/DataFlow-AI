"""Comprueba con Git real qué archivos entrarían en la publicación."""
from pathlib import Path
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from gemini_analyzer import local_diagnostics_enabled


class ProductionConfigTests(unittest.TestCase):
    def test_devcontainer_starts_streamlit_with_default_security(self):
        project = Path(__file__).resolve().parents[1]
        text = (project / '.devcontainer/devcontainer.json').read_text(encoding='utf-8')
        # El archivo JSONC remoto usa únicamente comentarios de línea completa.
        data = json.loads('\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('//')))
        command = shlex.split(data['postAttachCommand']['server'])
        self.assertEqual(['streamlit', 'run', 'app.py'], command)
        self.assertIn(8501, data['forwardPorts'])
        self.assertEqual('mcr.microsoft.com/devcontainers/python:1-3.11-bookworm', data['image'])
        from streamlit import config
        self.assertTrue(config.get_option('server.enableCORS'))
        self.assertTrue(config.get_option('server.enableXsrfProtection'))

    def test_versioned_cloud_config_keeps_diagnostics_disabled(self):
        project = Path(__file__).resolve().parents[1]
        config = tomllib.loads((project / '.streamlit/config.toml').read_text(encoding='utf-8'))
        address = config.get('server', {}).get('address')
        # Incluso un flag residual no habilita el panel con la configuración Cloud.
        with patch.dict(os.environ, {'DATAFLOW_LOCAL_DIAGNOSTICS': '1'}):
            self.assertFalse(local_diagnostics_enabled(address))


@unittest.skipUnless(shutil.which('git'), 'Git no está instalado')
class DeploymentIgnoreTests(unittest.TestCase):
    def test_private_files_are_ignored_and_deployment_files_are_kept(self):
        project = Path(__file__).resolve().parents[1]
        private = [
            '.venv/Scripts/python.exe', '.venv/bin/python',
            '__pycache__/analyzer.cpython-312.pyc', 'tests/__pycache__/test_app.pyc',
            '.pytest_cache/v/cache/nodeids', 'notes.tmp', 'backup.bak', 'server.log',
            '.env', '.env.local', '.env.production', '.streamlit/secrets.toml',
            'nested/.streamlit/secrets.toml', '.aws/credentials', '.ssh/id_rsa',
            'credentials.json', 'secrets.json', 'token.json', 'service-account-demo.json',
            'private.pem', 'private.key', 'certificate.pfx',
        ]
        public = [
            'assets/studio.css', 'tests/test_studio_ui.py', 'tests/test_clean_imports.py',
            'gemini_limits.py', 'tests/test_gemini_limits.py', 'tests/test_app_limits.py',
            '.devcontainer/devcontainer.json',
            'app.py', 'analyzer.py', 'gemini_analyzer.py', 'requirements.txt', '.streamlit/config.toml',
            'gemini_connectivity_check.py', 'tests/test_connectivity_cli.py',
            'examples/error_etl_ficticio.txt',
            'README.md', 'AGENTS.md', 'especificacion.md',
            'tests/test_analyzer.py', 'tests/test_app.py', 'tests/test_deployment.py',
            'tests/test_gemini_analyzer.py', 'tests/test_app_gemini.py',
            '.env.example', '.env.template',
        ]
        # Solo inicializa un repositorio temporal; no cambia el proyecto ni usa red.
        with tempfile.TemporaryDirectory(prefix='dataflow-ignore-') as folder:
            shutil.copyfile(project / '.gitignore', Path(folder) / '.gitignore')
            subprocess.run(['git', 'init', '-q', folder], check=True, capture_output=True)
            result = subprocess.run(
                ['git', '-c', 'core.excludesFile=', '-C', folder,
                 'check-ignore', '--no-index', '--stdin', '-z'],
                input=('\0'.join(private + public) + '\0').encode('utf-8'),
                capture_output=True, check=True,
            )
        self.assertEqual(set(private), set(result.stdout.decode('utf-8').rstrip('\0').split('\0')))


if __name__ == '__main__':
    unittest.main()
