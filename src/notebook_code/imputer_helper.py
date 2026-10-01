"""
Puente de Imputación Inteligente y Comparación para Notebooks
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: Rubin Framework, Preservación de Varianza, Visualización Diagnóstica
"""

import logging
from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import sys
from pathlib import Path

try:
    from imputer.imputation.imputation_engine import IntelligentImputer, ImputationBenchmarkResult
    from imputer.imputation.rubin_diagnostics import RubinDiagnostics, MissingPatternReport
except ImportError:
    src_dir = Path(__file__).resolve().parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from imputer.imputation.imputation_engine import IntelligentImputer, ImputationBenchmarkResult
    from imputer.imputation.rubin_diagnostics import RubinDiagnostics, MissingPatternReport

logger = logging.getLogger(__name__)


class NotebookImputerBridge:
    """
    Facilitador interactivo para la ejecución del motor de imputación
    en Jupyter Notebooks, con tablas comparativas y gráficos de preservación de varianza.
    """

    def __init__(self, variance_penalty_weight: float = 1.5) -> None:
        self.imputer = IntelligentImputer(variance_penalty_weight=variance_penalty_weight)

    def diagnose(self, df: pd.DataFrame) -> MissingPatternReport:
        """
        Ejecuta el diagnóstico estadístico de ausencias de Rubin y Little.
        """
        return RubinDiagnostics.inspect(df)

    def run_benchmark(
        self,
        df: pd.DataFrame,
        target_columns: Optional[List[str]] = None,
        inject_audit_flags: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, ImputationBenchmarkResult]:
        """
        Ejecuta el torneo competitivo y retorna:
        (df_imputado, tabla_resumen_benchmark, resultado_completo)
        """
        result = self.imputer.fit_impute(
            df=df,
            inject_audit_flags=inject_audit_flags,
            target_columns=target_columns,
        )

        # Construir tabla comparativa en pandas
        records = []
        for algo_name, score in result.scores_by_algorithm.items():
            records.append({
                "Algoritmo": algo_name,
                "Score_Torneo (RMSE x Varianza)": round(score, 4),
                "Seleccionado_Ganador": "✓ Ganador" if algo_name == result.winning_algorithm_name else "",
            })

        if records:
            summary_df = pd.DataFrame(records).sort_values("Score_Torneo (RMSE x Varianza)")
        else:
            summary_df = pd.DataFrame([{
                "Algoritmo": result.winning_algorithm_name,
                "Score_Torneo (RMSE x Varianza)": 0.0,
                "Seleccionado_Ganador": "N/A (Datos completos)",
            }])
        return result.imputed_dataframe, summary_df, result

    @staticmethod
    def plot_imputation_comparison(
        original_df: pd.DataFrame,
        imputed_df: pd.DataFrame,
        feature_col: str,
        figsize: tuple = (12, 4),
    ) -> Optional[plt.Figure]:
        """
        Compara la distribución de una variable antes y después de la imputación
        para auditar visualmente que no se haya colapsado la varianza natural.
        """
        if feature_col not in original_df.columns or feature_col not in imputed_df.columns:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        orig_clean = original_df[feature_col].dropna()
        imp_series = imputed_df[feature_col]

        # Gráfico 1: Histogramas / KDE superpuestos
        sns.kdeplot(orig_clean, ax=ax1, label="Original (Observado)", color="#1976d2", linewidth=2)
        sns.kdeplot(imp_series, ax=ax1, label="Post-Imputación (Completo)", color="#e65100", linestyle="--", linewidth=2)
        ax1.set_title(f"Densidad: {feature_col}")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Gráfico 2: Boxplots lado a lado
        box_data = pd.DataFrame({
            "Valor": list(orig_clean) + list(imp_series),
            "Estado": ["Original"] * len(orig_clean) + ["Imputado"] * len(imp_series),
        })
        sns.boxplot(data=box_data, x="Estado", y="Valor", ax=ax2, palette=["#90caf9", "#ffcc80"])
        ax2.set_title(f"Boxplot de Varianza: {feature_col}")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig
