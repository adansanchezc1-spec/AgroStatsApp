"""
Pruebas Unitarias para Resiliencia, Reintentos y Circuit Breaker
Fase PDCO: CONTROL | Active Skill: 04-testing
"""

import unittest
import time
from src.ingestion.resilience import CircuitBreaker, CircuitBreakerOpenException, retry_with_backoff


class TestResilience(unittest.TestCase):
    def test_circuit_breaker_transitions(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        self.assertEqual(cb.state, "CLOSED")
        self.assertTrue(cb.can_execute())

        # Primer fallo
        cb.record_failure()
        self.assertEqual(cb.state, "CLOSED")

        # Segundo fallo -> pasa a OPEN
        cb.record_failure()
        self.assertEqual(cb.state, "OPEN")
        self.assertFalse(cb.can_execute())

        # Esperar que expire el timeout
        time.sleep(0.12)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.state, "HALF_OPEN")

        # Éxito restablece a CLOSED
        cb.record_success()
        self.assertEqual(cb.state, "CLOSED")

    def test_circuit_breaker_decorator_blocks(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1.0)

        @cb
        def failing_func():
            raise ValueError("Error simulado")

        with self.assertRaises(ValueError):
            failing_func()

        # Circuito ahora abierto
        with self.assertRaises(CircuitBreakerOpenException):
            failing_func()

    def test_retry_with_backoff_success_after_failure(self):
        attempts = 0

        @retry_with_backoff(retries=3, initial_delay=0.01, backoff_factor=1.5, jitter=False)
        def flaky_func():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ConnectionError("Fallo temporal de red")
            return "OK"

        result = flaky_func()
        self.assertEqual(result, "OK")
        self.assertEqual(attempts, 2)


if __name__ == "__main__":
    unittest.main()
