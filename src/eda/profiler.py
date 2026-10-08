"""Motor de Análisis Exploratorio de Datos (EDA) y Perfilado Automatizado.
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 / SWEBOK v4
Funciones puras de diagnóstico estadístico, missingness y detección de brechas temporales.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("eda.profiler")


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un perfil estadístico exhaustivo de un DataFrame.
    Incluye tasas de missingness, cardinalidad, tipos de datos y métricas univariadas.
    """
    if df.empty:
        logger.warning("profile_dataframe invocado con un DataFrame vacío")
        return {
            "total_rows": 0,
            "total_columns": 0,
            "memory_bytes": 0,
            "columns": {},
        }

    total_rows = len(df)
    memory_bytes = int(df.memory_usage(deep=True).sum())
    col_profiles: Dict[str, Dict[str, Any]] = {}

    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        null_pct = float(null_count / total_rows) * 100.0
        unique_count = int(series.nunique(dropna=True))
        cardinality_ratio = float(unique_count / total_rows) if total_rows > 0 else 0.0

        col_info: Dict[str, Any] = {
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_percentage": round(null_pct, 2),
            "unique_count": unique_count,
            "cardinality_ratio": round(cardinality_ratio, 4),
        }

        # Estadísticas para columnas numéricas
        if pd.api.types.is_numeric_dtype(series):
            valid_series = series.dropna()
            if not valid_series.empty:
                q1 = float(np.percentile(valid_series, 25))
                q3 = float(np.percentile(valid_series, 75))
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers_iqr = int(((valid_series < lower_bound) | (valid_series > upper_bound)).sum())

                col_info["numeric_stats"] = {
                    "mean": round(float(valid_series.mean()), 4),
                    "std": round(float(valid_series.std()), 4) if len(valid_series) > 1 else 0.0,
                    "median": round(float(valid_series.median()), 4),
                    "min": round(float(valid_series.min()), 4),
                    "max": round(float(valid_series.max()), 4),
                    "p01": round(float(np.percentile(valid_series, 1)), 4),
                    "p05": round(float(np.percentile(valid_series, 5)), 4),
                    "p25": round(q1, 4),
                    "p75": round(q3, 4),
                    "p95": round(float(np.percentile(valid_series, 95)), 4),
                    "p99": round(float(np.percentile(valid_series, 99)), 4),
                    "iqr": round(iqr, 4),
                    "outliers_iqr_count": outliers_iqr,
                }
        col_profiles[str(col)] = col_info

    logger.info("Perfilado completado: %d filas, %d columnas, %.2f KB", total_rows, len(df.columns), memory_bytes / 1024.0)
    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "memory_bytes": memory_bytes,
        "columns": col_profiles,
    }


def temporal_coverage(
    df: pd.DataFrame,
    date_column: str,
    group_column: Optional[str] = None,
    freq: str = "MS",
) -> Dict[str, Any]:
    """
    Identifica el rango temporal efectivo y detecta brechas/lagunas temporales.
    """
    if df.empty or date_column not in df.columns:
        logger.warning("temporal_coverage: DataFrame vacío o columna '%s' inexistente", date_column)
        return {"has_gaps": False, "earliest_date": None, "latest_date": None, "missing_periods": []}

    temp_series = pd.to_datetime(df[date_column], errors="coerce").dropna()
    if temp_series.empty:
        return {"has_gaps": False, "earliest_date": None, "latest_date": None, "missing_periods": []}

    min_date = temp_series.min()
    max_date = temp_series.max()

    expected_range = pd.date_range(start=min_date, end=max_date, freq=freq)
    
    # Compatibilidad con pandas PeriodIndex (usa 'M' en lugar de 'MS')
    period_freq = freq.rstrip("S") if freq.endswith("S") else freq
    actual_periods = pd.PeriodIndex(temp_series, freq=period_freq).unique()
    expected_periods = pd.PeriodIndex(expected_range, freq=period_freq).unique()

    missing_periods = [str(p) for p in expected_periods if p not in actual_periods]
    has_gaps = len(missing_periods) > 0

    result: Dict[str, Any] = {
        "earliest_date": str(min_date),
        "latest_date": str(max_date),
        "expected_periods_count": len(expected_periods),
        "actual_periods_count": len(actual_periods),
        "missing_periods_count": len(missing_periods),
        "has_gaps": has_gaps,
        "missing_periods": missing_periods[:50],
    }

    # Si se agrupa por municipio o estación
    if group_column and group_column in df.columns:
        gaps_by_group: Dict[str, int] = {}
        for group_val, group_df in df.groupby(group_column):
            g_dates = pd.to_datetime(group_df[date_column], errors="coerce").dropna()
            g_periods = pd.PeriodIndex(g_dates, freq=period_freq).unique()
            g_missing = len([p for p in expected_periods if p not in g_periods])
            if g_missing > 0:
                gaps_by_group[str(group_val)] = g_missing
        result["gaps_by_group"] = gaps_by_group

    logger.info("Cobertura temporal: de %s a %s. Gaps detectados: %s", min_date, max_date, has_gaps)
    return result


def cardinality_matrix(
    df: pd.DataFrame,
    categorical_cols: List[str],
) -> pd.DataFrame:
    """
    Construye una matriz de cardinalidad y distribución para columnas categóricas.
    """
    records: List[Dict[str, Any]] = []
    total_rows = len(df)

    for col in categorical_cols:
        if col in df.columns:
            series = df[col].astype(str)
            vc = series.value_counts(dropna=False)
            top_category = vc.index[0] if not vc.empty else "N/A"
            top_freq = int(vc.iloc[0]) if not vc.empty else 0
            records.append({
                "columna": col,
                "cardinalidad_unica": int(series.nunique()),
                "categoria_dominante": top_category,
                "frecuencia_dominante": top_freq,
                "porcentaje_dominante": round((top_freq / total_rows) * 100.0, 2) if total_rows > 0 else 0.0,
            })

    return pd.DataFrame(records)
