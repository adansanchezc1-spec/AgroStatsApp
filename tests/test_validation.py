"""Pruebas Unitarias para Contratos de Validación y Quality Gates (Sprint 3).
Fase PDCO: CONTROL | Casos de Prueba: TC-301 a TC-308
"""

from __future__ import annotations
import pandas as pd
import pytest

from src.validation.contracts import (
    ValidationError,
    EVARecordContract,
    IDEAMClimaContract,
    SIPSAPrecioContract,
    ICAPecuarioContract,
)
from src.validation.quality_checker import QualityChecker


def test_tc301_eva_contract_rules() -> None:
    """TC-301: Verifica aceptación de registros válidos y rechazo ante inconsistencias en EVA."""
    valid_record = {
        "c_d_dep": "05",
        "c_d_mun": "05001",
        "a_o": "2023",
        "cultivo": "AGUACATE",
        "rea_sembrada_ha": "100.0",
        "rea_cosechada_ha": "95.0",
        "producci_n_t": "950.0",
        "rendimiento_t_ha": "10.0",
    }
    validated = EVARecordContract.validate(valid_record)
    assert validated["codigo_municipio"] == "05001"
    assert validated["cultivo"] == "AGUACATE"
    assert validated["anio"] == 2023

    # Violación: Cosecha excede siembra con amplio margen
    invalid_area = valid_record.copy()
    invalid_area["rea_cosechada_ha"] = "300.0"
    with pytest.raises(ValidationError, match="excede tolerancia"):
        EVARecordContract.validate(invalid_area)

    # Violación: Año fuera de rango
    invalid_year = valid_record.copy()
    invalid_year["a_o"] = "1980"
    with pytest.raises(ValidationError, match="fuera de rango"):
        EVARecordContract.validate(invalid_year)

    # Violación: Valores no numéricos y negativos
    invalid_types = valid_record.copy()
    invalid_types["rea_sembrada_ha"] = "-10.0"
    invalid_types["rea_cosechada_ha"] = "-5.0"
    invalid_types["producci_n_t"] = "-2.0"
    invalid_types["rendimiento_t_ha"] = "-1.0"
    invalid_types["cultivo"] = ""
    with pytest.raises(ValidationError):
        EVARecordContract.validate(invalid_types)


def test_tc302_ideam_contract_physical_limits() -> None:
    """TC-302: Verifica límites físicos de precipitación y temperatura en IDEAM."""
    valid_rain = {
        "codigoestacion": "21206990",
        "fechaobservacion": "2024-05-10 12:00:00",
        "valorobservado": "25.4",
        "descripcionsensor": "Precipitación Total Diaria",
    }
    val = IDEAMClimaContract.validate(valid_rain)
    assert val["valor"] == 25.4

    # Violación: Lluvia negativa
    negative_rain = valid_rain.copy()
    negative_rain["valorobservado"] = "-5.0"
    with pytest.raises(ValidationError, match="no puede ser negativa"):
        IDEAMClimaContract.validate(negative_rain)

    # Violación: Temperatura fuera de rango físico
    extreme_temp = {
        "codigoestacion": "21206990",
        "fechaobservacion": "2024-05-10 12:00:00",
        "valorobservado": "75.0",
        "descripcionsensor": "Temperatura del Aire",
    }
    with pytest.raises(ValidationError, match="fuera de límites físicos"):
        IDEAMClimaContract.validate(extreme_temp)

    # Violación: Radiación negativa
    invalid_rad = {
        "codigoestacion": "21206990",
        "fechaobservacion": "2024-05-10",
        "valorobservado": "-10.0",
        "descripcionsensor": "Radiación Solar",
    }
    with pytest.raises(ValidationError, match="radiacion solar"):
        IDEAMClimaContract.validate(invalid_rad)


