"""Sonda de consola privada del administrador; sin autorización no llama a Google.

No importar desde app.py ni conectar a rutas, botones, query params o tareas de
arranque. El control de acceso lo proporciona la consola privada del alojamiento,
no estos flags. No se presupone acceso a una consola en Community Cloud.
"""
import argparse
from importlib import metadata
import json
import logging
import os
import platform
import re
import sys

from gemini_analyzer import (
    TEST_MODEL, SUPPORTED_MODELS, MAX_ATTEMPTS, TIMEOUT_MS, GeminiError,
    check_connectivity_once, get_api_key, key_present_in_environment, resolve_model,
)


def runtime_metadata(model, *, explicit_model=False):
    """Lista cerrada offline; no leer Secrets, claves, URLs de proxy ni rutas."""
    versions = {}
    for package in ('streamlit', 'google-genai', 'httpx'):
        try:
            value = metadata.version(package)
        except Exception:
            value = 'unknown'
        versions[package] = value if re.fullmatch(r'[0-9][0-9A-Za-z.+_-]{0,63}', value) else 'unknown'
    system = platform.system()
    return {
        'model': model if model in SUPPORTED_MODELS else None,
        'model_source': 'explicit' if explicit_model else 'environment' if 'GEMINI_MODEL' in os.environ else 'default',
        'os': system if system in ('Windows', 'Linux', 'Darwin') else 'Other',
        'python': '.'.join(str(part) for part in sys.version_info[:3]),
        'packages': versions,
        'configured_base_url': 'https://generativelanguage.googleapis.com',
        'api_version_policy': 'sdk_default',
        'expected_api_version_pinned_sdk': 'v1beta',
        'timeout_ms': TIMEOUT_MS, 'max_attempts': MAX_ATTEMPTS,
        'follow_redirects': False,
        'environment_names_present': {
            name: name in os.environ for name in (
                'HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy',
                'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy',
                'SSL_CERT_FILE', 'SSL_CERT_DIR', 'GOOGLE_GENAI_HTTP_CLIENT',
            )
        },
    }


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # No reflejar argumentos desconocidos que pudieran incluir secretos.
        self.exit(2, 'Argumentos no válidos. Consulta --help; no pases claves como argumentos.\n')


def main(argv=None):
    parser = SafeArgumentParser(description=__doc__)
    parser.add_argument('--runtime-info', action='store_true', help='Añadir metadatos saneados offline, solo para consola privada; no habilita llamadas.')
    parser.add_argument('--model', choices=SUPPORTED_MODELS, help='Modelo explícito; prioridad sobre GEMINI_MODEL. Predeterminado de prueba: gemini-3.5-flash-lite.')
    parser.add_argument('--execute-once', action='store_true', help='Ejecutar una petición real; requiere autorización previa.')
    parser.add_argument('--confirm-cost', action='store_true', help='Confirmar posible consumo de cuota/coste para esa única petición.')
    args = parser.parse_args(argv)
    try:
        selected_model = resolve_model(args.model, default=TEST_MODEL)
    except GeminiError as exc:
        print(str(exc))
        print(json.dumps(exc.diagnostic))
        return 2
    present = key_present_in_environment()
    if args.runtime_info:
        print(json.dumps({'runtime': runtime_metadata(selected_model, explicit_model=args.model is not None)}))
    if not (args.execute_once and args.confirm_cost):
        print(json.dumps({
            'api_key_in_environment': present, 'request_executed': False,
            'model': selected_model, 'timeout_ms': TIMEOUT_MS, 'max_attempts': MAX_ATTEMPTS,
        }))
        return 0
    if not present:
        print(json.dumps({'model': selected_model, 'api_key_in_environment': False, 'request_executed': False}))
        return 2

    # Evitar cualquier log del SDK/transporte aunque el entorno active DEBUG.
    # El programa es local y de una sola ejecución; se restaura al terminar.
    previous_level = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        print(json.dumps({'model': selected_model, 'request_starting': True, 'timeout_ms': TIMEOUT_MS, 'max_attempts': MAX_ATTEMPTS}), flush=True)
        result = check_connectivity_once(api_key=get_api_key(), model=selected_model)
        print(json.dumps(result))
        return 0
    except GeminiError as exc:
        print(str(exc))  # Solo mensajes creados y saneados por la aplicación.
        print(json.dumps(exc.diagnostic))
        return 1
    except Exception:
        print('No se pudo completar la prueba aislada. No se muestran detalles de la excepción.')
        return 1
    finally:
        logging.disable(previous_level)


if __name__ == '__main__':
    raise SystemExit(main())
