"""Pruebas Unitarias para Análisis Exploratorio y Perfilado (Sprint 2).
Fase PDCO: CONTROL | Casos de Prueba: TC-201, TC-202, TC-203, TC-204, TC-205
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import pytest

from src.eda.profiler import profile_dataframe, temporal_coverage, cardinality_matrix


def test_tc201_profile_dataframe_metrics() -> None:
    """TC-201: Verifica el cálculo de missingness, cardinalidad y estadísticas numéricas."""
    df = pd.DataFrame({
        "departamento": ["ANTIOQUIA", "CUNDINAMARCA", "ANTIOQUIA", None],
        "precio": [100.0, 200.0, 300.0, 400.0],
        "rendimiento": [1.5, 2.0, np.nan, 3.5],
    })

    profile = profile_dataframe(df)
    assert profile["total_rows"] == 4
    assert profile["total_columns"] == 3
    assert profile["memory_bytes"] > 0

    dept_stats = profile["columns"]["departamento"]
    assert dept_stats["null_count"] == 1
    assert dept_stats["null_percentage"] == 25.0
    assert dept_stats["unique_count"] == 2

    precio_stats = profile["columns"]["precio"]["numeric_stats"]
    assert precio_stats["mean"] == 250.0
    assert precio_stats["min"] == 100.0
    assert precio_stats["max"] == 400.0
    assert precio_stats["median"] == 250.0
    assert "p01" in precio_stats
    assert "p99" in precio_stats


def test_tc202_temporal_coverage_gap_detection() -> None:
    """TC-202: Verifica que temporal_coverage identifique correctamente lagunas en la serie temporal."""
    # Serie con meses Enero, Febrero, Mayo y Junio de 2024 (falta Marzo y Abril)
    dates = ["2024-01-15", "2024-02-15", "2024-05-15", "2024-06-15"]
    df = pd.DataFrame({
        "fecha": dates,
        "estacion": ["EST_1", "EST_1", "EST_1", "EST_1"],
    })

    cov = temporal_coverage(df, date_column="fecha", group_column="estacion", freq="MS")
    assert cov["has_gaps"] is True
    assert cov["missing_periods_count"] == 2
    # Comprobar que los periodos faltantes sean Marzo y Abril
    assert any("2024-03" in p for p in cov["missing_periods"])
    assert any("2024-04" in p for p in cov["missing_periods"])


def test_tc203_cardinality_matrix_distribution() -> None:
    """TC-203: Verifica la construcción de la matriz de cardinalidad y categoría dominante."""
    df = pd.DataFrame({
        "cultivo": ["PAPA", "PAPA", "PAPA", "MAIZ", "ARROZ"],
        "variedad": ["PASTUSA", "PASTUSA", "DIAMANTE", "BLANCO", "FEDEARROZ"],
    })

    matrix = cardinality_matrix(df, categorical_cols=["cultivo", "variedad"])
    assert len(matrix) == 2
    
    papa_row = matrix[matrix["columna"] == "cultivo"].iloc[0]
    assert papa_row["cardinalidad_unica"] == 3
    assert papa_row["categoria_dominante"] == "PAPA"
    assert papa_row["frecuencia_dominante"] == 3
    assert papa_row["porcentaje_dominante"] == 60.0


def test_tc204_outliers_iqr_detection() -> None:
    """TC-204: Verifica la detección de outliers univariados por rango intercuartílico."""
    # Distribución homogénea con un outlier extremo
    vals = [10.0, 11.0, 12.0, 10.5, 11.2, 10.8, 11.5, 1000.0]
    df = pd.DataFrame({"medicion": vals})

    profile = profile_dataframe(df)
    stats = profile["columns"]["medicion"]["numeric_stats"]
    assert stats["outliers_iqr_count"] == 1
    assert stats["max"] == 1000.0


def test_tc205_empty_dataframe_handling() -> None:
    """TC-205: Verifica que las funciones manejen DataFrames vacíos de forma controlada sin excepciones."""
    empty_df = pd.DataFrame()
    profile = profile_dataframe(empty_df)
    assert profile["total_rows"] == 0
    assert profile["columns"] == {}

    cov = temporal_coverage(empty_df, date_column="fecha")
    assert cov["has_gaps"] is False
    assert cov["earliest_date"] is None

    mat = cardinality_matrix(empty_df, categorical_cols=["col_a"])
    assert mat.empty
