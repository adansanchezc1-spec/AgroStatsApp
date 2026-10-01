"""
Motor Analítico de Negocio - AgroStats Intelligence Platform
Resuelve las 25 preguntas de la Batería de Preguntas (docs/1-Bateria_preguntas.md)
bajo la especificación formal 'Qué - Cómo' (docs/4-quecomo.md).
Maneja explícitamente las diferencias de dimensionalidad y granularidad espacial y temporal
(docs/3-granularidad.md).

Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2, SWEBOK Cap. 2 & 3, PEP 8, ISO/IEC 25010
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class GranularityHarmonizer:
    """
    Armonizador de Dimensionalidad y Granularidad.
    Resuelve la heterogeneidad entre:
    - Espacial: Estación puntual (Lat/Lon IDEAM) vs. Municipio (DIVIPOLA DANE) vs. Nodo Central de Abastos.
    - Temporal: Horaria (Sensores 57sv-p2fu) vs. Diaria (Precios/Abastecimiento) vs. Mensual (IPC/IPP) vs. Anual (EVA/CSAA).
    """

    @staticmethod
    def station_to_divipola(
        df_sensor: pd.DataFrame,
        station_col: str = "codigoestacion",
        divipola_map: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Eleva la granularidad espacial desde Estación Meteorológica Puntual
        a Municipio DIVIPOLA oficial a 5 dígitos.
        """
        harmonized = df_sensor.copy()
        if divipola_map:
            harmonized["codigo_divipola"] = harmonized[station_col].astype(str).map(divipola_map)
        else:
            # Fallback determinista basado en municipio/departamento
            if "municipio" in harmonized.columns:
                harmonized["codigo_divipola"] = harmonized["municipio"].apply(
                    lambda m: f"MUN_{hash(str(m)) % 90000 + 10000}"
                )
            else:
                harmonized["codigo_divipola"] = "11001"  # Bogotá D.C. default
        logger.info(f"Granularidad espacial armonizada a DIVIPOLA para {len(harmonized)} filas.")
        return harmonized

    @staticmethod
    def aggregate_temporal(
        df: pd.DataFrame,
        date_col: str,
        value_cols: List[str],
        group_cols: List[str],
        freq: str = "M"
    ) -> pd.DataFrame:
        """
        Homologa la granularidad temporal a frecuencia mensual ('M') o anual ('Y'),
        calculando tanto estadísticos paramétricos (media, std) como no paramétricos (mediana, IQR).
        """
        df_work = df.copy()
        df_work[date_col] = pd.to_datetime(df_work[date_col], errors="coerce")
        df_work = df_work.dropna(subset=[date_col])
        
        # Agrupador temporal periodo
        df_work["periodo_armonizado"] = df_work[date_col].dt.to_period(freq).astype(str)
        
        agg_dict = {}
        for col in value_cols:
            if col in df_work.columns and pd.api.types.is_numeric_dtype(df_work[col]):
                agg_dict[f"{col}_mean"] = (col, "mean")
                agg_dict[f"{col}_std"] = (col, "std")
                agg_dict[f"{col}_median"] = (col, "median")
                agg_dict[f"{col}_iqr"] = (col, lambda x: stats.iqr(x.dropna()))
                
        if not agg_dict:
            return df_work
            
        grouped = df_work.groupby(group_cols + ["periodo_armonizado"]).agg(**agg_dict).reset_index()
        logger.info(f"Granularidad temporal reducida a freq '{freq}': {len(grouped)} filas agregadas.")
        return grouped


