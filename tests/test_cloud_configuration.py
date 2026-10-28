"""Configuraciones ficticias y transporte simulado: no Secrets reales ni red."""
from contextlib import redirect_stdout
import io
import json
import os
import unittest
from unittest.mock import patch

import httpx
from google import genai
from streamlit.runtime.secrets import Secrets

import gemini_connectivity_check as cli
from gemini_analyzer import MODEL, ALTERNATIVE_MODEL, GeminiError, analyze_gemini, resolve_model

REAL_CLIENT = genai.Client


class CloudConfigurationTests(unittest.TestCase):
    def setUp(self):
        # Una API mal escrita tampoco debe provocar la carga perezosa de archivos.
        self.enterContext(patch.object(Secrets, '_parse', side_effect=AssertionError('No leer Secrets')))

    def test_top_level_synthetic_streamlit_config_overrides_environment(self):
        with patch.dict(os.environ, {'GEMINI_MODEL': MODEL}):
            # Instancia aislada: solo datos sintéticos, no st.secrets ni archivos.
            synthetic = Secrets()
            Secrets.merge_programmatic_secrets(synthetic, {'GEMINI_MODEL': ALTERNATIVE_MODEL})
            self.assertEqual(ALTERNATIVE_MODEL, resolve_model())
            self.assertEqual(MODEL, resolve_model(MODEL))

    def test_nested_config_is_not_promoted_and_invalid_value_is_not_echoed(self):
        with patch.dict(os.environ) as environment:
            environment.pop('GEMINI_MODEL', None)
            synthetic = Secrets()
            Secrets.merge_programmatic_secrets(synthetic, {'gemini': {'GEMINI_MODEL': ALTERNATIVE_MODEL}})
            self.assertEqual(MODEL, resolve_model())
            Secrets.merge_programmatic_secrets(synthetic, {'GEMINI_MODEL': 'private-test-detail'})
            with self.assertRaises(GeminiError) as raised:
                resolve_model()
            self.assertNotIn('private-test-detail', str(raised.exception))

    def test_offline_metadata_does_not_read_environment_values_or_key(self):
        class NamesOnly(dict):
            def get(self, *args):
                raise AssertionError('No leer valores de entorno')
            def __getitem__(self, name):
                raise AssertionError('No leer valores de entorno')
        with patch.object(cli.os, 'environ', NamesOnly(HTTPS_PROXY='private-test-detail', GEMINI_API_KEY='unused-placeholder')):
            with patch.object(cli, 'get_api_key', side_effect=AssertionError('No leer claves')):
                data = cli.runtime_metadata(MODEL)
        self.assertTrue(data['environment_names_present']['HTTPS_PROXY'])
        self.assertNotIn('private-test-detail', json.dumps(data))
        self.assertNotIn('GEMINI_API_KEY', json.dumps(data))

    def test_runtime_flag_does_not_authorize_probe(self):
        with patch.dict(os.environ) as environment:
            environment.pop('GEMINI_MODEL', None)
            with patch.object(cli, 'get_api_key') as key, patch.object(cli, 'check_connectivity_once') as call:
                for flags in ([], ['--execute-once'], ['--confirm-cost']):
                    with redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(0, cli.main(['--runtime-info', *flags]))
                    lines = [json.loads(line) for line in output.getvalue().splitlines()]
                    self.assertIn('runtime', lines[0])
                    self.assertFalse(lines[-1]['request_executed'])
                key.assert_not_called()
                call.assert_not_called()

    def test_unknown_package_version_or_platform_cannot_leak_details(self):
        with patch.object(cli.metadata, 'version', return_value='/private-test-detail'), patch.object(cli.platform, 'system', return_value='private-test-detail'):
            data = cli.runtime_metadata(MODEL)
        self.assertEqual('Other', data['os'])
        self.assertEqual({'unknown'}, set(data['packages'].values()))
        self.assertNotIn('private-test-detail', json.dumps(data))

    def test_503_is_single_post_on_developer_endpoint_even_with_vertex_env(self):
        requests = []
        def handler(request):
            requests.append(request)
            # HTTP 503 no debe convertirse en un mensaje de cuota agotada.
            return httpx.Response(503, json={'error': {'code': 503, 'status': 'UNAVAILABLE', 'message': 'private-test-detail'}})
        def create_client(**kwargs):
            kwargs['http_options'].client_args.update({'transport': httpx.MockTransport(handler), 'trust_env': False})
            return REAL_CLIENT(**kwargs)
        with patch.dict(os.environ, {'GOOGLE_GENAI_USE_VERTEXAI': 'true', 'GOOGLE_GENAI_USE_ENTERPRISE': 'true', 'GEMINI_MODEL': MODEL}):
            with patch('google.genai.Client', side_effect=create_client):
                with self.assertRaises(GeminiError) as raised:
                    analyze_gemini('SELECT 1;', api_key='unit-test-placeholder')
        self.assertEqual(503, raised.exception.diagnostic['http_status'])
        self.assertIn('503', str(raised.exception))
        self.assertNotIn('cuota', str(raised.exception))
        self.assertNotIn('private-test-detail', str(raised.exception))
        self.assertEqual(1, len(requests))
        self.assertEqual('POST', requests[0].method)
        self.assertEqual('generativelanguage.googleapis.com', requests[0].url.host)
        self.assertEqual(f'/v1beta/models/{MODEL}:generateContent', requests[0].url.path)
        self.assertEqual(60.0, requests[0].extensions['timeout']['read'])

    def test_runtime_info_and_authorized_probe_make_only_one_mock_call(self):
        with patch.dict(os.environ, {'GEMINI_MODEL': MODEL}):
            with patch.object(cli, 'key_present_in_environment', return_value=True), patch.object(cli, 'get_api_key', return_value='unit-test-placeholder'):
                with patch.object(cli, 'check_connectivity_once', return_value={'response_received': True}) as probe, redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(0, cli.main(['--runtime-info', '--execute-once', '--confirm-cost']))
                probe.assert_called_once_with(api_key='unit-test-placeholder', model=MODEL)
                self.assertNotIn('unit-test-placeholder', output.getvalue())

    def test_runtime_info_cannot_retry_a_503(self):
        failure = GeminiError('Servicio temporalmente no disponible (HTTP 503).', http_status=503, operation='connectivity')
        with patch.dict(os.environ, {'GEMINI_MODEL': MODEL}):
            with patch.object(cli, 'key_present_in_environment', return_value=True), patch.object(cli, 'get_api_key', return_value='unit-test-placeholder'):
                with patch.object(cli, 'check_connectivity_once', side_effect=failure) as probe, redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(1, cli.main(['--runtime-info', '--execute-once', '--confirm-cost']))
                probe.assert_called_once()
                self.assertEqual(503, json.loads(output.getvalue().splitlines()[-1])['http_status'])
                self.assertNotIn('unit-test-placeholder', output.getvalue())


if __name__ == '__main__':
    unittest.main()
