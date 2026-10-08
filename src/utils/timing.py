"""Módulo de Utilidades de Profiling y Temporización.
Fase PDCO: DEVELOPMENT
Decoradores para auditoría de latencia y desempeño.
"""

from __future__ import annotations
import functools
import time
from typing import Any, Callable, TypeVar
from src.utils.logger import get_logger

F = TypeVar("F", bound=Callable[..., Any])
logger = get_logger("timing")


def timeit(func: F) -> F:
    """Decorador que mide y registra el tiempo de ejecución en milisegundos."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info("Función '%s' completada en %.2f ms", func.__name__, duration_ms)
            return result
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("Función '%s' falló tras %.2f ms con error: %s", func.__name__, duration_ms, exc)
            raise
    return wrapper  # type: ignore
