"""
Conector Especializado para APIs Socrata (datos.gov.co e IDEAM)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: OpenAPI/Socrata SODA 2.0, DAMA-DMBOK 2, Pandas DataFrames
"""

import logging
from typing import Any, Dict, List, Optional
import pandas as pd

from .base_client import ResilientHttpClient
from .constants import DATOS_GOV_API_URL, DEFAULT_BATCH_LIMIT

logger = logging.getLogger(__name__)


class SocrataClient:
    """
    Cliente para la API Abierta de Socrata (SODA 2.0) utilizada en datos.gov.co.
    Soporta paginación, filtros SoQL, extracción masiva y normalización tabular.
    """

    def __init__(
        self,
        base_url: str = DATOS_GOV_API_URL,
        app_token: Optional[str] = None,
        http_client: Optional[ResilientHttpClient] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.http_client = http_client or ResilientHttpClient()

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.app_token:
            headers["X-App-Token"] = self.app_token
        return headers

    def fetch_records(
        self,
        resource_id: str,
        limit: int = DEFAULT_BATCH_LIMIT,
        offset: int = 0,
        where_clause: Optional[str] = None,
        order_clause: Optional[str] = None,
        select_clause: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Consulta un lote de registros desde el endpoint Socrata con manejo explícito de errores HTTP.
        """
        url = f"{self.base_url}/{resource_id}.json"
        params: Dict[str, Any] = {"$limit": limit, "$offset": offset}
        if where_clause:
            params["$where"] = where_clause
        if order_clause:
            params["$order"] = order_clause
        if select_clause:
            params["$select"] = select_clause

        logger.info("Consultando Socrata [%s] con limit=%d, offset=%d", resource_id, limit, offset)
        response = self.http_client.get(
            url,
            params=params,
            headers=self._get_headers(),
            raise_for_status=False,
        )

        if response.status_code >= 400:
            try:
                err_data = response.json()
                error_msg = err_data.get("message", response.text[:200]) if isinstance(err_data, dict) else response.text[:200]
            except Exception:
                error_msg = response.text[:200]
            logger.error("Error en recurso Socrata %s (HTTP %d): %s", resource_id, response.status_code, error_msg)
            raise RuntimeError(f"Error Socrata [{resource_id}] HTTP {response.status_code}: {error_msg}")

        try:
            data = response.json()
        except Exception as exc:
            logger.error("Respuesta no es JSON válido para %s: %s", resource_id, exc)
            raise RuntimeError(f"Respuesta no JSON de Socrata [{resource_id}]") from exc

        if isinstance(data, dict) and data.get("error"):
            error_msg = data.get("message", "Error desconocido devuelto por Socrata")
            logger.error("Error en recurso Socrata %s: %s", resource_id, error_msg)
            raise RuntimeError(f"Error Socrata [{resource_id}]: {error_msg}")

        return data if isinstance(data, list) else []

    def fetch_dataframe(
        self,
        resource_id: str,
        max_records: int = DEFAULT_BATCH_LIMIT,
        batch_size: int = 2000,
        where_clause: Optional[str] = None,
        select_clause: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Descarga registros paginados hasta alcanzar max_records y retorna un DataFrame.
        """
        all_rows: List[Dict[str, Any]] = []
        offset = 0

        while len(all_rows) < max_records:
            current_limit = min(batch_size, max_records - len(all_rows))
            batch = self.fetch_records(
                resource_id=resource_id,
                limit=current_limit,
                offset=offset,
                where_clause=where_clause,
                select_clause=select_clause,
            )
            if not batch:
                break

            all_rows.extend(batch)
            offset += len(batch)

            if len(batch) < current_limit:
                # Ya no hay más registros en la fuente remota
                break

        if not all_rows:
            logger.warning("No se obtuvieron registros para recurso [%s]", resource_id)
            return pd.DataFrame()

        df = pd.DataFrame(all_rows)
        logger.info("Recuperados %d registros para recurso [%s]", len(df), resource_id)
        return df
