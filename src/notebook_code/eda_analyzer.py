"""
Analizador Exploratorio de Datos (EDA) para Notebooks Agropecuarios
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: SWEBOK, PEP 8, ISO/IEC 25010, Estadística Descriptiva e Inferencial
"""

import logging
from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


class EdaAnalyzer:
    """
    Motor estadístico para Análisis Exploratorio de Datos (EDA) en agricultura y bioestadística.
    Proporciona resúmenes distributivos, análisis de correlaciones, detección de anomalías
    y visualizaciones diagnósticas listas para publicación.
    """

    @staticmethod
    def describe_numeric_distributions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula estadísticos distributivos avanzados (asimetría, curtosis, IQR)
        para todas las variables numéricas del dataset.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return pd.DataFrame()

        records = []
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue

            q25 = float(series.quantile(0.25))
            q75 = float(series.quantile(0.75))
            iqr = q75 - q25
            skew = float(series.skew()) if len(series) > 2 else 0.0
            kurt = float(series.kurtosis()) if len(series) > 3 else 0.0

            records.append({
                "Variable": col,
                "Conteo": int(series.count()),
                "Nulos": int(df[col].isna().sum()),
                "Tasa_Nulos_%": round((df[col].isna().sum() / len(df)) * 100.0, 2),
                "Media": round(float(series.mean()), 4),
                "Desv_Std": round(float(series.std()), 4),
                "Min": round(float(series.min()), 4),
                "Q25": round(q25, 4),
                "Mediana": round(float(series.median()), 4),
                "Q75": round(q75, 4),
                "Max": round(float(series.max()), 4),
                "IQR": round(iqr, 4),
                "Asimetría": round(skew, 4),
                "Curtosis": round(kurt, 4),
            })

        return pd.DataFrame(records)

    @staticmethod
    def correlation_analysis(
        df: pd.DataFrame,
        method: str = "spearman",
        threshold_collinearity: float = 0.85,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calcula la matriz de correlación (Spearman o Pearson) e identifica
        pares con correlación fuerte o sospecha de multicolinealidad.
        """
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or numeric_df.shape[1] < 2:
            return pd.DataFrame(), pd.DataFrame()

        corr_matrix = numeric_df.corr(method=method)

        # Extraer pares sin duplicados simétricos ni diagonal
        pairs = []
        cols = corr_matrix.columns
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                c1, c2 = cols[i], cols[j]
                val = corr_matrix.loc[c1, c2]
                if not np.isnan(val):
                    pairs.append({
                        "Variable_1": c1,
                        "Variable_2": c2,
                        "Coeficiente": round(float(val), 4),
                        "Magnitud_Abs": round(abs(float(val)), 4),
                        "Alerta_Colinealidad": "⚠️ ALTA" if abs(val) >= threshold_collinearity else "Normal",
                    })

        pairs_df = pd.DataFrame(pairs).sort_values("Magnitud_Abs", ascending=False)
        return corr_matrix, pairs_df

    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        method: str = "tukey",
        threshold: float = 1.5,
    ) -> pd.DataFrame:
        """
        Detecta anomalías y valores atípicos mediante el criterio de Tukey (IQR)
        o Z-Score modificado.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        records = []

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 5:
                continue

            if method == "tukey":
                q25 = series.quantile(0.25)
                q75 = series.quantile(0.75)
                iqr = q75 - q25
                lower_bound = q25 - (threshold * iqr)
                upper_bound = q75 + (threshold * iqr)
                outliers_mask = (series < lower_bound) | (series > upper_bound)
            else:  # Z-score
                mean = series.mean()
                std = series.std()
                if std == 0:
                    continue
                z_scores = np.abs((series - mean) / std)
                outliers_mask = z_scores > threshold
                lower_bound = mean - (threshold * std)
                upper_bound = mean + (threshold * std)

            count = int(outliers_mask.sum())
            rate = round((count / len(series)) * 100.0, 2)

            records.append({
                "Variable": col,
                "Metodo": method.upper(),
                "Limite_Inferior": round(float(lower_bound), 4),
                "Limite_Superior": round(float(upper_bound), 4),
                "Conteo_Atipicos": count,
                "Tasa_Atipicos_%": rate,
            })

        return pd.DataFrame(records).sort_values("Conteo_Atipicos", ascending=False)

    @staticmethod
    def time_series_dynamics(
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        freq: str = "ME",
        rolling_window: int = 3,
    ) -> pd.DataFrame:
        """
        Calcula la dinámica temporal de una variable: tendencia agrupada,
        volatilidad móvil y tasa de crecimiento período a período.
        """
        if date_col not in df.columns or value_col not in df.columns:
            return pd.DataFrame()

        clean_df = df[[date_col, value_col]].dropna().copy()
        clean_df[date_col] = pd.to_datetime(clean_df[date_col], errors="coerce")
        clean_df = clean_df.dropna().sort_values(date_col)

        # Resampleo a la frecuencia deseada
        ts = clean_df.set_index(date_col)[value_col].resample(freq).mean().dropna()

        ts_df = pd.DataFrame({
            "Valor_Promedio": ts,
            f"Media_Movil_{rolling_window}P": ts.rolling(rolling_window, min_periods=1).mean(),
            f"Volatilidad_Movil_{rolling_window}P": ts.rolling(rolling_window, min_periods=1).std().fillna(0),
            "Variacion_Pct": ts.pct_change() * 100.0,
        }).reset_index()

        return ts_df

    @staticmethod
    def plot_correlation_heatmap(
        df: pd.DataFrame,
        cols: Optional[List[str]] = None,
        method: str = "spearman",
        figsize: Tuple[int, int] = (10, 8),
        title: str = "Matriz de Correlaciones",
    ) -> Optional[plt.Figure]:
        """Genera un heatmap estético con paleta divergente para correlaciones."""
        target_df = df[cols] if cols else df.select_dtypes(include=[np.number])
        if target_df.empty or target_df.shape[1] < 2:
            return None

        corr = target_df.corr(method=method)
        fig, ax = plt.subplots(figsize=figsize)

        mask = np.triu(np.ones_like(corr, dtype=bool))
        cmap = sns.diverging_palette(220, 20, as_cmap=True)

        sns.heatmap(
            corr,
            mask=mask,
            cmap=cmap,
            vmax=1.0,
            vmin=-1.0,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            annot=True,
            fmt=".2f",
            ax=ax,
        )
        ax.set_title(f"{title} ({method.capitalize()})", fontsize=13, pad=12)
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_time_series(
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        figsize: Tuple[int, int] = (12, 4),
        title: Optional[str] = None,
    ) -> Optional[plt.Figure]:
        """Genera gráfico de línea temporal con media móvil suavizada."""
        if date_col not in df.columns or value_col not in df.columns:
            return None

        clean_df = df[[date_col, value_col]].dropna().copy()
        clean_df[date_col] = pd.to_datetime(clean_df[date_col], errors="coerce")
        clean_df = clean_df.dropna().sort_values(date_col)

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(clean_df[date_col], clean_df[value_col], label="Observado", color="#1976d2", alpha=0.6, linewidth=1.2)

        # Suavizado móvil
        rolling_mean = clean_df[value_col].rolling(window=7, min_periods=1).mean()
        ax.plot(clean_df[date_col], rolling_mean, label="Media Móvil (7 periodos)", color="#e65100", linewidth=2.0)

        ax.set_title(title or f"Trayectoria Temporal de {value_col}", fontsize=12)
        ax.set_xlabel("Fecha")
        ax.set_ylabel(value_col)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_bivariate_relationship(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        figsize: Tuple[int, int] = (8, 5),
        title: Optional[str] = None,
    ) -> Optional[plt.Figure]:
        """Genera diagrama de dispersión con línea de regresión de tendencia."""
        if x_col not in df.columns or y_col not in df.columns:
            return None

        clean_df = df[[x_col, y_col]].dropna()
        if len(clean_df) < 3:
            return None

        fig, ax = plt.subplots(figsize=figsize)
        sns.regplot(
            data=clean_df,
            x=x_col,
            y=y_col,
            scatter_kws={"alpha": 0.5, "color": "#0288d1"},
            line_kws={"color": "#d32f2f", "linewidth": 2},
            ax=ax,
        )
        ax.set_title(title or f"Relación Bivariada: {x_col} vs {y_col}", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        return fig
