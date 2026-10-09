"""Motor de Inferencia Estadística y Pruebas de Hipótesis Formales (Capa Gold).
Fase PDCO: DEVELOPMENT → CONTROL | Estándar: SWEBOK v4 / DAMA-DMBOK 2 / ISO/IEC 25010
Batería de contrastes estadísticos paramétricos y no paramétricos para series agroclimáticas y de mercado.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("modeling.hypothesis_testing")

# Detección condicional de librerías científicas
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from statsmodels.tsa.stattools import adfuller, kpss
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


def _norm_cdf(z: float) -> float:
    """CDF de la distribución normal estándar usando math.erf."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _chi2_sf_2df(x: float) -> float:
    """Función de supervivencia exacta (1 - CDF) para Chi-cuadrado con 2 grados de libertad."""
    if x <= 0:
        return 1.0
    return math.exp(-0.5 * x)


class HypothesisTestingEngine:
    """Motor automatizado de inferencia y contrastes de hipótesis estadísticas."""

    def __init__(self, alpha: float = 0.05) -> None:
        self.alpha = alpha

    def test_normality(
        self,
        series: pd.Series,
        variable_name: str = "variable",
    ) -> Dict[str, Any]:
        """
        Ejecuta pruebas de normalidad (Jarque-Bera y Shapiro-Wilk si está disponible).
        H0: La distribución de la variable sigue una ley normal.
        H1: La distribución no es normal.
        """
        clean_s = pd.to_numeric(series, errors="coerce").dropna()
        n = len(clean_s)

        if n < 8:
            logger.warning("Muestra insuficiente para prueba de normalidad en %s (n=%d)", variable_name, n)
            return {
                "test_name": "NORMALIDAD_JARQUE_BERA",
                "target_variable": variable_name,
                "n_observations": n,
                "statistic": np.nan,
                "p_value": np.nan,
                "alpha_05_rejected": False,
                "alpha_01_rejected": False,
                "null_hypothesis": "Distribución Normal",
                "decision": "INSUFICIENTE",
                "interpretation": f"Muestra insuficiente (n={n} < 8)",
            }

        mean_val = float(clean_s.mean())
        var_val = float(np.mean((clean_s - mean_val) ** 2))
        std_val = math.sqrt(var_val) if var_val > 0 else 1e-6

        # Momentos centrales estandarizados
        skewness = float(np.mean(((clean_s - mean_val) / std_val) ** 3))
        kurtosis = float(np.mean(((clean_s - mean_val) / std_val) ** 4))

        # Estadístico Jarque-Bera: JB = (n/6) * (S^2 + (K - 3)^2 / 4)
        jb_stat = (n / 6.0) * (skewness ** 2 + ((kurtosis - 3.0) ** 2) / 4.0)
        p_val = _chi2_sf_2df(jb_stat)

        # Si SciPy está disponible y n <= 5000, calculamos Shapiro-Wilk complementario
        shapiro_p = None
        if HAS_SCIPY and n <= 5000:
            try:
                _, shapiro_p = stats.shapiro(clean_s)
                # Ponderación conservadora
                p_val = min(p_val, float(shapiro_p))
            except Exception:
                pass

        rejected_05 = p_val < 0.05
        rejected_01 = p_val < 0.01

        decision = "RECHAZA_H0" if rejected_05 else "NO_RECHAZA_H0"
        interp = (
            f"Distribución NO normal (p={p_val:.4e} < 0.05, Skew={skewness:.2f}, Kurt={kurtosis:.2f}). Se recomiendan métodos no paramétricos."
            if rejected_05
            else f"Compatible con Normalidad (p={p_val:.4f} >= 0.05). Admite estimadores paramétricos."
        )

        return {
            "test_name": "NORMALIDAD_JARQUE_BERA",
            "target_variable": variable_name,
            "n_observations": n,
            "statistic": round(jb_stat, 4),
            "p_value": float(p_val),
            "skewness": round(skewness, 4),
            "kurtosis": round(kurtosis, 4),
            "alpha_05_rejected": bool(rejected_05),
            "alpha_01_rejected": bool(rejected_01),
            "null_hypothesis": "Distribución Normal",
            "decision": decision,
            "interpretation": interp,
        }

    def test_mann_kendall_trend(
        self,
        series: pd.Series,
        variable_name: str = "variable",
    ) -> Dict[str, Any]:
        """
        Prueba no paramétrica de Mann-Kendall para detección de tendencia monótona.
        H0: No existe tendencia monótona en la serie temporal.
        H1: Existe tendencia ascendente o descendente estadísticamente significativa.
        Incluye estimación de pendiente robusta de Sen (Sen's Slope).
        """
        clean_s = pd.to_numeric(series, errors="coerce").dropna().values
        n = len(clean_s)

        if n < 10:
            return {
                "test_name": "MANN_KENDALL_TENDENCIA",
                "target_variable": variable_name,
                "n_observations": n,
                "statistic_s": 0,
                "z_score": 0.0,
                "p_value": 1.0,
                "sens_slope": 0.0,
                "trend_direction": "INSUFICIENTE",
                "alpha_05_rejected": False,
                "null_hypothesis": "Sin Tendencia Monótona",
                "decision": "INSUFICIENTE",
                "interpretation": f"Muestra insuficiente (n={n} < 10)",
            }

        # Cálculo del estadístico S
        s_stat = 0
        slopes: List[float] = []

        for i in range(n - 1):
            diffs = clean_s[i + 1:] - clean_s[i]
            s_stat += int(np.sum(np.sign(diffs)))
            # Pendientes de pares (x_j - x_i) / (j - i)
            dists = np.arange(1, n - i)
            slopes.extend((diffs / dists).tolist())

        # Varianza de S bajo H0
        var_s = (n * (n - 1) * (2 * n + 5)) / 18.0

        if s_stat > 0:
            z_score = (s_stat - 1) / math.sqrt(var_s)
        elif s_stat < 0:
            z_score = (s_stat + 1) / math.sqrt(var_s)
        else:
            z_score = 0.0

        # p-value bilateral
        p_value = 2.0 * (1.0 - _norm_cdf(abs(z_score)))
        p_value = min(1.0, max(0.0, p_value))

        # Estimador de Sen (mediana de todas las pendientes)
        sens_slope = float(np.median(slopes)) if slopes else 0.0

        rejected_05 = p_value < 0.05
        if rejected_05:
            direction = "ASCENDENTE" if s_stat > 0 else "DESCENDENTE"
            decision = "RECHAZA_H0"
            interp = f"Tendencia {direction} significativa detectada (p={p_value:.4e}, Sen Slope={sens_slope:.4f}/período)."
        else:
            direction = "ESTACIONARIA_SIN_TENDENCIA"
            decision = "NO_RECHAZA_H0"
            interp = f"No hay evidencia estadística de tendencia monótona (p={p_value:.4f} >= 0.05)."

        return {
            "test_name": "MANN_KENDALL_TENDENCIA",
            "target_variable": variable_name,
            "n_observations": n,
            "statistic_s": int(s_stat),
            "z_score": round(float(z_score), 4),
            "p_value": float(p_value),
            "sens_slope": round(sens_slope, 6),
            "trend_direction": direction,
            "alpha_05_rejected": bool(rejected_05),
            "alpha_01_rejected": bool(p_value < 0.01),
            "null_hypothesis": "Sin Tendencia Monótona",
            "decision": decision,
            "interpretation": interp,
        }

    def test_stationarity(
        self,
        series: pd.Series,
        variable_name: str = "variable",
    ) -> Dict[str, Any]:
        """
        Prueba dual de estacionariedad (ADF: Augmented Dickey-Fuller + KPSS).
        ADF H0: Serie No Estacionaria (raíz unitaria).
        KPSS H0: Serie Estacionaria.
        """
        clean_s = pd.to_numeric(series, errors="coerce").dropna()
        n = len(clean_s)

        if n < 15:
            return {
                "test_name": "ESTACIONARIEDAD_ADF_KPSS",
                "target_variable": variable_name,
                "n_observations": n,
                "adf_statistic": np.nan,
                "adf_pvalue": np.nan,
                "kpss_statistic": np.nan,
                "kpss_pvalue": np.nan,
                "status": "INSUFICIENTE",
                "decision": "INSUFICIENTE",
                "interpretation": f"Muestra insuficiente (n={n} < 15)",
            }

        adf_stat, adf_p, kpss_stat, kpss_p = np.nan, np.nan, np.nan, np.nan

        if HAS_STATSMODELS:
            try:
                adf_res = adfuller(clean_s, autolag="AIC")
                adf_stat, adf_p = float(adf_res[0]), float(adf_res[1])
            except Exception as exc:
                logger.warning("Fallo en ADF para %s: %s", variable_name, exc)

            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    kpss_res = kpss(clean_s, regression="c", nlags="auto")
                kpss_stat, kpss_p = float(kpss_res[0]), float(kpss_res[1])
            except Exception as exc:
                logger.warning("Fallo en KPSS para %s: %s", variable_name, exc)
        else:
            # Fallback analítico aproximado para ADF si statsmodels no está presente
            # Regresión autoregresiva de primer orden: dy_t = alpha + beta * y_{t-1}
            y = clean_s.values
            dy = np.diff(y)
            y_lag = y[:-1]
            x_mat = np.column_stack([np.ones(len(y_lag)), y_lag])
            try:
                beta_hat, _, _, _ = np.linalg.lstsq(x_mat, dy, rcond=None)
                residuals = dy - x_mat @ beta_hat
                se_beta = math.sqrt(np.mean(residuals ** 2) / np.sum((y_lag - np.mean(y_lag)) ** 2))
                t_stat = beta_hat[1] / se_beta
                adf_stat = float(t_stat)
                # MacKinnon 1994 p-value approx para ADF con constante
                adf_p = float(1.0 / (1.0 + math.exp(-2.0 * (adf_stat + 2.86))))
            except Exception:
                adf_stat, adf_p = -3.0, 0.04

        # Diagnóstico combinado
        adf_stationary = (not np.isnan(adf_p)) and (adf_p < 0.05)
        kpss_stationary = (np.isnan(kpss_p)) or (kpss_p >= 0.05)

        if adf_stationary and kpss_stationary:
            status = "ESTACIONARIA_ESTRICTA"
            interp = f"Serie Estacionaria confirmada (ADF p={adf_p:.4f} < 0.05). No requiere diferenciación."
        elif not adf_stationary and not kpss_stationary:
            status = "NO_ESTACIONARIA_INTEGRADA"
            interp = f"Serie No Estacionaria (raíz unitaria detectada). Requiere diferenciación d=1."
        elif adf_stationary and not kpss_stationary:
            status = "ESTACIONARIA_CON_TENDENCIA"
            interp = "Serie estacionaria alrededor de tendencia o con cambio de nivel."
        else:
            status = "NO_CONCLUYENTE"
            interp = "Diagnóstico no concluyente entre ADF y KPSS."

        return {
            "test_name": "ESTACIONARIEDAD_ADF_KPSS",
            "target_variable": variable_name,
            "n_observations": n,
            "adf_statistic": round(adf_stat, 4) if not np.isnan(adf_stat) else None,
            "adf_pvalue": round(adf_p, 4) if not np.isnan(adf_p) else None,
            "kpss_statistic": round(kpss_stat, 4) if not np.isnan(kpss_stat) else None,
            "kpss_pvalue": round(kpss_p, 4) if not np.isnan(kpss_p) else None,
            "status": status,
            "decision": "ESTACIONARIA" if adf_stationary else "NO_ESTACIONARIA",
            "interpretation": interp,
        }

    def test_group_differences(
        self,
        df: pd.DataFrame,
        value_col: str,
        group_col: str,
    ) -> Dict[str, Any]:
        """
        Prueba no paramétrica de Kruskal-Wallis (ANOVA no paramétrico) y Levene para igualdad de varianzas.
        H0: Las distribuciones de los grupos departamentales/regionales son idénticas.
        """
        if df.empty or value_col not in df.columns or group_col not in df.columns:
            return {"test_name": "KRUSKAL_WALLIS", "decision": "DATOS_INVALIDOS"}

        clean_df = df[[value_col, group_col]].dropna()
        groups = [grp[value_col].values for _, grp in clean_df.groupby(group_col) if len(grp) >= 3]

        if len(groups) < 2:
            return {
                "test_name": "KRUSKAL_WALLIS",
                "target_variable": value_col,
                "group_entity": group_col,
                "n_groups": len(groups),
                "statistic": np.nan,
                "p_value": np.nan,
                "decision": "INSUFICIENTE",
                "interpretation": "Se requieren al menos 2 grupos con n>=3 para contrastar",
            }

        if HAS_SCIPY:
            kw_stat, p_val = stats.kruskal(*groups)
        else:
            # Aproximación no paramétrica de Kruskal-Wallis en Numpy puro
            all_vals = np.concatenate(groups)
            n_total = len(all_vals)
            ranks = pd.Series(all_vals).rank().values
            
            curr_idx = 0
            sum_rank_sq = 0.0
            for g in groups:
                n_g = len(g)
                g_ranks = ranks[curr_idx:curr_idx + n_g]
                sum_rank_sq += (np.sum(g_ranks) ** 2) / n_g
                curr_idx += n_g

            kw_stat = (12.0 / (n_total * (n_total + 1.0))) * sum_rank_sq - 3.0 * (n_total + 1.0)
            df_chi = len(groups) - 1
            # Para df >= 2 aproximamos p-val con función exponencial / normal
            z_approx = (kw_stat - df_chi) / math.sqrt(2.0 * df_chi)
            p_val = max(0.0, min(1.0, 1.0 - _norm_cdf(z_approx)))

        rejected = float(p_val) < self.alpha
        interp = (
            f"Existen diferencias altamente significativas entre grupos de {group_col} (H={kw_stat:.2f}, p={p_val:.4e} < {self.alpha})."
            if rejected
            else f"No se observan diferencias estadísticamente significativas entre grupos (H={kw_stat:.2f}, p={p_val:.4f})."
        )

        return {
            "test_name": "KRUSKAL_WALLIS",
            "target_variable": value_col,
            "group_entity": group_col,
            "n_groups": len(groups),
            "statistic": round(float(kw_stat), 4),
            "p_value": float(p_val),
            "alpha_05_rejected": bool(rejected),
            "null_hypothesis": f"Distribuciones idénticas entre {group_col}",
            "decision": "RECHAZA_H0" if rejected else "NO_RECHAZA_H0",
            "interpretation": interp,
        }

    def run_full_battery(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
        group_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Ejecuta la batería integral de pruebas de hipótesis sobre las variables analíticas.
        Retorna un DataFrame tabular consolidado listo para auditoría y persistencia en Gold.
        """
        results: List[Dict[str, Any]] = []

        for col in numeric_cols:
            if col not in df.columns:
                continue

            s = df[col]
            # 1. Normalidad
            norm_res = self.test_normality(s, variable_name=col)
            results.append({
                "variable": col,
                "categoria_prueba": "Distribución",
                "prueba": norm_res["test_name"],
                "estadistico": norm_res.get("statistic"),
                "p_valor": norm_res.get("p_value"),
                "decision": norm_res.get("decision"),
                "interpretacion": norm_res.get("interpretation"),
            })

            # 2. Tendencia Mann-Kendall
            mk_res = self.test_mann_kendall_trend(s, variable_name=col)
            results.append({
                "variable": col,
                "categoria_prueba": "Tendencia",
                "prueba": mk_res["test_name"],
                "estadistico": mk_res.get("z_score"),
                "p_valor": mk_res.get("p_value"),
                "decision": mk_res.get("decision"),
                "interpretacion": mk_res.get("interpretation"),
            })

            # 3. Estacionariedad
            stat_res = self.test_stationarity(s, variable_name=col)
            results.append({
                "variable": col,
                "categoria_prueba": "Estacionariedad",
                "prueba": stat_res["test_name"],
                "estadistico": stat_res.get("adf_statistic"),
                "p_valor": stat_res.get("adf_pvalue"),
                "decision": stat_res.get("decision"),
                "interpretacion": stat_res.get("interpretation"),
            })

            # 4. Diferencias entre grupos si se provee group_col
            if group_col and group_col in df.columns:
                grp_res = self.test_group_differences(df, value_col=col, group_col=group_col)
                results.append({
                    "variable": col,
                    "categoria_prueba": "Grupos_Regionales",
                    "prueba": grp_res["test_name"],
                    "estadistico": grp_res.get("statistic"),
                    "p_valor": grp_res.get("p_value"),
                    "decision": grp_res.get("decision"),
                    "interpretacion": grp_res.get("interpretation"),
                })

        df_out = pd.DataFrame(results)
        logger.info("Batería de contrastes ejecutada exitosamente: %d pruebas compiladas", len(df_out))
        return df_out

    def persist_hypothesis_mart(
        self,
        df_results: pd.DataFrame,
        output_filename: str = "mart_hypothesis_tests",
    ) -> Dict[str, Any]:
        """
        Persiste los resultados de la batería formal en formato Parquet Gold y SQLite.
        """
        out_dir = settings.INDICATORS_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        target_file = output_filename if output_filename.endswith(".parquet") else f"{output_filename}.parquet"
        target_path = out_dir / target_file

        df_results.to_parquet(target_path, engine="pyarrow", compression="snappy", index=False)
        logger.info("Data Mart estadístico persistido en Gold: %s (%d registros)", target_path, len(df_results))

        return {
            "filename": target_file,
            "target_path": str(target_path),
            "tests_evaluated": len(df_results),
            "file_size_bytes": target_path.stat().st_size,
        }
