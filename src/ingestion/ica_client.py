"""Conector REST para Azure Analysis Services / PowerBI Embedded (ICA).
Fase PDCO: DEVELOPMENT
Extracción de información del censo pecuario y movilización animal.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd

from src.config.settings import settings
from src.ingestion.base_client import BaseAPIClient
from src.utils.logger import get_logger

logger = get_logger("ingestion.ica_client")


class ICAClient(BaseAPIClient):
    """Conector hacia el backend público de PowerBI QueryData del ICA."""

    def __init__(
        self,
        resource_key: Optional[str] = None,
        tenant_id: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        timeout_seconds: int = 60,
    ) -> None:
        self.endpoint_url = endpoint_url or settings.ICA_ENDPOINT_URL
        super().__init__(base_url="", timeout_seconds=timeout_seconds)
        self.resource_key = resource_key or settings.ICA_RESOURCE_KEY
        self.tenant_id = tenant_id or settings.ICA_TENANT_ID

        # Headers obligatorios para Azure PowerBI Viewer
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-PowerBI-ResourceKey": self.resource_key,
        })
        logger.info("ICAClient configurado con ResourceKey: %s...", self.resource_key[:8])

    def build_query_payload(self, semantic_query_or_dax: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ensambla el payload compatible con el endpoint QueryData de PowerBI."""
        if semantic_query_or_dax is not None:
            return semantic_query_or_dax

        # Payload base por defecto para el modelo semántico del reporte pecuario ICA
        return {
            "version": "1.0.0",
            "queries": [
                {
                    "Query": {
                        "Commands": [
                            {
                                "SemanticQueryDataShapeCommand": {
                                    "Query": {
                                        "Version": 2,
                                        "From": [{"Name": "c", "Entity": "CensoPecuario", "Type": 0}],
                                        "Select": [
                                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "CodigoMunicipio"}, "Name": "cod_municipio"},
                                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Especie"}, "Name": "especie"},
                                            {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Anio"}, "Name": "anio"},
                                            {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "InventarioTotal"}, "Name": "total_animales"},
                                        ]
                                    },
                                    "Binding": {
                                        "Primary": {"Groupings": [{"Keys": [{"SourceRef": {"Source": "c"}}]}]},
                                        "Version": 1,
                                    }
                                }
                            }
                        ]
                    },
                    "QueryId": "",
                    "ApplicationContext": {"DatasetId": self.resource_key, "Sources": [{"ReportId": ""}]}
                }
            ],
            "cancelQueries": [],
            "modelId": self.tenant_id,
        }

    def execute_query(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Envía el payload a la API REST de Azure Analysis Services."""
        query_payload = self.build_query_payload(payload)
        logger.debug("Enviando petición a QueryData ICA...")
        response = self.post(self.endpoint_url, json_payload=query_payload)
        return response.json()

    def parse_response_to_dataframe(self, response_json: Dict[str, Any]) -> pd.DataFrame:
        """Desempaqueta las estructuras semánticas tabulares retornadas por PowerBI."""
        records: List[Dict[str, Any]] = []
        try:
            results = response_json.get("results", [])
            for res in results:
                data_shapes = res.get("result", {}).get("data", {}).get("dsr", {}).get("DS", [])
                for ds in data_shapes:
                    rows = ds.get("PH", [{}])[0].get("DM0", [])
                    for row in rows:
                        # Extraer valores de tupla retornada en formato semántico
                        values = row.get("C", [])
                        if values:
                            records.append({f"col_{i}": val for i, val in enumerate(values)})
        except Exception as exc:
            logger.warning("No se pudo parsear el resultado semántico estructurado: %s", exc)

        logger.info("Respuesta ICA desempaquetada con %d registros", len(records))
        return pd.DataFrame(records)

    def fetch_censo_dataframe(self) -> pd.DataFrame:
        """Flujo completo de extracción y conversión a DataFrame."""
        raw_response = self.execute_query()
        return self.parse_response_to_dataframe(raw_response)
