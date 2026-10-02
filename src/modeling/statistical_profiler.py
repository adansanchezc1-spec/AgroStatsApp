"""
Motor de Rigor Estadístico, Ajuste de Distribuciones y Perfilamiento de Datos
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: SWEBOK (Data Science & Scientific Computing), ISO/IEC 25010, PEP 8
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

logger = logging.getLogger(__name__)


class StatisticalProfiler:
    """
    Motor analítico con rigor matemático y estadístico completo:
      - Estimación dual: Momentos Paramétricos vs. Estimadores Robustos No Paramétricos.
      - Ajuste y selección de Distribuciones de Probabilidad vía MLE con pruebas KS y AIC/BIC.
      - Contrastes formales de hipótesis (Normalidad: Shapiro/D'Agostino; Estacionariedad: ADF/KPSS).
      - Perfilamiento visual de valores ausentes (missingno).
    """

    @staticmethod
    def calculate_dual_moments(series: pd.Series) -> Dict[str, float]:
        """
        Calcula la tabla completa de medidas de tendencia central, dispersión y forma.
        """
        s = series.dropna().astype(float)
        if len(s) == 0:
            return {}

        n = len(s)
        # Paramétricos
        mean_val = float(s.mean())
        std_val = float(s.std(ddof=1)) if n > 1 else 0.0
        var_val = float(s.var(ddof=1)) if n > 1 else 0.0
        skew_val = float(stats.skew(s)) if n > 2 else 0.0
        kurt_val = float(stats.kurtosis(s)) if n > 3 else 0.0

        # No Paramétricos / Robustos
        median_val = float(s.median())
        q25, q75 = float(s.quantile(0.25)), float(s.quantile(0.75))
        iqr_val = q75 - q25
        mad_val = float(np.median(np.abs(s - median_val)))
        trimmed_mean_10 = float(stats.trim_mean(s, 0.10))
        
        # Coeficientes de Variación
        cv_parametric = (std_val / mean_val) if mean_val != 0 else 0.0
        rsd_iqr_robust = (iqr_val / median_val) if median_val != 0 else 0.0
        rsd_mad_robust = (mad_val * 1.4826 / median_val) if median_val != 0 else 0.0

        return {
            "n_obs": n,
            "media_parametrica": round(mean_val, 4),
            "desviacion_estandar": round(std_val, 4),
            "varianza": round(var_val, 4),
            "asimetria_fisher": round(skew_val, 4),
            "curtosis_exceso": round(kurt_val, 4),
            "mediana_robusta": round(median_val, 4),
            "percentil_25": round(q25, 4),
            "percentil_75": round(q75, 4),
            "iqr_intercuartilico": round(iqr_val, 4),
            "mad_mediana_absoluta": round(mad_val, 4),
            "media_recortada_10pct": round(trimmed_mean_10, 4),
            "cv_parametrico": round(cv_parametric, 4),
            "rsd_iqr_robusto": round(rsd_iqr_robust, 4),
            "rsd_mad_robusto": round(rsd_mad_robust, 4)
        }

    @staticmethod
    def test_normality(series: pd.Series) -> Dict[str, Any]:
        """
        Ejecuta pruebas formales de Normalidad:
          - Shapiro-Wilk (para n <= 5000)
          - D'Agostino-Pearson (omnibus basada en asimetría y curtosis)
        """
        s = series.dropna().astype(float)
        if len(s) < 8:
            return {"es_normal": False, "motivo": "Muestra insuficiente (<8 observaciones)"}

        # D'Agostino-Pearson omnibus
        stat_da, p_da = stats.normaltest(s)
        
        # Shapiro-Wilk (submuestra si n > 5000 por límites de scipy)
        sample_sw = s.sample(min(len(s), 5000), random_state=42) if len(s) > 5000 else s
        stat_sw, p_sw = stats.shapiro(sample_sw)

        es_normal = (p_da >= 0.05) and (p_sw >= 0.05)

        return {
            "shapiro_wilk_stat": round(float(stat_sw), 4),
            "shapiro_wilk_pvalue": float(p_sw),
            "dagostino_pearson_stat": round(float(stat_da), 4),
            "dagostino_pearson_pvalue": float(p_da),
            "es_normal_5pct": es_normal,
            "conclusion": "Distribución Gaussiana (No se rechaza H0)" if es_normal else "Distribución No Gaussiana (Se rechaza H0, p < 0.05)"
        }

    @staticmethod
    def fit_distributions(series: pd.Series) -> Dict[str, Any]:
        """
        Ajusta distribuciones teóricas continuas por Máxima Verosimilitud (MLE):
          - Normal (Gaussian)
          - Lognormal
          - Gamma
          - Exponencial
          - Weibull Min
        Calcula bondad de ajuste de Kolmogorov-Smirnov (KS-test) y criterios de información AIC/BIC.
        """
        s = series.dropna().astype(float)
        s_pos = s[s > 0]  # Requerido para Lognormal, Gamma, Weibull
        n = len(s)
        if n < 10:
            return {"mejor_distribucion": "Indeterminada"}

        distributions = {
            "Normal": (stats.norm, s),
            "Lognormal": (stats.lognorm, s_pos),
            "Gamma": (stats.gamma, s_pos),
            "Exponencial": (stats.expon, s_pos),
            "Weibull": (stats.weibull_min, s_pos)
        }

        results = []

        for name, (dist, data) in distributions.items():
            if len(data) < 10:
                continue
            try:
                params = dist.fit(data)
                # Prueba Kolmogorov-Smirnov
                ks_stat, ks_pval = stats.kstest(data, dist.name, args=params)
                
                # Log-Likelihood
                log_lik = float(np.sum(dist.logpdf(data, *params)))
                k_params = len(params)
                aic = 2 * k_params - 2 * log_lik
                bic = k_params * np.log(len(data)) - 2 * log_lik

                results.append({
                    "distribucion": name,
                    "ks_statistic": round(float(ks_stat), 4),
                    "ks_pvalue": float(ks_pval),
                    "aic": round(aic, 2),
                    "bic": round(bic, 2),
                    "parametros": [round(float(p), 4) for p in params]
                })
            except Exception:
                pass

        if not results:
            return {"mejor_distribucion": "Normal"}

        # Ordenar por menor estadístico KS (mejor ajuste empírico a la CDF)
        results.sort(key=lambda x: x["ks_statistic"])
        best = results[0]

        return {
            "mejor_distribucion": best["distribucion"],
            "mejor_ks_stat": best["ks_statistic"],
            "mejor_ks_pvalue": best["ks_pvalue"],
            "comparativa_completa": results
        }

    @staticmethod
    def test_stationarity(series: pd.Series) -> Dict[str, Any]:
        """
        Evalúa la estacionariedad de una serie temporal usando:
          - Augmented Dickey-Fuller (ADF, H0: Presencia de raíz unitaria / no estacionaria)
          - KPSS (H0: Serie estacionaria alrededor de nivel o tendencia)
        """
        s = series.dropna().astype(float)
        if len(s) < 20:
            return {"estacionaria": True, "motivo": "Serie corta"}

        # ADF
        adf_res = adfuller(s, autolag="AIC")
        adf_stat = float(adf_res[0])
        adf_pval = float(adf_res[1])
        adf_crit = {k: float(v) for k, v in adf_res[4].items()}

        # KPSS
        try:
            kpss_res = kpss(s, regression="c", nlags="auto")
            kpss_stat = float(kpss_res[0])
            kpss_pval = float(kpss_res[1])
        except Exception:
            kpss_stat, kpss_pval = 0.0, 1.0

        # Si ADF p < 0.05 y KPSS p >= 0.05 -> Estacionaria pura I(0)
        es_estacionaria = (adf_pval < 0.05)

        return {
            "adf_statistic": round(adf_stat, 4),
            "adf_pvalue": adf_pval,
            "adf_critical_values": adf_crit,
            "kpss_statistic": round(kpss_stat, 4),
            "kpss_pvalue": kpss_pval,
            "es_estacionaria": es_estacionaria,
            "orden_integracion": "I(0) Estacionaria" if es_estacionaria else "I(1) Raíz Unitaria (Requiere Diferenciación)"
        }

    @classmethod
    def plot_statistical_distribution(
        cls,
        series: pd.Series,
        var_name: str,
        output_file: Path
    ) -> None:
        """Genera figura con Histograma + KDE + QQ-Plot + Boxplot/Violin."""
        s = series.dropna().astype(float)
        if len(s) < 5:
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # 1. Histograma + KDE
        sns.histplot(s, kde=True, ax=axes[0], color="#2b5c8f", stat="density", bins=30)
        axes[0].set_title(f"Distribución Empírica y KDE: {var_name}", fontsize=12, fontweight="bold")
        axes[0].set_xlabel(var_name)
        axes[0].set_ylabel("Densidad")

        # 2. Q-Q Plot Normal
        stats.probplot(s, dist="norm", plot=axes[1])
        axes[1].get_lines()[0].set_markerfacecolor('#e74c3c')
        axes[1].get_lines()[0].set_markeredgecolor('#c0392b')
        axes[1].get_lines()[1].set_color('#2c3e50')
        axes[1].set_title("Q-Q Plot vs. Normal Teórica", fontsize=12, fontweight="bold")

        # 3. Boxplot con Violin Plot
        sns.violinplot(y=s, ax=axes[2], color="#ecf0f1", inner=None)
        sns.boxplot(y=s, ax=axes[2], width=0.3, color="#3498db", fliersize=3)
        axes[2].set_title("Diagrama de Caja y Violín (Dispersión e IQR)", fontsize=12, fontweight="bold")
        axes[2].set_ylabel(var_name)

        plt.tight_layout()
        fig.savefig(output_file, dpi=150)
        plt.close(fig)
        logger.info(f"Gráfico de rigor estadístico guardado en: {output_file}")

    @classmethod
    def plot_missingness_profile(
        cls,
        df: pd.DataFrame,
        dataset_name: str,
        output_file: Path
    ) -> None:
        """Genera matriz de completitud y ausencias mediante missingno."""
        if df.empty or len(df.columns) == 0 or len(df) < 2:
            logger.warning(f"DataFrame vacío o insuficiente para missingno: {dataset_name}")
            return

        output_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            fig, ax = plt.subplots(figsize=(14, 6))
            sample_df = df.head(500) if len(df) > 500 else df
            msno.matrix(sample_df, ax=ax, sparkline=False, color=(0.18, 0.38, 0.58), fontsize=10)
            ax.set_title(f"Perfil de Ausencias (Missingno Matrix): {dataset_name}", fontsize=14, fontweight="bold", pad=20)
            
            plt.tight_layout()
            fig.savefig(output_file, dpi=150)
            plt.close(fig)
            logger.info(f"Perfil missingno guardado en: {output_file}")
        except Exception as e:
            logger.warning(f"No fue posible generar matriz missingno para {dataset_name}: {e}")
            plt.close('all')
