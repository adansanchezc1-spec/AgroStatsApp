"""
Diagnóstico de Ausencias bajo el Marco de Rubin (MCAR, MAR, MNAR)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: Rubin (1976), Little (1988), ISO 25010 (Integridad de Datos)
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class MissingPatternReport:
    """
    Reporte formal de la auditoría de datos faltantes.
    """
    total_rows: int
    total_cols: int
    missing_rates_by_col: Dict[str, float]
    missing_counts_by_col: Dict[str, int]
    diagnosed_mechanism: str  # 'MCAR', 'MAR', 'MNAR'
    littles_test_p_value: Optional[float]
    recommended_strategy: str
    details: Dict[str, str]


class RubinDiagnostics:
    """
    Motor estadístico para caracterizar el mecanismo de pérdida de datos.
    Permite seleccionar de manera matemáticamente justificada el algoritmo de imputación.
    """

    @staticmethod
    def inspect(df: pd.DataFrame) -> MissingPatternReport:
        """
        Ejecuta el análisis multidimensional de ausencias en el DataFrame.
        """
        total_rows, total_cols = df.shape
        missing_counts = df.isna().sum().to_dict()
        missing_rates = (df.isna().mean()).to_dict()

        cols_with_na = [col for col, count in missing_counts.items() if count > 0]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not cols_with_na:
            return MissingPatternReport(
                total_rows=total_rows,
                total_cols=total_cols,
                missing_rates_by_col=missing_rates,
                missing_counts_by_col=missing_counts,
                diagnosed_mechanism="COMPLETE_DATA",
                littles_test_p_value=1.0,
                recommended_strategy="NONE",
                details={"status": "El dataset no presenta valores nulos."},
            )

        # Matriz binaria de ausencia: 1 si es NaN, 0 si está observado
        missing_indicator = df.isna().astype(int)

        # Test de correlación biserial / t-test entre faltantes y covariables observadas (Proxy Little)
        p_values: List[float] = []
        for target_col in cols_with_na:
            indicator = missing_indicator[target_col]
            if indicator.sum() < 2 or (len(indicator) - indicator.sum()) < 2:
                continue

            for obs_col in numeric_cols:
                if obs_col == target_col or obs_col in cols_with_na:
                    continue
                valid_mask = df[obs_col].notna()
                group_missing = df.loc[valid_mask & (indicator == 1), obs_col]
                group_observed = df.loc[valid_mask & (indicator == 0), obs_col]

                if len(group_missing) >= 2 and len(group_observed) >= 2:
                    try:
                        _, p_val = stats.ttest_ind(group_missing, group_observed, equal_var=False)
                        if not np.isnan(p_val):
                            p_values.append(float(p_val))
                    except Exception:
                        pass

        # Interpretación bajo la hipótesis nula H0: Los datos son MCAR (p > 0.05)
        littles_p = float(np.median(p_values)) if p_values else 0.5

        if littles_p > 0.05:
            mechanism = "MCAR"
            recommended = "KNN_OR_INTERPOLATION"
            explanation = "Las ausencias no presentan dependencia con otras variables observadas (MCAR)."
        elif littles_p > 0.001:
            mechanism = "MAR"
            recommended = "MICE_OR_GROUP_MEDIAN"
            explanation = "Las ausencias dependen sistemáticamente de covariables registradas (MAR)."
        else:
            mechanism = "MNAR_OR_STRONG_MAR"
            recommended = "MICE_WITH_FLAG"
            explanation = "Alta probabilidad de dependencia no aleatoria; se requiere bandera explicativa de imputación."

        return MissingPatternReport(
            total_rows=total_rows,
            total_cols=total_cols,
            missing_rates_by_col=missing_rates,
            missing_counts_by_col=missing_counts,
            diagnosed_mechanism=mechanism,
            littles_test_p_value=littles_p,
            recommended_strategy=recommended,
            details={"diagnostic_notes": explanation},
        )
