"""
Módulo de Detección Rigurosa y Tratamiento de Anomalías Agropecuarias
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: SWEBOK (Data Quality), ISO/IEC 25010, Clean Code, PEP 8
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class AnomalyTreatmentEngine:
    """
    Motor estadístico para la detección, clasificación y tratamiento de anomalías.
    Distingue rigurosamente entre:
      - 'ERROR_DE_DATO': Valores físicamente imposibles (precios < 0, pesos < 0) -> Imputación / Winsorización.
      - 'SHOCK_AGROCLIMATICO': Eventos reales de mercado (sequía, helada, paro) -> Preservación y etiquetado.
    """

    @staticmethod
    def detect_tukey_fences(series: pd.Series, k: float = 1.5) -> pd.Series:
        """Detección no paramétrica mediante Vallas de Tukey."""
        s = series.dropna()
        if len(s) < 4:
            return pd.Series(False, index=series.index)
        q25, q75 = s.quantile(0.25), s.quantile(0.75)
        iqr = q75 - q25
        lower = q25 - k * iqr
        upper = q75 + k * iqr
        return (series < lower) | (series > upper)

    @staticmethod
    def detect_hampel_filter(series: pd.Series, n_sigmas: float = 3.0) -> pd.Series:
        """Filtro robusto de Hampel basado en la Desviación Absoluta respecto a la Mediana (MAD)."""
        s = series.dropna()
        if len(s) < 4:
            return pd.Series(False, index=series.index)
        median = s.median()
        mad = np.median(np.abs(s - median))
        if mad == 0:
            return pd.Series(False, index=series.index)
        # Factor 1.4826 para consistencia asintótica con la distribución Normal
        threshold = n_sigmas * 1.4826 * mad
        return np.abs(series - median) > threshold

    @classmethod
    def treat_price_anomalies(
        cls,
        df: pd.DataFrame,
        price_col: str,
        commodity_col: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Aplica tratamiento sistemático sobre series de precios:
        1. Corrige precios <= 0 (errores físicos).
        2. Detecta shocks extremos por producto mediante Hampel / Tukey.
        3. Etiqueta shocks agroclimáticos sin destruir la señal real del mercado.
        """
        df_treated = df.copy()
        if price_col not in df_treated.columns or not pd.api.types.is_numeric_dtype(df_treated[price_col]):
            return df_treated, {"treated": False, "reason": "Columna no numérica"}

        # 1. Errores físicos imposibles
        neg_mask = df_treated[price_col] <= 0
        neg_count = int(neg_mask.sum())
        if neg_count > 0:
            median_val = df_treated.loc[~neg_mask, price_col].median()
            df_treated.loc[neg_mask, price_col] = median_val
            logger.info(f"[AnomalyTreatment] Corregidos {neg_count} precios <= 0 con mediana: {median_val}")

        # 2. Detección de atípicos por grupo de producto o global
        if commodity_col and commodity_col in df_treated.columns:
            is_shock = df_treated.groupby(commodity_col)[price_col].transform(
                lambda s: cls.detect_hampel_filter(s, n_sigmas=3.5)
            )
        else:
            is_shock = cls.detect_hampel_filter(df_treated[price_col], n_sigmas=3.5)

        df_treated["es_shock_agroclimatico"] = is_shock.fillna(False)
        shock_count = int(df_treated["es_shock_agroclimatico"].sum())

        summary = {
            "total_records": len(df_treated),
            "physical_errors_fixed": neg_count,
            "agroclimatic_shocks_flagged": shock_count,
            "shock_percentage": round((shock_count / len(df_treated)) * 100, 2)
        }
        logger.info(
            f"[AnomalyTreatment] Precios evaluados: {neg_count} errores corregidos, "
            f"{shock_count} shocks agroclimáticos etiquetados."
        )
        return df_treated, summary

    @classmethod
    def treat_quantity_anomalies(
        cls,
        df: pd.DataFrame,
        qty_col: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Aplica tratamiento sobre volúmenes de carga y abastecimiento."""
        df_treated = df.copy()
        if qty_col not in df_treated.columns or not pd.api.types.is_numeric_dtype(df_treated[qty_col]):
            return df_treated, {"treated": False}

        # Corregir cantidades negativas
        neg_mask = df_treated[qty_col] < 0
        neg_count = int(neg_mask.sum())
        if neg_count > 0:
            df_treated.loc[neg_mask, qty_col] = np.nan

        # Detección de cargas atípicas (> 50 toneladas por camión individual)
        extreme_mask = df_treated[qty_col] > 50000.0  # 50 Toneladas
        extreme_count = int(extreme_mask.sum())
        df_treated["es_despacho_masivo"] = extreme_mask

        summary = {
            "total_records": len(df_treated),
            "negative_quantities_nullified": neg_count,
            "massive_shipments_flagged": extreme_count
        }
        return df_treated, summary
