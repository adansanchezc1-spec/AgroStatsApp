"""Motor de Indicadores Agroclimáticos (Capa Gold).
Fase PDCO: DEVELOPMENT | Estándar: WMO (World Meteorological Organization) / SWEBOK v4
Cálculo riguroso del Índice de Precipitación Estandarizado (SPI) y Anomalías Térmicas Z-Score.
Soporte dual: Scipy acelerado y fallback analítico puro (Thom MLE / Abramowitz & Stegun / Wilson-Hilferty).
"""

from __future__ import annotations
import math
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("indicators.climate_indices")

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.info("Scipy no detectado; utilizando motor estadístico analítico puro para SPI")


def _inv_norm_cdf(p: float) -> float:
    """
    Aproximación racional de Abramowitz & Stegun (1964, fórmula 26.2.23) para la función cuantil normal estándar.
    Precisión absoluta < 4.5e-4, garantizando robustez sin dependencias binarias.
    """
    if p <= 0.0:
        return -3.5
    if p >= 1.0:
        return 3.5

    if p < 0.5:
        t = math.sqrt(-2.0 * math.log(p))
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        num = c0 + c1 * t + c2 * (t ** 2)
        den = 1.0 + d1 * t + d2 * (t ** 2) + d3 * (t ** 3)
        return -(t - num / den)
    else:
        q = 1.0 - p
        t = math.sqrt(-2.0 * math.log(q))
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        num = c0 + c1 * t + c2 * (t ** 2)
        den = 1.0 + d1 * t + d2 * (t ** 2) + d3 * (t ** 3)
        return t - num / den


def _gamma_cdf_approx(x: float, alpha: float, beta: float) -> float:
    """
    Aproximación de Wilson-Hilferty (1931) para la CDF Gamma compuesta con math.erf.
    """
    if x <= 0:
        return 0.0
    mean_val = alpha * beta
    if mean_val <= 0 or alpha <= 0:
        return 0.5
    cube_root = (x / mean_val) ** (1.0 / 3.0)
    mu_wh = 1.0 - 1.0 / (9.0 * alpha)
    sigma_wh = math.sqrt(1.0 / (9.0 * alpha))
    z = (cube_root - mu_wh) / sigma_wh
    cdf = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return max(0.0, min(1.0, cdf))


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

    # Ajuste de distribución Gamma a los datos positivos
    if len(positives) < 3:
        logger.warning("Menos de 3 valores positivos para ajuste Gamma en SPI-%d", scale)
        return pd.Series(np.nan, index=precip_series.index, dtype="float64")

    if HAS_SCIPY:
        try:
            alpha_param, _, beta_param = stats.gamma.fit(positives, floc=0)
        except Exception as exc:
            logger.error("Error al ajustar distribución Gamma con scipy: %s", exc)
            return pd.Series(np.nan, index=precip_series.index, dtype="float64")
    else:
        # Estimación por Máxima Verosimilitud de Thom (1958)
        mean_x = float(positives.mean())
        log_mean = math.log(max(mean_x, 1e-6))
        mean_log = float(np.log(positives.clip(lower=1e-6)).mean())
        diff_a = log_mean - mean_log
        if diff_a <= 0:
            alpha_param = 1.0
        else:
            alpha_param = (1.0 + math.sqrt(1.0 + (4.0 * diff_a) / 3.0)) / (4.0 * diff_a)
        beta_param = mean_x / alpha_param

    # Cálculo de la probabilidad acumulada compuesta H(x) = q + (1 - q) * G(x)
    spi_results = pd.Series(np.nan, index=precip_series.index, dtype="float64")

    for idx, val in rolling_precip.items():
        if pd.isna(val):
            continue
        if val <= 0.0:
            h_prob = prob_zero
        else:
            if HAS_SCIPY:
                g_prob = stats.gamma.cdf(val, a=alpha_param, scale=beta_param)
            else:
                g_prob = _gamma_cdf_approx(val, alpha=alpha_param, beta=beta_param)
            h_prob = prob_zero + (1.0 - prob_zero) * g_prob

        # Acotar probabilidades numéricamente para evitar inf / -inf
        h_prob = np.clip(h_prob, 1e-6, 1.0 - 1e-6)

        # Transformación a variable normal estándar Z ~ N(0, 1)
        if HAS_SCIPY:
            z_score = stats.norm.ppf(h_prob)
        else:
            z_score = _inv_norm_cdf(h_prob)

        # Acotar dentro del rango meteorológico típico [-3.5, 3.5]
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
