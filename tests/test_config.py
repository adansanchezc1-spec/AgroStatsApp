"""Pruebas Unitarias para Configuración, Logging y Timing (Sprint 0).
Fase PDCO: CONTROL
Casos de prueba: TC-001, TC-002, TC-003, TC-004
"""

from __future__ import annotations
import logging
from pathlib import Path
import pytest
from src.config.settings import AppSettings, settings
from src.utils.logger import get_logger, setup_logging
from src.utils.timing import timeit


def test_tc001_settings_loading_and_defaults() -> None:
    """TC-001: Verifica que las variables de configuración carguen con tipos y valores por defecto."""
    custom_settings = AppSettings(ENV="testing", LOG_LEVEL="DEBUG")
    assert custom_settings.ENV == "testing"
    assert custom_settings.LOG_LEVEL == "DEBUG"
    assert isinstance(custom_settings.BASE_DIR, Path)
    assert custom_settings.ICA_RESOURCE_KEY == "a7581d79-b3bb-416f-a7c5-5034e5ca7a7"
    assert custom_settings.ICA_TENANT_ID == "b7aeda0c-64cd-49d2-9a4d-3062367432e3"
    assert "querydata" in custom_settings.ICA_ENDPOINT_URL


def test_tc002_catalog_integrity_of_11_socrata_datasets() -> None:
    """TC-002: Verifica que el catálogo de datasets Socrata contenga exactamente los 11 recursos oficiales."""
    expected_resources = {
        # 7 IDEAM
        "57sv-p2fu", "s54a-sgyg", "sbwg-7ju4", "ccvq-rp9s", "afdg-3zpb", "rv9s-8nv6", "nsz2-kzcq",
        # 2 SIPSA
        "gwbi-fnzs", "wgj6-cvyj",
        # 2 UPRA
        "gaic-b8aw", "2pnw-mmge",
    }
    actual_resources = {ds.resource_id for ds in settings.SOCRATA_DATASETS.values()}
    assert actual_resources == expected_resources, f"Diferencia en recursos SODA: {actual_resources ^ expected_resources}"
    assert len(settings.SOCRATA_DATASETS) == 11


def test_tc003_structured_logger_formatting_and_file_creation(tmp_path: Path) -> None:
    """TC-003: Verifica que setup_logging configure archivo y capture eventos sin fallos."""
    log_dir = tmp_path / "logs"
    setup_logging(log_dir=log_dir, log_level="DEBUG", force=True)
    logger = get_logger("test_module")
    
    test_msg = "Mensaje de auditoría de prueba unitaria"
    logger.info(test_msg)
    
    # Asegurar flush de handlers
    for h in logging.getLogger("agrostats").handlers:
        h.flush()
        
    log_file = log_dir / "agrostats.log"
    assert log_file.exists(), "El archivo de logs agrostats.log debe crearse en disco"
    content = log_file.read_text(encoding="utf-8")
    assert test_msg in content
    assert "INFO" in content
    assert "agrostats.test_module" in content


def test_tc004_timeit_decorator_execution() -> None:
    """TC-004: Verifica que el decorador @timeit ejecute la función y preserve retorno y excepciones."""
    @timeit
    def suma_rapida(a: int, b: int) -> int:
        return a + b

    resultado = suma_rapida(15, 27)
    assert resultado == 42

    @timeit
    def funcion_con_error() -> None:
        raise ValueError("Error forzado de prueba")

    with pytest.raises(ValueError, match="Error forzado de prueba"):
        funcion_con_error()