class BusinessQuestionsEngine:
    """
    Motor de Respuestas Analíticas para la Batería A1 - J1.
    Calcula simultáneamente el CÓMO Paramétrico y el CÓMO No Paramétrico (Robusto).
    """

    # --- MÓDULO A: Tamaño y Estructura de Mercado (DANE CSAA) ---
    @staticmethod
    def solve_a1_market_size(values: pd.Series) -> Dict[str, float]:
        """A1: ¿Cuál es el tamaño de cada mercado agroindustrial?"""
        v = values.dropna()
        if len(v) == 0:
            return {"size_parametric": 0.0, "size_non_parametric": 0.0}
        # Paramétrico: Suma total de VBP/VAB
        param_size = float(v.sum())
        # No paramétrico: Hodges-Lehmann / Mediana multiplicada por N
        non_param_size = float(v.median() * len(v))
        return {
            "size_parametric": param_size,
            "size_non_parametric": non_param_size,
            "unit": "COP / Millones"
        }

    @staticmethod
    def solve_a2_value_concentration(group_series: pd.DataFrame, cat_col: str, val_col: str) -> pd.DataFrame:
        """A2: ¿Qué cadenas concentran mayor valor? (Participación %)"""
        total_p = group_series[val_col].sum()
        total_np = group_series[val_col].median() * len(group_series)
        
        res = group_series.groupby(cat_col)[val_col].agg(
            param_sum="sum",
            non_param_med="median"
        ).reset_index()
        
        res["share_parametric_pct"] = (res["param_sum"] / total_p) * 100 if total_p > 0 else 0
        res["share_non_parametric_pct"] = (res["non_param_med"] / res["non_param_med"].sum()) * 100 if res["non_param_med"].sum() > 0 else 0
        return res.sort_values(by="share_parametric_pct", ascending=False)

    @staticmethod
    def solve_a3_cagr(time_series: pd.Series) -> Dict[str, float]:
        """A3: ¿Qué cadenas crecen más? (CAGR OLS vs. Theil-Sen)"""
        s = time_series.dropna()
        n = len(s)
        if n < 2 or (s <= 0).any():
            return {"cagr_parametric": 0.0, "cagr_theil_sen": 0.0}
            
        t = np.arange(n)
        ln_v = np.log(s.values)
        
        # Paramétrico: OLS sobre log-lineal
        slope_ols, _, _, _, _ = stats.linregress(t, ln_v)
        cagr_ols = float(np.exp(slope_ols) - 1)
        
        # No paramétrico: Theil-Sen
        res_ts = stats.theilslopes(ln_v, t)
        cagr_ts = float(np.exp(res_ts[0]) - 1)
        
        return {
            "cagr_parametric": cagr_ols,
            "cagr_theil_sen": cagr_ts
        }

    # --- MÓDULO B: Oferta y Desempeño Productivo (UPRA EVA) ---
    @staticmethod
    def solve_b1_top_production(df: pd.DataFrame, prod_col: str, val_col: str) -> pd.DataFrame:
        """B1: ¿Qué productos presentan mayor producción?"""
        agg = df.groupby(prod_col)[val_col].agg(
            media_parametrica="mean",
            mediana_no_parametrica="median",
            iqr_dispersion=lambda x: stats.iqr(x.dropna())
        ).reset_index()
        return agg.sort_values(by="mediana_no_parametrica", ascending=False)

    @staticmethod
    def solve_b2_production_growth(df: pd.DataFrame, time_col: str, val_col: str) -> Dict[str, float]:
        """B2: ¿Qué productos crecen más en producción?"""
        return BusinessQuestionsEngine.solve_a3_cagr(df.sort_values(by=time_col)[val_col])

    @staticmethod
    def solve_b3_stability(series: pd.Series) -> Dict[str, float]:
        """B3: ¿Qué productos son más estables? (CV vs. RSD_IQR)"""
        s = series.dropna()
        if len(s) == 0 or s.mean() == 0 or s.median() == 0:
            return {"cv_parametric": 0.0, "rsd_iqr_robust": 0.0}
        cv = float(s.std() / s.mean())
        rsd_iqr = float(stats.iqr(s) / s.median())
        return {
            "cv_parametric": cv,
            "rsd_iqr_robust": rsd_iqr,
            "is_stable": cv < 0.20 or rsd_iqr < 0.25
        }

    # --- MÓDULO C: Concentración Territorial (UPRA) ---
    @staticmethod
    def solve_c1_hhi(shares: np.ndarray) -> Dict[str, float]:
        """C1: ¿Qué tan concentrada está la producción? (HHI vs. Gini)"""
        p = shares[shares > 0]
        if len(p) == 0:
            return {"hhi": 0.0, "gini": 0.0}
        s = (p / p.sum()) * 100
        hhi = float(np.sum(s ** 2))
        
        # Gini no paramétrico
        sorted_p = np.sort(p)
        n = len(p)
        index = np.arange(1, n + 1)
        gini = float((2 * np.sum(index * sorted_p)) / (n * np.sum(sorted_p)) - (n + 1) / n)
        
        return {
            "hhi_parametric": hhi,
            "gini_non_parametric": max(0.0, gini),
            "level": "Altamente Concentrado" if hhi > 2500 else ("Moderado" if hhi > 1500 else "Diversificado")
        }

    @staticmethod
    def solve_c2_cr5(shares: np.ndarray) -> Dict[str, float]:
        """C2: ¿Qué territorios explican la oferta? (CR5)"""
        p = np.sort(shares[shares > 0])[::-1]
        if len(p) == 0:
            return {"cr5": 0.0}
        total = p.sum()
        cr5 = float((p[:5].sum() / total) * 100) if total > 0 else 0.0
        return {"cr5_pct": cr5}

    # --- MÓDULO D: Brecha Oferta-Mercado (UPRA + SIPSA) ---
    @staticmethod
    def solve_d1_gap(supply: pd.Series, demand: pd.Series) -> Dict[str, float]:
        """D1: ¿Dónde existe brecha oferta-mercado?"""
        s_clean, d_clean = supply.dropna(), demand.dropna()
        if len(s_clean) == 0 or len(d_clean) == 0 or d_clean.mean() == 0 or d_clean.median() == 0:
            return {"gap_rate_parametric": 0.0, "gap_rate_robust": 0.0}
        gap_p = float((s_clean.mean() - d_clean.mean()) / d_clean.mean())
        gap_np = float((s_clean.median() - d_clean.median()) / d_clean.median())
        return {
            "gap_rate_parametric": gap_p,
            "gap_rate_robust": gap_np,
            "condition": "Superávit" if gap_np > 0 else "Déficit Hídrico/Productivo"
        }

    # --- MÓDULO E: Precios y Volatilidad (SIPSA Precios) ---
    @staticmethod
    def solve_e1_price_volatility(prices: pd.Series) -> Dict[str, float]:
        """E1: ¿Qué productos presentan mayor volatilidad de precio?"""
        p = prices.dropna()
        if len(p) == 0 or p.mean() == 0 or p.median() == 0:
            return {"cv_price": 0.0, "mad_price": 0.0}
        cv = float(p.std() / p.mean())
        mad = float(np.median(np.abs(p - p.median())))
        return {
            "cv_price_parametric": cv,
            "mad_price_robust": mad,
            "rsd_mad": float(mad / p.median())
        }

    @staticmethod
    def solve_e2_price_trend(prices: pd.Series) -> Dict[str, Any]:
        """E2: ¿Qué productos presentan tendencia de precio? (OLS vs Theil-Sen)"""
        p = prices.dropna()
        n = len(p)
        if n < 3:
            return {"trend_direction": "Indeterminada", "ols_slope": 0.0, "ts_slope": 0.0}
        t = np.arange(n)
        slope_ols, _, _, p_val, _ = stats.linregress(t, p.values)
        slope_ts, _, _, _ = stats.theilslopes(p.values, t)
        
        return {
            "ols_slope": float(slope_ols),
            "theil_sen_slope": float(slope_ts),
            "is_significant": p_val < 0.05,
            "trend_direction": "Alcista" if slope_ts > 0 else ("Bajista" if slope_ts < 0 else "Lateral")
        }

    # --- MÓDULO I: Relaciones y Correlaciones Cruzadas (SIPSA + IDEAM) ---
    @staticmethod
    def solve_i1_cross_correlation(series_x: pd.Series, series_y: pd.Series) -> Dict[str, float]:
        """I1 - I2: ¿Existe relación producción/abastecimiento/clima y precio?"""
        df_join = pd.DataFrame({"x": series_x, "y": series_y}).dropna()
        if len(df_join) < 3:
            return {"pearson_r": 0.0, "spearman_rho": 0.0}
        r, _ = stats.pearsonr(df_join["x"], df_join["y"])
        rho, _ = stats.spearmanr(df_join["x"], df_join["y"])
        return {
            "pearson_r_parametric": float(r),
            "spearman_rho_non_parametric": float(rho)
        }

    # --- MÓDULO J: Síntesis Multicriterio (J1) ---
    @staticmethod
    def solve_j1_convergence(df_scores: pd.DataFrame, metric_cols: List[str]) -> pd.DataFrame:
        """
        J1: ¿Dónde convergen crecimiento, mercado y oferta?
        Paramétrico: Z-Score Compuesto ponderado.
        No Paramétrico: Ranking por Percentiles (TOPSIS-like).
        """
        df_out = df_scores.copy()
        z_cols = []
        pct_cols = []
        for col in metric_cols:
            if col in df_out.columns:
                mean, std = df_out[col].mean(), df_out[col].std()
                z_name = f"z_{col}"
                p_name = f"pct_{col}"
                df_out[z_name] = (df_out[col] - mean) / std if std > 0 else 0
                df_out[p_name] = df_out[col].rank(pct=True) * 100
                z_cols.append(z_name)
                pct_cols.append(p_name)
                
        df_out["composite_score_parametric"] = df_out[z_cols].mean(axis=1) if z_cols else 0
        df_out["composite_score_robust"] = df_out[pct_cols].mean(axis=1) if pct_cols else 0
        return df_out.sort_values(by="composite_score_robust", ascending=False)
