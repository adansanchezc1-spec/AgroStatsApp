"""
Motor de Exploración y Perfilamiento Informático de Datos Agropecuarios
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Calidad de Datos 6D), ISO 25010, Rubin Framework, PEP 8
"""

import logging
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class DatasetProfiler:
    """
    Motor de análisis exploratorio informático para datasets agropecuarios.
    Examina sistemáticamente: metadatos, contexto, granularidad temporal/espacial,
    matriz de datos nulos, duplicados e integridad de claves primarias.
    """

    @staticmethod
    def inspect(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
        """
        Genera un diagnóstico multidimensional completo en formato diccionario.
        """
        rows, cols = df.shape
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        # 1. Clasificación de Tipos de Columnas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        object_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

        # Detección de columnas de fecha no parseadas
        date_candidates = []
        for col in object_cols:
            col_lower = col.lower()
            if any(k in col_lower for k in ["fecha", "date", "periodo", "ano", "ao", "mes"]):
                date_candidates.append(col)

        # 2. Análisis de Nulos y Ausencias
        null_counts = df.isna().sum().to_dict()
        null_percents = (df.isna().mean() * 100).round(2).to_dict()
        total_cells = rows * cols
        total_nulls = sum(null_counts.values())
        global_null_pct = round((total_nulls / total_cells * 100), 2) if total_cells > 0 else 0.0
        complete_rows = int((~df.isna().any(axis=1)).sum())
        complete_rows_pct = round((complete_rows / rows * 100), 2) if rows > 0 else 0.0

        # 3. Análisis de Duplicados
        exact_duplicates = int(df.duplicated().sum())
        exact_duplicates_pct = round((exact_duplicates / rows * 100), 2) if rows > 0 else 0.0

        # 4. Análisis de Granularidad Espacial y Temporal
        spatial_cols = [c for c in df.columns if any(k in c.lower() for k in [
            "municipio", "departamento", "cod_municipio", "codmpo", "estacion", "codigoestacion", "latitud", "longitud"
        ])]
        spatial_summary = {}
        for sc in spatial_cols:
            spatial_summary[sc] = {
                "unique_count": int(df[sc].nunique()),
                "sample_values": df[sc].dropna().unique()[:5].tolist()
            }

        temporal_summary = {}
        target_dates = datetime_cols if datetime_cols else date_candidates
        for tc in target_dates:
            try:
                parsed_dates = pd.to_datetime(df[tc], errors="coerce").dropna()
                if len(parsed_dates) > 0:
                    temporal_summary[tc] = {
                        "min_date": str(parsed_dates.min()),
                        "max_date": str(parsed_dates.max()),
                        "total_days_span": int((parsed_dates.max() - parsed_dates.min()).days),
                        "unique_dates": int(parsed_dates.nunique()),
                    }
            except Exception:
                pass

        # 5. Detección de Claves Candidatas
        key_candidates = []
        for col in df.columns:
            if df[col].nunique() == rows and null_counts[col] == 0:
                key_candidates.append(col)

        return {
            "metadata": {
                "dataset_name": dataset_name,
                "total_rows": rows,
                "total_columns": cols,
                "memory_mb": round(memory_mb, 2),
                "numeric_columns_count": len(numeric_cols),
                "categorical_columns_count": len(object_cols),
                "datetime_columns_count": len(datetime_cols) + len(date_candidates),
            },
            "missingness": {
                "total_null_cells": total_nulls,
                "global_missing_rate_pct": global_null_pct,
                "complete_rows_count": complete_rows,
                "complete_rows_pct": complete_rows_pct,
                "null_counts_by_col": null_counts,
                "null_percents_by_col": null_percents,
                "columns_with_missing": [c for c, count in null_counts.items() if count > 0],
            },
            "duplication": {
                "exact_duplicate_rows": exact_duplicates,
                "duplicate_rate_pct": exact_duplicates_pct,
                "unique_key_candidates": key_candidates,
            },
            "granularity": {
                "spatial_features": spatial_summary,
                "temporal_features": temporal_summary,
            },
            "columns": {
                "numeric": numeric_cols,
                "categorical": object_cols,
                "date_candidates": date_candidates,
            }
        }

    @staticmethod
    def profile_table(df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera una tabla resumen columna a columna lista para visualizar en Jupyter.
        """
        rows = len(df)
        records = []

        for col in df.columns:
            dtype = str(df[col].dtype)
            n_null = int(df[col].isna().sum())
            pct_null = round((n_null / rows * 100), 2) if rows > 0 else 0.0
            n_unique = int(df[col].nunique())

            # Estadísticos condicionales según tipo
            if pd.api.types.is_numeric_dtype(df[col]):
                mean_val = round(float(df[col].mean()), 2) if df[col].notna().any() else np.nan
                std_val = round(float(df[col].std()), 2) if df[col].notna().any() else np.nan
                min_val = round(float(df[col].min()), 2) if df[col].notna().any() else np.nan
                max_val = round(float(df[col].max()), 2) if df[col].notna().any() else np.nan
                detail = f"Media={mean_val}, Std={std_val}, Rango=[{min_val} : {max_val}]"
            else:
                top_val = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
                top_freq = int((df[col] == top_val).sum()) if top_val != "N/A" else 0
                pct_top = round((top_freq / rows * 100), 1) if rows > 0 else 0.0
                detail = f"Moda='{str(top_val)[:15]}...' ({pct_top}%)"

            records.append({
                "Columna": col,
                "Tipo": dtype,
                "No_Nulos": rows - n_null,
                "Nulos": n_null,
                "%_Nulos": pct_null,
                "Valores_Únicos": n_unique,
                "Detalle_Estadístico": detail,
            })

        return pd.DataFrame(records)

    @staticmethod
    def plot_missingness_heatmap(df: pd.DataFrame, max_cols: int = 40, figsize: tuple = (12, 5)) -> plt.Figure:
        """
        Renderiza un mapa de calor matricial de datos faltantes (estilo Missingno).
        """
        cols_to_plot = df.columns[:max_cols]
        missing_matrix = df[cols_to_plot].isna()

        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(
            missing_matrix,
            cmap="viridis",
            cbar=False,
            yticklabels=False,
            ax=ax,
        )
        ax.set_title(f"Matriz de Ausencias (Valores Nulos en Amarillo) - {len(cols_to_plot)} Columnas", fontsize=12)
        ax.set_xlabel("Variables / Características")
        ax.set_ylabel("Filas / Observaciones")
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_distributions(df: pd.DataFrame, max_features: int = 6, figsize: tuple = (14, 8)) -> Optional[plt.Figure]:
        """
        Genera gráficos de distribución e histogramas de variables numéricas.
        """
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_features]
        if not num_cols:
            return None

        n_plots = len(num_cols)
        cols_grid = min(3, n_plots)
        rows_grid = (n_plots + cols_grid - 1) // cols_grid

        fig, axes = plt.subplots(rows_grid, cols_grid, figsize=figsize)
        if n_plots == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        for idx, col in enumerate(num_cols):
            clean_series = df[col].dropna()
            sns.histplot(clean_series, kde=True, ax=axes[idx], color="#1b5e20", bins=25)
            axes[idx].set_title(f"Distribución: {col}", fontsize=10)
            axes[idx].grid(True, alpha=0.3)

        # Ocultar ejes vacíos si los hay
        for j in range(idx + 1, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()
        return fig
