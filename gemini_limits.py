"""Presupuesto EN MEMORIA de un proceso: solo contadores, tiempos y un lock.

No es persistente, distribuido ni una cuota por persona. No guarda identificadores,
consultas, respuestas o credenciales. No mantener el lock durante una llamada HTTP.
"""
from dataclasses import dataclass
import math
import os
from threading import Lock
import time


class LimitConfigError(Exception):
    """Configuración inválida: Gemini se bloquea, el análisis local continúa."""


class QuotaExceeded(Exception):
    def __init__(self, reason, message):
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class Limits:
    session_limit: int = 3
    cooldown_seconds: int = 30
    global_limit: int = 20

    def __post_init__(self):
        for value in (self.session_limit, self.cooldown_seconds, self.global_limit):
            if type(value) is not int or value < 0:
                raise LimitConfigError('La configuración de límites Gemini no es válida. Usa el análisis local y avisa al responsable.')


def load_limits(environ=None):
    """Lee únicamente tres parámetros públicos de entorno, nunca secretos."""
    source = os.environ if environ is None else environ
    try:
        return Limits(
            session_limit=int(source.get('DATAFLOW_GEMINI_SESSION_LIMIT', '3')),
            cooldown_seconds=int(source.get('DATAFLOW_GEMINI_COOLDOWN_SECONDS', '30')),
            global_limit=int(source.get('DATAFLOW_GEMINI_GLOBAL_LIMIT', '20')),
        )
    except (ValueError, TypeError, LimitConfigError):
        # Nunca reflejar valores de entorno en mensajes o logs.
        raise LimitConfigError('La configuración de límites Gemini no es válida. Usa el análisis local y avisa al responsable.') from None


@dataclass
class SessionUsage:
    used: int = 0
    last_request_at: float | None = None


class RequestLimiter:
    def __init__(self, clock=time.monotonic):
        self._used = 0
        self._lock = Lock()
        self._clock = clock

    @property
    def used(self):
        with self._lock:
            return self._used

    def _check(self, session, limits, now):
        if session.used >= limits.session_limit:
            raise QuotaExceeded('session', 'Has alcanzado el límite de intentos Gemini de esta sesión. Puedes continuar con el análisis local ilimitado.')
        if self._used >= limits.global_limit:
            raise QuotaExceeded('global', 'Se ha agotado el presupuesto Gemini compartido de esta instancia. Puedes continuar con el análisis local ilimitado.')
        if session.last_request_at is not None:
            remaining = limits.cooldown_seconds - (now - session.last_request_at)
            if remaining > 0:
                raise QuotaExceeded('cooldown', f'Espera {math.ceil(remaining)} s antes de otro intento Gemini. Mientras tanto puedes usar el análisis local ilimitado.')

    def check(self, session, limits):
        """Precomprobación sin consumir: evita leer la clave si ya se bloquea."""
        with self._lock:
            self._check(session, limits, self._clock())

    def reserve(self, session, limits):
        """Recomprueba y reserva ambos contadores atómicamente; no se reembolsa."""
        with self._lock:
            now = self._clock()
            self._check(session, limits, now)
            self._used += 1
            session.used += 1
            session.last_request_at = now


# Python comparte este módulo entre sesiones y reruns del MISMO proceso.
# No usar un caché por configuración: cambiar los límites no reinicia el consumo.
_GLOBAL_LIMITER = RequestLimiter()


def get_limiter():
    return _GLOBAL_LIMITER
