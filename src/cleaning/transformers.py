"""Transformadores Puros de Datos y Sanitización (Capa Silver).
Fase PDCO: DEVELOPMENT | Estándar: Clean Code / SWEBOK v4 / DAMA-DMBOK 2
Funciones puras de normalización tipográfica, tipado seguro y resolución de duplicados.
"""

from __future__ import annotations
import re
import unicodedata
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("cleaning.transformers")


def sanitize_text(text: Any) -> str:
    """
    Normaliza texto eliminando tildes (NFKD), colapsando espacios y convirtiendo a mayúsculas.
    Garantiza pureza e idempotencia: sanitize_text(sanitize_text(x)) == sanitize_text(x).
    """
    if text is None or pd.isna(text):
        return ""

    raw_str = str(text).strip()
    if not raw_str:
        return ""

    # Normalización Unicode NFKD para separar caracteres base de sus diacríticos
    normalized = unicodedata.normalize("NFKD", raw_str)
    # Filtrar marcas de combinación diacrítica (Mn)
    ascii_str = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    # Colapsar múltiples espacios internos a uno solo
    collapsed = re.sub(r"\s+", " ", ascii_str)
    return collapsed.strip().upper()


def cast_datatypes(
    df: pd.DataFrame,
    type_schema: Dict[str, str],
) -> pd.DataFrame:
    """
    Castea columnas de un DataFrame de forma segura según el diccionario type_schema.
    Soporta tipos: 'int64', 'float64', 'category', 'string', 'datetime64[ns]'.
    """
    if df.empty:
        return df.copy()

    df_out = df.copy()

    for col, target_type in type_schema.items():
        if col not in df_out.columns:
            continue

        target_type_clean = target_type.lower().strip()
        try:
            if target_type_clean in {"float", "float64"}:
                df_out[col] = pd.to_numeric(df_out[col], errors="coerce").astype("float64")
            elif target_type_clean in {"int", "int64"}:
                # Coerción numérica con reemplazo seguro de nulos antes de entero
                num_series = pd.to_numeric(df_out[col], errors="coerce").fillna(0)
                df_out[col] = num_series.astype("int64")
            elif target_type_clean in {"category"}:
                df_out[col] = df_out[col].astype("category")
            elif target_type_clean in {"string", "str"}:
                df_out[col] = df_out[col].astype("string")
            elif "datetime" in target_type_clean:
                df_out[col] = pd.to_datetime(df_out[col], errors="coerce")
            else:
                df_out[col] = df_out[col].astype(target_type)
        except Exception as exc:
            logger.warning("Fallo al castear columna '%s' a tipo '%s': %s", col, target_type, exc)

    return df_out


def handle_missing_values(
    df: pd.DataFrame,
    categorical_cols: Optional[List[str]] = None,
    default_fill: str = "SIN_VARIEDAD_ESPECIFICADA",
    numeric_fill: Optional[float] = None,
) -> pd.DataFrame:
    """
    Imputa de forma controlada valores nulos en variables categóricas o numéricas.
    """
    if df.empty:
        return df.copy()

    df_out = df.copy()

    # Tratamiento categórico
    target_cats = categorical_cols or [c for c in df_out.columns if df_out[c].dtype == "object" or df_out[c].dtype.name == "category"]
    for col in target_cats:
        if col in df_out.columns:
            # Reemplazar cadenas vacías o espacios con el valor por defecto
            series = df_out[col].fillna(default_fill).astype(str)
            series = series.replace(r"^\s*$", default_fill, regex=True)
            series = series.replace("NAN", default_fill).replace("NONE", default_fill)
            df_out[col] = series

    # Tratamiento numérico opcional
    if numeric_fill is not None:
        num_cols = df_out.select_dtypes(include=[np.number]).columns
        df_out[num_cols] = df_out[num_cols].fillna(numeric_fill)

    return df_out


def deduplicate_dataset(
    df: pd.DataFrame,
    subset_keys: List[str],
    sort_by: Optional[str] = None,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Deduplica un DataFrame sobre un subconjunto de claves, conservando el registro
    más reciente si se provee columna de ordenamiento temporal.
    """
    if df.empty:
        return df.copy()

    df_out = df.copy()
    valid_keys = [k for k in subset_keys if k in df_out.columns]

    if not valid_keys:
        logger.warning("deduplicate_dataset invocado sin claves válidas presentes en el DataFrame")
        return df_out.drop_duplicates()

    if sort_by and sort_by in df_out.columns:
        df_out = df_out.sort_values(by=sort_by, ascending=ascending)

    before_count = len(df_out)
    df_out = df_out.drop_duplicates(subset=valid_keys, keep="first").reset_index(drop=True)
    after_count = len(df_out)
    diff = before_count - after_count

    if diff > 0:
        logger.info("Deduplicación eliminó %d registros duplicados sobre claves %s", diff, valid_keys)

    return df_out
