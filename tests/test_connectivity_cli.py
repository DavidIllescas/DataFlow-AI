"""Solo simulaciones: nunca ejecutar la sonda contra Google en las pruebas."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import logging
import os
import unittest
from unittest.mock import patch

from google.genai import errors
import gemini_connectivity_check as cli
from gemini_analyzer import ALTERNATIVE_MODEL, TEST_MODEL


class ConnectivityCliTests(unittest.TestCase):
    def setUp(self):
        environment = self.enterContext(patch.dict(os.environ))
        environment.pop('GEMINI_MODEL', None)
        self.factory = self.enterContext(patch('google.genai.Client'))
        self.key = self.enterContext(patch('gemini_connectivity_check.get_api_key', return_value='unit-test-placeholder'))
        self.present = self.enterContext(patch('gemini_connectivity_check.key_present_in_environment', return_value=True))

    def test_default_and_partial_flags_never_call_or_read_key(self):
        for args in ([], ['--execute-once'], ['--confirm-cost']):
            with self.subTest(args=args), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(0, cli.main(args))
                self.assertFalse(json.loads(output.getvalue())['request_executed'])
        self.key.assert_not_called()
        self.factory.assert_not_called()

    def test_missing_key_stops_before_client_creation(self):
        self.present.return_value = False
        with redirect_stdout(io.StringIO()):
            self.assertEqual(2, cli.main(['--execute-once', '--confirm-cost']))
        self.key.assert_not_called()
        self.factory.assert_not_called()

    def test_authorized_flags_make_one_mock_call_without_response_output(self):
        client = self.factory.return_value.__enter__.return_value
        client.models.generate_content.return_value = object()
        previous = logging.root.manager.disable
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, cli.main(['--execute-once', '--confirm-cost']))
        result = json.loads(output.getvalue().splitlines()[-1])
        self.assertTrue(result['response_received'])
        self.assertEqual(TEST_MODEL, result['model'])
        self.assertNotIn('unit-test-placeholder', output.getvalue())
        self.assertEqual(previous, logging.root.manager.disable)
        client.models.generate_content.assert_called_once()

    def test_error_only_outputs_sanitized_metadata(self):
        client = self.factory.return_value.__enter__.return_value
        client.models.generate_content.side_effect = errors.ServerError(500, {'message': 'private-test-detail'})
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(1, cli.main(['--execute-once', '--confirm-cost']))
        self.assertIn('ServerError', output.getvalue())
        self.assertIn('500', output.getvalue())
        self.assertNotIn('private-test-detail', output.getvalue())
        self.assertNotIn('unit-test-placeholder', output.getvalue())
        client.models.generate_content.assert_called_once()

    def test_invalid_arguments_are_not_echoed(self):
        with redirect_stderr(io.StringIO()) as output, self.assertRaises(SystemExit):
            cli.main(['--private-test-detail'])
        self.assertNotIn('private-test-detail', output.getvalue())
        self.factory.assert_not_called()

    def test_explicit_model_is_shown_and_passed_once(self):
        for model in (ALTERNATIVE_MODEL, TEST_MODEL):
            with self.subTest(model=model), redirect_stdout(io.StringIO()) as output:
                self.factory.reset_mock()
                self.assertEqual(0, cli.main(['--model', model, '--execute-once', '--confirm-cost']))
                lines = output.getvalue().splitlines()
                self.assertEqual(model, json.loads(lines[0])['model'])
                self.assertEqual(model, json.loads(lines[-1])['model'])
                client = self.factory.return_value.__enter__.return_value
                client.models.generate_content.assert_called_once()
                self.assertEqual(model, client.models.generate_content.call_args.kwargs['model'])

    def test_environment_model_and_cli_override_without_calls(self):
        with patch.dict(os.environ, {'GEMINI_MODEL': ALTERNATIVE_MODEL}):
            with redirect_stdout(io.StringIO()) as output:
                cli.main([])
            self.assertEqual(ALTERNATIVE_MODEL, json.loads(output.getvalue())['model'])
            with redirect_stdout(io.StringIO()) as output:
                cli.main(['--model', TEST_MODEL])
            self.assertEqual(TEST_MODEL, json.loads(output.getvalue())['model'])
        self.factory.assert_not_called()
        self.key.assert_not_called()

    def test_invalid_configuration_stops_without_leaking_value(self):
        with patch.dict(os.environ, {'GEMINI_MODEL': 'private-test-detail'}), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(2, cli.main(['--execute-once', '--confirm-cost']))
        self.assertNotIn('private-test-detail', output.getvalue())
        self.factory.assert_not_called()
        self.key.assert_not_called()


if __name__ == '__main__':
    unittest.main()
