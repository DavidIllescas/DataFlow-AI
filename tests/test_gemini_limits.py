"""Contadores y carreras concurrentes: sin SDK, red, datos ni credenciales."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from threading import Barrier
import unittest

from gemini_limits import Limits, LimitConfigError, QuotaExceeded, RequestLimiter, SessionUsage, get_limiter, load_limits


class LimitTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.limiter = RequestLimiter(clock=lambda: self.now)
        self.session = SessionUsage()

    def test_conservative_defaults_and_nonsecret_configuration(self):
        self.assertEqual(Limits(3, 30, 20), load_limits({}))
        self.assertEqual(Limits(2, 45, 8), load_limits({
            'DATAFLOW_GEMINI_SESSION_LIMIT': '2',
            'DATAFLOW_GEMINI_COOLDOWN_SECONDS': '45',
            'DATAFLOW_GEMINI_GLOBAL_LIMIT': '8',
        }))

    def test_invalid_config_is_closed_and_does_not_echo_values(self):
        for name in ('DATAFLOW_GEMINI_SESSION_LIMIT', 'DATAFLOW_GEMINI_COOLDOWN_SECONDS', 'DATAFLOW_GEMINI_GLOBAL_LIMIT'):
            for value in ('-1', '1.5', '', 'private-test-detail'):
                with self.subTest(name=name, value=value), self.assertRaises(LimitConfigError) as raised:
                    load_limits({name: value})
                self.assertNotIn('private-test-detail', str(raised.exception))

    def test_zero_budgets_disable_gemini(self):
        for limits in (Limits(session_limit=0), Limits(global_limit=0)):
            with self.subTest(limits=limits), self.assertRaises(QuotaExceeded):
                self.limiter.reserve(self.session, limits)
        self.assertEqual(0, self.limiter.used)

    def test_session_cap_and_independent_session_budget(self):
        limits = Limits(2, 0, 10)
        self.limiter.reserve(self.session, limits)
        self.limiter.reserve(self.session, limits)
        with self.assertRaises(QuotaExceeded) as raised:
            self.limiter.reserve(self.session, limits)
        self.assertEqual('session', raised.exception.reason)
        other = SessionUsage()
        self.limiter.reserve(other, limits)
        self.assertEqual(1, other.used)
        self.assertEqual(2, self.session.used)
        self.assertEqual(3, self.limiter.used)

    def test_cooldown_boundary_and_denials_do_not_consume(self):
        limits = Limits(5, 30, 10)
        self.limiter.reserve(self.session, limits)
        self.now = 129.9
        with self.assertRaises(QuotaExceeded) as raised:
            self.limiter.reserve(self.session, limits)
        self.assertEqual('cooldown', raised.exception.reason)
        self.assertEqual(1, self.limiter.used)
        self.assertEqual(100.0, self.session.last_request_at)
        self.now = 130.0
        self.limiter.reserve(self.session, limits)
        self.assertEqual(2, self.limiter.used)

    def test_new_sessions_cannot_bypass_global_cap(self):
        limits = Limits(3, 0, 2)
        for _ in range(2):
            self.limiter.reserve(SessionUsage(), limits)
        fresh = SessionUsage()
        with self.assertRaises(QuotaExceeded) as raised:
            self.limiter.reserve(fresh, limits)
        self.assertEqual('global', raised.exception.reason)
        self.assertEqual(0, fresh.used)
        self.assertEqual(2, self.limiter.used)

    def test_check_does_not_reserve_and_reserve_rechecks(self):
        limits = Limits(3, 0, 1)
        self.limiter.check(self.session, limits)
        self.assertEqual(0, self.limiter.used)
        self.limiter.reserve(SessionUsage(), limits)
        with self.assertRaises(QuotaExceeded):
            self.limiter.reserve(self.session, limits)
        self.assertEqual(0, self.session.used)

    def test_config_change_does_not_reset_global_count(self):
        self.limiter.reserve(self.session, Limits(3, 0, 20))
        with self.assertRaises(QuotaExceeded):
            self.limiter.reserve(SessionUsage(), Limits(3, 0, 1))
        self.assertEqual(1, self.limiter.used)

    def test_shared_object_is_stable_and_has_no_session_directory(self):
        self.assertIs(get_limiter(), get_limiter())
        self.limiter.reserve(self.session, Limits())
        self.assertEqual({'used': 1, 'last_request_at': 100.0}, asdict(self.session))
        self.assertEqual({'_used', '_lock', '_clock'}, set(vars(self.limiter)))

    def test_process_recreation_resets_only_the_in_memory_budget(self):
        self.limiter.reserve(self.session, Limits())
        self.assertEqual(0, RequestLimiter().used)

    def run_concurrent(self, sessions, limits):
        barrier = Barrier(len(sessions))
        def attempt(session):
            barrier.wait(timeout=5)
            try:
                self.limiter.reserve(session, limits)
                return True
            except QuotaExceeded:
                return False
        with ThreadPoolExecutor(max_workers=len(sessions)) as pool:
            return list(pool.map(attempt, sessions))

    def test_concurrent_sessions_cannot_exceed_global_cap(self):
        sessions = [SessionUsage() for _ in range(24)]
        results = self.run_concurrent(sessions, Limits(3, 0, 7))
        self.assertEqual(7, sum(results))
        self.assertEqual(7, self.limiter.used)
        self.assertEqual(7, sum(item.used for item in sessions))

    def test_concurrent_same_session_cannot_exceed_session_cap(self):
        results = self.run_concurrent([self.session] * 16, Limits(3, 0, 100))
        self.assertEqual(3, sum(results))
        self.assertEqual(3, self.session.used)
        self.assertEqual(3, self.limiter.used)

    def test_concurrent_same_session_cooldown_admits_one(self):
        results = self.run_concurrent([self.session] * 16, Limits(20, 30, 100))
        self.assertEqual(1, sum(results))
        self.assertEqual(1, self.limiter.used)


if __name__ == '__main__':
    unittest.main()
