"""
Módulo de Resiliencia, Reintentos y Circuit Breaker para Ingesta de Datos
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: SWEBOK (Software Construction & Reliability), Clean Code, PEP 8
"""

import time
import random
import logging
from typing import Callable, Any, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreakerOpenException(Exception):
    """Excepción lanzada cuando el circuito está ABIERTO debido a fallos reiterados."""
    pass


class CircuitBreaker:
    """
    Patrón Circuit Breaker para evitar sobrecargar servicios caídos o APIs externas (ej. Socrata / IDEAM).
    Estados:
      - CLOSED: Operación normal, permite solicitudes.
      - OPEN: Bloquea solicitudes temporalmente tras superar el umbral de fallos.
      - HALF_OPEN: Permite una solicitud de prueba para verificar si el servicio se recuperó.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # "CLOSED", "OPEN", "HALF_OPEN"

    def record_success(self):
        """Registra un llamado exitoso y resetea el contador de fallos."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Registra un fallo y abre el circuito si supera el umbral."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"[CircuitBreaker] Circuito ABIERTO tras {self.failure_count} fallos consecutivos. "
                f"Bloqueando llamadas por {self.recovery_timeout}s."
            )

    def can_execute(self) -> bool:
        """Verifica si se permite ejecutar la llamada."""
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("[CircuitBreaker] Transición a HALF_OPEN. Permitiendo llamada de prueba.")
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return False

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not self.can_execute():
                raise CircuitBreakerOpenException(
                    f"CircuitBreaker para {func.__name__} está ABIERTO. "
                    f"Tiempo restante: {max(0.0, self.recovery_timeout - (time.time() - self.last_failure_time)):.1f}s"
                )
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise e
        return wrapper


def retry_with_backoff(
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorador que aplica reintentos con Retroceso Exponencial (Exponential Backoff) y Jitter.
    
    :param retries: Número máximo de reintentos.
    :param initial_delay: Retardo inicial en segundos.
    :param backoff_factor: Multiplicador del retardo en cada reintento.
    :param jitter: Si True, añade ruido aleatorio para evitar 'thundering herd problem'.
    :param exceptions: Tupla de excepciones a capturar.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt == retries:
                        logger.error(
                            f"[RetryEngine] Falló intento final ({attempt}/{retries}) en {func.__name__}: {exc}"
                        )
                        raise last_exception
                    
                    sleep_time = delay + (random.uniform(0, 0.5 * delay) if jitter else 0)
                    logger.warning(
                        f"[RetryEngine] Falló intento {attempt}/{retries} en {func.__name__}: {exc}. "
                        f"Reintentando en {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
                    delay *= backoff_factor
                    
            raise last_exception
        return wrapper
    return decorator
