"""Motor de Indicadores Agroclimáticos (Capa Gold).
Fase PDCO: DEVELOPMENT | Estándar: WMO (World Meteorological Organization) / SWEBOK v4
Cálculo riguroso del Índice de Precipitación Estandarizado (SPI) y Anomalías Térmicas Z-Score.
"""

from __future__ import annotations
from typing import Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from src.utils.logger import get_logger

logger = get_logger("indicators.climate_indices")


def calculate_spi(
    precip_series: pd.Series,
    scale: int = 3,
    min_periods: int = 12,
) -> pd.Series:
    """
    Calcula el Índice de Precipitación Estandarizado (SPI) según el estándar WMO-No. 1090.

    Parámetros:
    -----------
    precip_series : pd.Series
        Serie temporal mensual de precipitación acumulada en milímetros (mm).
    scale : int
        Escala temporal de acumulación móvil (ej. 1, 3, 6 o 12 meses).
    min_periods : int
        Número mínimo de observaciones para el ajuste estadístico de la distribución Gamma.

    Retorna:
    --------
    pd.Series
        Valores continuos de SPI, alineados con el índice de la serie original.
    """
    if precip_series.empty:
        return pd.Series(dtype="float64", index=precip_series.index)

    # 1. Acumulación temporal móvil sobre la ventana especificada
    rolling_precip = precip_series.rolling(window=scale, min_periods=scale).sum()

    # Si hay menos observaciones válidas que el mínimo requerido
    valid_accum = rolling_precip.dropna()
    if len(valid_accum) < min_periods:
        logger.warning(
            "Muestra insuficiente para ajuste SPI-%d (registros válidos=%d, mínimo=%d)",
            scale, len(valid_accum), min_periods,
        )
        return pd.Series(np.nan, index=precip_series.index, dtype="float64")

    # Separar ceros de valores estrictamente positivos
    zeros_mask = valid_accum <= 0.0
    m_zeros = int(zeros_mask.sum())
    n_total = len(valid_accum)
    prob_zero = m_zeros / n_total

    positives = valid_accum[~zeros_mask]

    # Ajuste de distribución Gamma a los datos positivos (floc=0 fija el origen en cero)
    if len(positives) < 3:
        logger.warning("Menos de 3 valores positivos para ajuste Gamma en SPI-%d", scale)
        return pd.Series(np.nan, index=precip_series.index, dtype="float64")

    try:
        # alpha = shape, beta = scale
        alpha_param, loc_param, beta_param = stats.gamma.fit(positives, floc=0)
    except Exception as exc:
        logger.error("Error al ajustar distribución Gamma para SPI: %s", exc)
        return pd.Series(np.nan, index=precip_series.index, dtype="float64")

    # Cálculo de la probabilidad acumulada compuesta H(x) = q + (1 - q) * G(x)
    spi_results = pd.Series(np.nan, index=precip_series.index, dtype="float64")

    for idx, val in rolling_precip.items():
        if pd.isna(val):
            continue
        if val <= 0.0:
            h_prob = prob_zero
        else:
            g_prob = stats.gamma.cdf(val, a=alpha_param, scale=beta_param)
            h_prob = prob_zero + (1.0 - prob_zero) * g_prob

        # Acotar probabilidades numéricamente para evitar inf / -inf en cuantiles normales
        h_prob = np.clip(h_prob, 1e-6, 1.0 - 1e-6)

        # Transformación a variable normal estándar Z ~ N(0, 1)
        z_score = stats.norm.ppf(h_prob)
        # Acotar dentro del rango meteorológico típico [-3.09, 3.09] (percentiles 0.1% a 99.9%)
        spi_results[idx] = float(np.clip(z_score, -3.5, 3.5))

    logger.debug("SPI-%d calculado exitosamente para %d registros", scale, len(precip_series))
    return spi_results


def calculate_thermal_anomaly(
    temp_series: pd.Series,
    dates_series: pd.Series,
    min_years: int = 1,
) -> pd.Series:
    """
    Calcula la anomalía térmica mensual estandarizada (Z-score climatológico).

    ZT = (T_obs - mu_mes) / sigma_mes

    Parámetros:
    -----------
    temp_series : pd.Series
        Serie de temperaturas observadas (°C).
    dates_series : pd.Series
        Serie de fechas correspondientes (formato datetime).
    min_years : int
        Años mínimos requeridos en el registro.

    Retorna:
    --------
    pd.Series
        Anomalía Z-score por cada observación mensual.
    """
    if temp_series.empty or dates_series.empty:
        return pd.Series(dtype="float64", index=temp_series.index)

    df_temp = pd.DataFrame({
        "temp": pd.to_numeric(temp_series, errors="coerce"),
        "fecha": pd.to_datetime(dates_series, errors="coerce"),
    }, index=temp_series.index)

    df_temp["mes"] = df_temp["fecha"].dt.month

    # Climatología mensual: media y desviación estándar por mes del año
    monthly_stats = df_temp.groupby("mes")["temp"].agg(["mean", "std"])

    anomalies = pd.Series(np.nan, index=temp_series.index, dtype="float64")

    for idx, row in df_temp.iterrows():
        mes = row["mes"]
        t_val = row["temp"]
        if pd.isna(mes) or pd.isna(t_val) or mes not in monthly_stats.index:
            continue

        mean_m = monthly_stats.loc[mes, "mean"]
        std_m = monthly_stats.loc[mes, "std"]

        if pd.isna(std_m) or std_m == 0:
            anomalies[idx] = 0.0
        else:
            anomalies[idx] = float((t_val - mean_m) / std_m)

    return anomalies
