"""Pruebas Unitarias para Ingestión Multifuente y Landing Inmutable (Sprint 1).
Fase PDCO: CONTROL | Casos de Prueba: TC-101 a TC-106
"""

from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
import requests

from src.ingestion.base_client import BaseAPIClient
from src.ingestion.socrata_client import SocrataClient
from src.ingestion.ica_client import ICAClient
from src.ingestion.landing_manager import LandingManager


class DummyAPIClient(BaseAPIClient):
    """Implementación concreta mínima para testear BaseAPIClient."""
    pass


def test_tc101_base_client_retry_on_transient_error() -> None:
    """TC-101: Verifica que BaseAPIClient reintente automáticamente ante errores 429 y 503."""
    client = DummyAPIClient(base_url="https://mock.api.test", max_retries=3, backoff_factor=0.01)

    mock_resp_fail = MagicMock(spec=requests.Response)
    mock_resp_fail.status_code = 429
    mock_resp_fail.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_resp_fail)

    mock_resp_success = MagicMock(spec=requests.Response)
    mock_resp_success.status_code = 200
    mock_resp_success.json.return_value = {"status": "ok"}
    mock_resp_success.raise_for_status.return_value = None

    with patch.object(client.session, "request", side_effect=[mock_resp_fail, mock_resp_success]) as mock_request:
        response = client.get("/test-endpoint")
        assert response.status_code == 200
        assert mock_request.call_count == 2
    client.close()


def test_tc102_socrata_client_pagination() -> None:
    """TC-102: Verifica que SocrataClient pagine con $offset hasta agotar el dataset."""
    client = SocrataClient(base_url="https://mock.datos.gov.co", app_token="test_token")

    page_1 = [{"id": 1, "municipio": "BOGOTA"}, {"id": 2, "municipio": "MEDELLIN"}]
    page_2 = [{"id": 3, "municipio": "CALI"}]
    page_3: list[dict] = []

    with patch.object(client, "fetch_page", side_effect=[page_1, page_2, page_3]) as mock_fetch:
        df = client.fetch_dataframe(resource_id="57sv-p2fu", batch_size=2)
        assert len(df) == 3
        assert list(df["municipio"]) == ["BOGOTA", "MEDELLIN", "CALI"]
        assert mock_fetch.call_count == 2
    client.close()


def test_tc103_ica_client_payload_assembly_and_parsing() -> None:
    """TC-103: Verifica el ensamblado del payload y el desempaquetado tabular de PowerBI."""
    client = ICAClient(resource_key="mock_key_123", tenant_id="mock_tenant_456")
    assert client.session.headers["X-PowerBI-ResourceKey"] == "mock_key_123"

    payload = client.build_query_payload()
    assert payload["version"] == "1.0.0"
    assert payload["modelId"] == "mock_tenant_456"

    mock_response_json = {
        "results": [
            {
                "result": {
                    "data": {
                        "dsr": {
                            "DS": [
                                {
                                    "PH": [
                                        {
                                            "DM0": [
                                                {"C": ["05001", "BOVINO", 2024, 15000]},
                                                {"C": ["05002", "PORCINO", 2024, 8200]},
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        ]
    }
    df = client.parse_response_to_dataframe(mock_response_json)
    assert len(df) == 2
    assert df.iloc[0]["col_0"] == "05001"
    assert df.iloc[0]["col_1"] == "BOVINO"
    assert df.iloc[1]["col_3"] == 8200
    client.close()


def test_tc104_landing_manager_sha256_and_immutability(tmp_path: Path) -> None:
    """TC-104: Verifica el guardado en Parquet, cálculo de SHA-256 y la inmutabilidad de Bronze."""
    manager = LandingManager(raw_base_dir=tmp_path / "RAW")
    sample_df = pd.DataFrame({
        "codigo_municipio": ["05001", "08001"],
        "precio": [12500.0, 14200.0],
    })

    # Primer guardado
    meta_1 = manager.save_raw_dataset(sample_df, source_category="ideam", filename="clima_test.parquet")
    assert Path(meta_1["file_path"]).exists()
    assert meta_1["rows"] == 2
    sha_1 = meta_1["sha256"]
    assert len(sha_1) == 64

    # Verificación de integridad en manifiesto
    integrity = manager.verify_integrity()
    assert integrity.get("ideam/clima_test.parquet") is True

    # Segundo guardado sin overwrite (debe preservar y no sobrescribir)
    meta_2 = manager.save_raw_dataset(sample_df, source_category="ideam", filename="clima_test.parquet", overwrite=False)
    assert meta_2["sha256"] == sha_1

    # Verificar que el manifiesto contenga la entrada registrada
    manifest = manager.load_manifest()
    assert "ideam/clima_test.parquet" in manifest["datasets"]


def test_tc105_socrata_healthcheck_and_post() -> None:
    """TC-105: Evalúa métodos check_health y POST en conectores."""
    client = SocrataClient(base_url="https://mock.datos.gov.co", app_token="test_token")
    
    mock_resp_200 = MagicMock(spec=requests.Response)
    mock_resp_200.status_code = 200
    mock_resp_200.raise_for_status.return_value = None

    with patch.object(client, "get", return_value=mock_resp_200):
        assert client.check_health("57sv-p2fu") is True

    with patch.object(client, "get", side_effect=requests.RequestException("Timeout")):
        assert client.check_health("57sv-p2fu") is False

    with patch.object(client.session, "request", return_value=mock_resp_200):
        resp_post = client.post("test", json_payload={"k": "v"})
        assert resp_post.status_code == 200
    client.close()


def test_tc106_landing_manager_empty_and_tampered_integrity(tmp_path: Path) -> None:
    """TC-106: Evalúa integridad ante manipulación física de archivos."""
    manager = LandingManager(raw_base_dir=tmp_path / "RAW")
    df = pd.DataFrame({"a": [1, 2, 3]})
    meta = manager.save_raw_dataset(df, source_category="upra", filename="test_eva.parquet")

    # Manipular el archivo para provocar fallo de integridad
    target_file = Path(meta["file_path"])
    target_file.write_bytes(b"DATOS_CORRUPTOS")

    integrity = manager.verify_integrity()
    assert integrity["upra/test_eva.parquet"] is False
