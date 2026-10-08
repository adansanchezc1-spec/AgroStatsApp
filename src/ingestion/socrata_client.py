"""Cliente para la API SODA 2.0 de Socrata (datos.gov.co).
Fase PDCO: DEVELOPMENT
Paginación continua $limit / $offset y consumo de los 11 endpoints gubernamentales.
"""

from __future__ import annotations
from typing import Any, Dict, Generator, List, Optional
import pandas as pd

from src.config.settings import settings
from src.ingestion.base_client import BaseAPIClient
from src.utils.logger import get_logger

logger = get_logger("ingestion.socrata_client")


class SocrataClient(BaseAPIClient):
    """Cliente para extracción continua de datos abiertos gubernamentales."""

    def __init__(
        self,
        app_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 45,
    ) -> None:
        resolved_base_url = base_url or settings.SOCRATA_BASE_URL
        super().__init__(base_url=resolved_base_url, timeout_seconds=timeout_seconds)
        self.app_token = app_token or settings.SOCRATA_APP_TOKEN

        if self.app_token:
            self.session.headers["X-App-Token"] = self.app_token
            logger.info("SocrataClient inicializado con X-App-Token activo")
        else:
            logger.warning("SocrataClient inicializado sin App-Token (cuota pública limitada)")

    def check_health(self, resource_id: str) -> bool:
        """Verifica la conectividad y disponibilidad de un dataset consultando 1 registro."""
        endpoint = f"{resource_id}.json"
        try:
            resp = self.get(endpoint, params={"$limit": 1})
            return resp.status_code == 200
        except Exception as exc:
            logger.error("Healthcheck falló para recurso %s: %s", resource_id, exc)
            return False

    def fetch_page(
        self,
        resource_id: str,
        limit: int = 50000,
        offset: int = 0,
        order: str = ":id",
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Descarga una página individual de datos."""
        endpoint = f"{resource_id}.json"
        params: Dict[str, Any] = {
            "$limit": limit,
            "$offset": offset,
            "$order": order,
        }
        if extra_params:
            params.update(extra_params)

        logger.debug("Descargando %s (offset=%d, limit=%d)", resource_id, offset, limit)
        response = self.get(endpoint, params=params)
        data = response.json()
        if not isinstance(data, list):
            logger.warning("Respuesta inesperada para %s (no es lista): %s", resource_id, type(data))
            return []
        return data

    def fetch_all(
        self,
        resource_id: str,
        batch_size: int = 50000,
        max_records: Optional[int] = None,
        order: str = ":id",
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Generador que pagina continuamente hasta agotar el dataset o alcanzar max_records."""
        offset = 0
        total_retrieved = 0

        while True:
            limit = batch_size
            if max_records is not None:
                remaining = max_records - total_retrieved
                if remaining <= 0:
                    break
                limit = min(batch_size, remaining)

            page = self.fetch_page(resource_id=resource_id, limit=limit, offset=offset, order=order)
            if not page:
                logger.info("Fin de datos para recurso %s tras recuperar %d registros", resource_id, total_retrieved)
                break

            yield page
            total_retrieved += len(page)
            offset += len(page)

            if len(page) < limit:
                # La última página retornó menos registros que el límite -> fin del dataset
                break

    def fetch_dataframe(
        self,
        resource_id: str,
        batch_size: int = 50000,
        max_records: Optional[int] = None,
    ) -> pd.DataFrame:
        """Descarga todas las páginas de un dataset y las consolida en un DataFrame de pandas."""
        all_records: List[Dict[str, Any]] = []
        for batch in self.fetch_all(resource_id=resource_id, batch_size=batch_size, max_records=max_records):
            all_records.extend(batch)

        logger.info("Dataset %s consolidado en DataFrame con %d filas", resource_id, len(all_records))
        return pd.DataFrame(all_records)
