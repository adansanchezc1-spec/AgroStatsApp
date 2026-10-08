"""Generación de Características Temporales sin Sesgo Prospectivo (Lookahead Bias).
Fase PDCO: DEVELOPMENT | Estándar: Clean Code / SWEBOK v4 / Time-Series Engineering
Construcción de rezagos (lags) y medias móviles rezagadas (rolling) por series agrupadas.
"""

from __future__ import annotations
from typing import List, Optional
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("indicators.temporal_features")


def add_lag_features(
    df: pd.DataFrame,
    target_col: str,
    lags: Optional[List[int]] = None,
    group_col: Optional[str] = None,
    order_by: Optional[str] = None,
) -> pd.DataFrame:
    """
    Agrega columnas de rezago temporal (lags) garantizando causalidad estricta (t - k).

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame de entrada.
    target_col : str
        Nombre de la variable numérica sobre la cual calcular los rezagos.
    lags : List[int]
        Lista de períodos de rezago (por defecto [1, 3, 6, 12]).
    group_col : Optional[str]
        Columna para agrupar series temporales independientes (ej. 'cod_municipio').
    order_by : Optional[str]
        Columna temporal para asegurar orden cronológico antes del shift.

    Retorna:
    --------
    pd.DataFrame
        DataFrame con las nuevas columnas target_col_lag_k incorporadas.
    """
    if df.empty or target_col not in df.columns:
        return df.copy()

    lags = lags or [1, 3, 6, 12]
    df_out = df.copy()

    if order_by and order_by in df_out.columns:
        df_out = df_out.sort_values(by=order_by).reset_index(drop=True)

    for k in lags:
        lag_col_name = f"{target_col}_lag_{k}"
        if group_col and group_col in df_out.columns:
            df_out[lag_col_name] = df_out.groupby(group_col)[target_col].shift(k)
        else:
            df_out[lag_col_name] = df_out[target_col].shift(k)

    return df_out


def add_rolling_features(
    df: pd.DataFrame,
    target_col: str,
    windows: Optional[List[int]] = None,
    group_col: Optional[str] = None,
    order_by: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calcula medias y desviaciones estándar móviles estrictamente históricas.
    Aplica shift(1) previo a la ventana móvil para erradicar el sesgo de anticipación
    (lookahead bias), de modo que el valor en t no se incluya en su propia media.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame de entrada.
    target_col : str
        Variable numérica objetivo.
    windows : List[int]
        Ventanas móviles temporales (por defecto [3, 6]).
    group_col : Optional[str]
        Columna de agrupación (ej. 'cod_municipio').
    order_by : Optional[str]
        Columna temporal para orden cronológico.

    Retorna:
    --------
    pd.DataFrame
        DataFrame con target_col_roll_mean_w y target_col_roll_std_w.
    """
    if df.empty or target_col not in df.columns:
        return df.copy()

    windows = windows or [3, 6]
    df_out = df.copy()

    if order_by and order_by in df_out.columns:
        df_out = df_out.sort_values(by=order_by).reset_index(drop=True)

    for w in windows:
        mean_col_name = f"{target_col}_roll_mean_{w}"
        std_col_name = f"{target_col}_roll_std_{w}"

        if group_col and group_col in df_out.columns:
            # Desplazar 1 período hacia el pasado para excluir t de la ventana móvil
            shifted = df_out.groupby(group_col)[target_col].shift(1)
            df_out[mean_col_name] = (
                shifted.groupby(df_out[group_col])
                .rolling(window=w, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
            )
            df_out[std_col_name] = (
                shifted.groupby(df_out[group_col])
                .rolling(window=w, min_periods=2)
                .std()
                .reset_index(level=0, drop=True)
            )
        else:
            shifted = df_out[target_col].shift(1)
            df_out[mean_col_name] = shifted.rolling(window=w, min_periods=1).mean()
            df_out[std_col_name] = shifted.rolling(window=w, min_periods=2).std()

    return df_out
