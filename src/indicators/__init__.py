"""Paquete de Motor de Indicadores Agroclimáticos y de Mercado (Capa Gold).
Fase PDCO: DEVELOPMENT | Estándar: Clean Code / SWEBOK v4 / DAMA-DMBOK 2
"""

from src.indicators.climate_indices import calculate_spi, calculate_thermal_anomaly
from src.indicators.market_indices import (
    calculate_yoy_inflation,
    calculate_terms_of_trade,
    calculate_price_index,
)
from src.indicators.temporal_features import add_lag_features, add_rolling_features
from src.indicators.indicator_store import IndicatorStore

__all__ = [
    "calculate_spi",
    "calculate_thermal_anomaly",
    "calculate_yoy_inflation",
    "calculate_terms_of_trade",
    "calculate_price_index",
    "add_lag_features",
    "add_rolling_features",
    "IndicatorStore",
]
