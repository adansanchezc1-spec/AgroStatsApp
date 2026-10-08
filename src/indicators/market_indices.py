"""Motor de Indicadores de Mercado Agropecuario e Insumos (Capa Gold).
Fase PDCO: DEVELOPMENT | Estándar: FAO / DAMA-DMBOK 2 / SWEBOK v4
Cálculo de inflación interanual (YoY), Términos de Intercambio (TOT) Insumo/Producto y Base 100.
"""

from __future__ import annotations
from typing import Optional
import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("indicators.market_indices")


def calculate_yoy_inflation(
    price_series: pd.Series,
    lag_periods: int = 12,
) -> pd.Series:
    """
    Calcula la variación porcentual interanual (Year-over-Year) de una serie de precios.

    Delta_YoY = ((P_t - P_{t-k}) / P_{t-k}) * 100

    Parámetros:
    -----------
    price_series : pd.Series
        Serie temporal ordenada de precios (ej. mensual con lag_periods=12).
    lag_periods : int
        Períodos de rezago temporal (12 para frecuencia mensual interanual).

    Retorna:
    --------
    pd.Series
        Tasa de inflación porcentual interanual.
    """
    if price_series.empty:
        return pd.Series(dtype="float64", index=price_series.index)

    p_clean = pd.to_numeric(price_series, errors="coerce")
    lagged = p_clean.shift(lag_periods)

    # Evitar división por cero
    denom = lagged.replace(0, np.nan)
    yoy_pct = ((p_clean - lagged) / denom) * 100.0

    return yoy_pct


def calculate_terms_of_trade(
    input_price_series: pd.Series,
    product_price_series: pd.Series,
) -> pd.Series:
    """
    Calcula la Relación de Intercambio o Términos de Intercambio (Terms of Trade - TOT):
    
    TOT = P_insumo / P_producto

    Indica cuántas unidades de producto agrícola se requieren para adquirir una unidad de insumo (fertilizante/alimento).
    Un valor creciente indica deterioro de los términos de intercambio para el productor.
    """
    if input_price_series.empty or product_price_series.empty:
        return pd.Series(dtype="float64", index=input_price_series.index)

    p_in = pd.to_numeric(input_price_series, errors="coerce")
    p_out = pd.to_numeric(product_price_series, errors="coerce").replace(0, np.nan)

    tot_ratio = p_in / p_out
    return tot_ratio


def calculate_price_index(
    price_series: pd.Series,
    base_idx: Optional[int] = 0,
) -> pd.Series:
    """
    Normaliza una serie de precios a número índice en Base 100 respecto a un período de referencia.
    """
    if price_series.empty:
        return pd.Series(dtype="float64", index=price_series.index)

    p_clean = pd.to_numeric(price_series, errors="coerce")
    valid_prices = p_clean.dropna()

    if valid_prices.empty or valid_prices.iloc[base_idx] == 0:
        return pd.Series(np.nan, index=price_series.index, dtype="float64")

    base_price = valid_prices.iloc[base_idx]
    return (p_clean / base_price) * 100.0
