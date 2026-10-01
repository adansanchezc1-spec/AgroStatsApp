"""
Cliente HTTP Resiliente con Reintentos Exponenciales
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: PEP 8, Principio SRP (Single Responsibility), Resiliencia Cloud
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .constants import (
    HTTP_TIMEOUT_SECONDS,
    MAX_HTTP_RETRIES,
    RETRY_BACKOFF_FACTOR,
    USER_AGENT,
)

logger = logging.getLogger(__name__)


class ResilientHttpClient:
    """
    Cliente HTTP con reintentos exponenciales, manejo de backoff y sesiones persistentes.
    Cumple con el estándar de robustez para ingesta de datos gubernamentales.
    """

    def __init__(
        self,
        timeout: int = HTTP_TIMEOUT_SECONDS,
        max_retries: int = MAX_HTTP_RETRIES,
        backoff_factor: float = RETRY_BACKOFF_FACTOR,
        user_agent: str = USER_AGENT,
    ) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def close(self) -> None:
        """Cierra la sesión HTTP persistente."""
        self.session.close()

    def __enter__(self) -> "ResilientHttpClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
        raise_for_status: bool = True,
    ) -> requests.Response:
        """
        Ejecuta una petición GET con manejo de excepciones y reintentos.
        """
        try:
            merged_headers = self.session.headers.copy()
            if headers:
                merged_headers.update(headers)

            response = self.session.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=self.timeout,
                stream=stream,
            )
            if raise_for_status:
                response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            logger.error("Error en petición HTTP a %s: %s", url, exc)
            raise

    def download_file(self, url: str, destination_path: Union[str, Path]) -> Path:
        """
        Descarga un archivo binario o texto en chunks para optimizar memoria.
        """
        dest = Path(destination_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Iniciando descarga streaming desde: %s hacia %s", url, dest)
        response = self.get(url, stream=True, raise_for_status=True)
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        logger.info("Archivo guardado exitosamente en: %s", dest)
        return dest
