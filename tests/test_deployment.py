"""Comprueba con Git real qué archivos entrarían en la publicación."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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
            'app.py', 'analyzer.py', 'requirements.txt', '.streamlit/config.toml',
            'README.md', 'AGENTS.md', 'especificacion.md',
            'tests/test_analyzer.py', 'tests/test_app.py', 'tests/test_deployment.py',
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