def test_tc303_sipsa_and_ica_contracts() -> None:
    """TC-303: Verifica validación de precios SIPSA y censo pecuario ICA."""
    valid_sipsa = {
        "articulo": "UREA 46%",
        "anio": "2024",
        "mes": "6",
        "preciopromedio": "115000.0",
    }
    val_sipsa = SIPSAPrecioContract.validate(valid_sipsa)
    assert val_sipsa["precio"] == 115000.0

    # Violación: Precio <= 0
    invalid_price = valid_sipsa.copy()
    invalid_price["preciopromedio"] = "0.0"
    with pytest.raises(ValidationError, match="estrictamente mayor a 0"):
        SIPSAPrecioContract.validate(invalid_price)

    # Violación: Mes 15
    invalid_month = valid_sipsa.copy()
    invalid_month["mes"] = "15"
    with pytest.raises(ValidationError, match="rango"):
        SIPSAPrecioContract.validate(invalid_month)

    # ICA
    valid_ica = {"cod_municipio": "05001", "especie": "BOVINO", "total_animales": "450"}
    val_ica = ICAPecuarioContract.validate(valid_ica)
    assert val_ica["total_animales"] == 450

    invalid_ica = {"cod_municipio": "", "especie": "", "total_animales": "-5"}
    with pytest.raises(ValidationError):
        ICAPecuarioContract.validate(invalid_ica)


def test_tc304_quality_checker_batch_partitioning() -> None:
    """TC-304: Verifica particionamiento de DataFrame en conformes y no conformes con métricas."""
    df_raw = pd.DataFrame([
        {"c_d_dep": "05", "c_d_mun": "05001", "a_o": "2023", "cultivo": "CAFE", "rea_sembrada_ha": "10", "rea_cosechada_ha": "9", "producci_n_t": "15", "rendimiento_t_ha": "1.5"},
        {"c_d_dep": "05", "c_d_mun": "05002", "a_o": "2023", "cultivo": "CAFE", "rea_sembrada_ha": "10", "rea_cosechada_ha": "50", "producci_n_t": "15", "rendimiento_t_ha": "1.5"}, # Invalido (cosecha > siembra)
        {"c_d_dep": "08", "c_d_mun": "08001", "a_o": "2024", "cultivo": "PAPA", "rea_sembrada_ha": "20", "rea_cosechada_ha": "20", "producci_n_t": "200", "rendimiento_t_ha": "10.0"},
        {"c_d_dep": "08", "c_d_mun": "", "a_o": "2024", "cultivo": "PAPA", "rea_sembrada_ha": "20", "rea_cosechada_ha": "20", "producci_n_t": "200", "rendimiento_t_ha": "10.0"}, # Invalido (mun vacio)
    ])

    valid_df, invalid_df, metrics = QualityChecker.validate_dataset(df_raw, EVARecordContract)
    assert len(valid_df) == 2
    assert len(invalid_df) == 2
    assert metrics["compliance_rate_pct"] == 50.0
    assert "_validation_error" in invalid_df.columns


def test_tc305_composite_key_uniqueness_check() -> None:
    """TC-305: Verifica la detección de duplicados en llaves compuestas."""
    df = pd.DataFrame({
        "anio": [2024, 2024, 2024],
        "mes": [1, 1, 2],
        "municipio": ["05001", "05001", "05001"], # Fila 0 y 1 tienen misma clave (2024, 1, 05001)
        "valor": [10.0, 12.0, 15.0],
    })

    result = QualityChecker.check_composite_key_uniqueness(df, key_columns=["anio", "mes", "municipio"])
    assert result["is_unique"] is False
    assert result["duplicate_rows"] == 2
    assert result["unique_keys"] == 2

    with pytest.raises(KeyError):
        QualityChecker.check_composite_key_uniqueness(df, key_columns=["columna_inexistente"])


def test_tc306_markdown_report_generation() -> None:
    """TC-306: Verifica la generación estructurada del reporte Markdown de Quality Gate."""
    metrics = {
        "total_records": 100,
        "valid_records": 95,
        "invalid_records": 5,
        "compliance_rate_pct": 95.0,
        "error_summary": {"area_cosechada": 3, "codigo_municipio": 2},
    }
    report_md = QualityChecker.generate_markdown_report(metrics, dataset_name="UPRA_EVA_2024")
    assert "### Reporte de Quality Gate: UPRA_EVA_2024" in report_md
    assert "95.0%" in report_md
    assert "GREEN" in report_md
    assert "area_cosechada" in report_md


def test_tc307_empty_dataframe_quality_checks() -> None:
    """TC-307: Verifica manejo robusto ante DataFrames vacíos en QualityChecker."""
    empty_df = pd.DataFrame()
    v_df, inv_df, metrics = QualityChecker.validate_dataset(empty_df, EVARecordContract)
    assert v_df.empty
    assert inv_df.empty
    assert metrics["compliance_rate_pct"] == 100.0

    key_res = QualityChecker.check_composite_key_uniqueness(empty_df, key_columns=[])
    assert key_res["is_unique"] is True
