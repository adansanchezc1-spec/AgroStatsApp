"""
Motor Inteligente de Imputación Competitiva con Preservación de Varianza
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: Rubin Framework, ISO 25010 (Calidad y Linaje), DAMA-DMBOK 2
"""

from dataclasses import dataclass, field
import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from .rubin_diagnostics import RubinDiagnostics, MissingPatternReport
from .algorithms import (
    BaseImputerAlgorithm,
    TimeInterpolationImputer,
    SpatialKnnImputer,
    MiceIterativeImputer,
    ConditionalGroupMedianImputer,
)

logger = logging.getLogger(__name__)


@dataclass
class ImputationBenchmarkResult:
    """
    Resultado del torneo competitivo entre algoritmos de imputación.
    """
    winning_algorithm_name: str
    winning_score: float
    scores_by_algorithm: Dict[str, float]
    diagnostics: MissingPatternReport
    imputed_dataframe: pd.DataFrame
    audit_flags_injected: List[str] = field(default_factory=list)


class IntelligentImputer:
    """
    Orquestador de imputación inteligente: diagnostica el mecanismo de pérdida,
    ejecuta un benchmark competitivo evaluando error cuadrático y distorsión de varianza,
    y entrega el dataset curado con banderas de auditoría DAMA.
    """

    def __init__(
        self,
        variance_penalty_weight: float = 1.5,
        group_keys: Optional[List[str]] = None,
    ) -> None:
        self.variance_penalty_weight = variance_penalty_weight
        self.group_keys = group_keys or ["cod_municipio", "departamento", "producto"]

    def _evaluate_algorithm_score(
        self,
        algorithm: BaseImputerAlgorithm,
        sample_df: pd.DataFrame,
        numeric_cols: List[str],
    ) -> float:
        """
        Evalúa un algoritmo mediante simulación de máscara de pérdida sobre datos observados.
        Calcula: Score = RMSE * (1 + |1 - Var_imp / Var_orig| * penalty)
        """
        complete_df = sample_df[numeric_cols].dropna()
        if len(complete_df) < 10:
            return 9999.0

        # Crear máscara artificial del 15% de ausencias
        rng = np.random.default_rng(42)
        mask = rng.random(size=complete_df.shape) < 0.15
        if not mask.any():
            return 1.0

        corrupted_df = complete_df.copy()
        corrupted_df[mask] = np.nan

        try:
            imputed_df = algorithm.fit_transform(corrupted_df, target_columns=numeric_cols)
            true_vals = complete_df.values[mask]
            imp_vals = imputed_df.values[mask]

            # Reemplazar posibles nulos no completados
            if np.isnan(imp_vals).any():
                imp_vals = np.nan_to_num(imp_vals, nan=np.nanmean(true_vals))

            rmse = float(np.sqrt(np.mean((true_vals - imp_vals) ** 2)))

            # Ratio de varianza
            orig_var = float(np.var(true_vals)) + 1e-9
            imp_var = float(np.var(imp_vals)) + 1e-9
            var_distortion = abs(1.0 - (imp_var / orig_var))

            final_score = rmse * (1.0 + var_distortion * self.variance_penalty_weight)
            return float(final_score)
        except Exception as exc:
            logger.debug("Algoritmo %s falló en evaluación sintética: %s", algorithm.name, exc)
            return 99999.0

    def fit_impute(
        self,
        df: pd.DataFrame,
        inject_audit_flags: bool = True,
        target_columns: Optional[List[str]] = None,
    ) -> ImputationBenchmarkResult:
        """
        Punto de entrada principal: diagnostica, compite y genera el dataset imputado.
        """
        diagnostics = RubinDiagnostics.inspect(df)
        numeric_cols = target_columns or df.select_dtypes(include=[np.number]).columns.tolist()

        if diagnostics.diagnosed_mechanism == "COMPLETE_DATA" or not numeric_cols:
            return ImputationBenchmarkResult(
                winning_algorithm_name="NO_IMPUTATION_NEEDED",
                winning_score=0.0,
                scores_by_algorithm={},
                diagnostics=diagnostics,
                imputed_dataframe=df.copy(),
                audit_flags_injected=[],
            )

        # Definición de la batería de algoritmos candidatos
        candidates: List[BaseImputerAlgorithm] = [
            TimeInterpolationImputer(method="linear"),
            SpatialKnnImputer(n_neighbors=5),
            MiceIterativeImputer(max_iter=10),
            ConditionalGroupMedianImputer(group_columns=self.group_keys),
        ]

        # Torneo competitivo
        scores: Dict[str, float] = {}
        for algo in candidates:
            score = self._evaluate_algorithm_score(algo, df, numeric_cols)
            scores[algo.name] = score
            logger.info("Benchmark Imputación [%s]: Score = %.4f", algo.name, score)

        winning_algo = min(candidates, key=lambda a: scores.get(a.name, 999999.0))
        winning_score = scores[winning_algo.name]
        logger.info("Algoritmo ganador seleccionado: %s (Score: %.4f)", winning_algo.name, winning_score)

        # Registro de qué celdas eran nulas originalmente
        missing_mask_dict = {col: df[col].isna() for col in numeric_cols if df[col].isna().any()}

        # Aplicar el algoritmo ganador al dataset completo
        imputed_df = winning_algo.fit_transform(df, target_columns=numeric_cols)

        # Inyectar banderas de trazabilidad DAMA
        injected_flags: List[str] = []
        if inject_audit_flags:
            for col, mask in missing_mask_dict.items():
                flag_col = f"{col}_is_imputed"
                imputed_df[flag_col] = mask
                injected_flags.append(flag_col)

            imputed_df["_impute_method"] = winning_algo.name
            injected_flags.append("_impute_method")

        return ImputationBenchmarkResult(
            winning_algorithm_name=winning_algo.name,
            winning_score=winning_score,
            scores_by_algorithm=scores,
            diagnostics=diagnostics,
            imputed_dataframe=imputed_df,
            audit_flags_injected=injected_flags,
        )
