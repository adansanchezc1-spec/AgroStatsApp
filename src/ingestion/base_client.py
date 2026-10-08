"""Cliente Base Abstracto para Ingestión de APIs REST.
Fase PDCO: DEVELOPMENT | Estándar: SWEBOK v4 / Clean Code
Manejo de sesiones HTTP persistentes y reintentos exponenciales con Tenacity.
"""

from __future__ import annotations
from abc import ABC
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)
import logging

from src.utils.logger import get_logger

logger = get_logger("ingestion.base_client")


def _is_transient_error(exception: BaseException) -> bool:
    """Identifica si una excepción es un fallo transitorio de red o servidor."""
    if isinstance(exception, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if exception.response is not None:
            status = exception.response.status_code
            return status in {429, 500, 502, 503, 504}
    return False


class BaseAPIClient(ABC):
    """Clase base abstracta para conectores REST con resiliencia y reintentos."""

    def __init__(
        self,
        base_url: str = "",
        timeout_seconds: int = 30,
        max_retries: int = 4,
        backoff_factor: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self) -> None:
        """Configura headers globales y adaptadores en la sesión."""
        self.session.headers.update({
            "User-Agent": "AgroStatsApp-Ingestion-Engine/3.0.0 (Research & Production)",
            "Accept": "application/json",
        })

    def close(self) -> None:
        """Cierra la sesión HTTP persistente."""
        self.session.close()

    def __enter__(self) -> BaseAPIClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def request_with_retry(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Ejecuta una petición HTTP envuelta en política de reintentos exponenciales."""
        
        @retry(
            reraise=True,
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.backoff_factor, min=1, max=10),
            retry=retry_if_exception(_is_transient_error),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )
        def _execute() -> requests.Response:
            logger.debug("Petición HTTP %s a: %s", method, url)
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response

        return _execute()

    def get(
        self,
        endpoint_or_url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Método GET con resolución de URL y reintentos."""
        full_url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}/{endpoint_or_url.lstrip('/')}"
        return self.request_with_retry("GET", full_url, params=params, headers=headers)

    def post(
        self,
        endpoint_or_url: str,
        json_payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Método POST con resolución de URL y reintentos."""
        full_url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}/{endpoint_or_url.lstrip('/')}"
        return self.request_with_retry("POST", full_url, json_payload=json_payload, headers=headers)
