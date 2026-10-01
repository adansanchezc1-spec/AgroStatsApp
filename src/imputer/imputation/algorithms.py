"""
Algoritmos de Imputación Multivariada y Geoespacial
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: PEP 8, GoF Strategy Pattern, Scikit-Learn Estimator API
"""

from abc import ABC, abstractmethod
import logging
from typing import List, Optional
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

# Habilitar IterativeImputer experimental en scikit-learn
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

logger = logging.getLogger(__name__)


class BaseImputerAlgorithm(ABC):
    """
    Estrategia base abstracta para cualquier algoritmo de imputación.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def fit_transform(self, df: pd.DataFrame, target_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Aplica la imputación y retorna un DataFrame con los valores completados.
        """
        pass


class TimeInterpolationImputer(BaseImputerAlgorithm):
    """
    Imputación temporal mediante interpolación continua (Lineal, Spline o PCHIP).
    Ideal para series climáticas de alta frecuencia (precipitación, temperatura) o precios diarios.
    """

    def __init__(self, method: str = "linear", order: int = 2) -> None:
        super().__init__(name=f"Interpolation_{method}")
        self.method = method
        self.order = order

    def fit_transform(self, df: pd.DataFrame, target_columns: Optional[List[str]] = None) -> pd.DataFrame:
        result_df = df.copy()
        cols = target_columns or result_df.select_dtypes(include=[np.number]).columns.tolist()

        for col in cols:
            if result_df[col].isna().any():
                try:
                    if self.method == "spline":
                        interpolated = result_df[col].interpolate(
                            method="spline", order=self.order, limit_direction="both"
                        )
                    else:
                        interpolated = result_df[col].interpolate(
                            method=self.method, limit_direction="both"
                        )
                    # Completar bordes extremos si quedan residuales
                    result_df[col] = interpolated.bfill().ffill()
                except Exception as exc:
                    logger.debug("Fallback en interpolación para %s: %s", col, exc)
                    result_df[col] = result_df[col].bfill().ffill()

        return result_df


class SpatialKnnImputer(BaseImputerAlgorithm):
    """
    Imputación K-Nearest Neighbors ponderada por distancia en el espacio multivariado.
    Adecuado para estaciones meteorológicas vecinas o atributos municipales.
    """

    def __init__(self, n_neighbors: int = 5, weights: str = "distance") -> None:
        super().__init__(name=f"KNN_k{n_neighbors}")
        self.n_neighbors = n_neighbors
        self.weights = weights

    def fit_transform(self, df: pd.DataFrame, target_columns: Optional[List[str]] = None) -> pd.DataFrame:
        result_df = df.copy()
        num_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()

        if not num_cols or not result_df[num_cols].isna().any().any():
            return result_df

        # Adaptar n_neighbors si el número de muestras es menor
        valid_rows = len(result_df)
        k = min(self.n_neighbors, max(1, valid_rows - 1))

        imputer = KNNImputer(n_neighbors=k, weights=self.weights)
        imputed_array = imputer.fit_transform(result_df[num_cols])

        cols_to_update = target_columns if target_columns else num_cols
        for i, col in enumerate(num_cols):
            if col in cols_to_update:
                result_df[col] = imputed_array[:, i]

        return result_df


class MiceIterativeImputer(BaseImputerAlgorithm):
    """
    Imputación MICE (Multiple Imputation by Chained Equations) vía Bayesian Ridge.
    Preserva las relaciones de covarianza y correlación entre variables económicas y biofísicas.
    """

    def __init__(self, max_iter: int = 10, random_state: int = 42) -> None:
        super().__init__(name="MICE_BayesianRidge")
        self.max_iter = max_iter
        self.random_state = random_state

    def fit_transform(self, df: pd.DataFrame, target_columns: Optional[List[str]] = None) -> pd.DataFrame:
        result_df = df.copy()
        num_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()

        if not num_cols or not result_df[num_cols].isna().any().any():
            return result_df

        estimator = BayesianRidge()
        imputer = IterativeImputer(
            estimator=estimator,
            max_iter=self.max_iter,
            random_state=self.random_state,
            initial_strategy="median",
            skip_complete=True,
        )
        imputed_array = imputer.fit_transform(result_df[num_cols])

        cols_to_update = target_columns if target_columns else num_cols
        for i, col in enumerate(num_cols):
            if col in cols_to_update:
                result_df[col] = imputed_array[:, i]

        return result_df


class ConditionalGroupMedianImputer(BaseImputerAlgorithm):
    """
    Imputación por mediana condicional jerárquica basada en factores de agrupación
    (ej. por 'cod_municipio', 'departamento' o 'producto_cpc').
    """

    def __init__(self, group_columns: List[str]) -> None:
        super().__init__(name="ConditionalGroupMedian")
        self.group_columns = group_columns

    def fit_transform(self, df: pd.DataFrame, target_columns: Optional[List[str]] = None) -> pd.DataFrame:
        result_df = df.copy()
        existing_groups = [g for g in self.group_columns if g in result_df.columns]
        num_cols = target_columns or result_df.select_dtypes(include=[np.number]).columns.tolist()

        if not existing_groups or not num_cols:
            # Fallback a mediana global
            for col in num_cols:
                median_val = result_df[col].median()
                result_df[col] = result_df[col].fillna(median_val)
            return result_df

        for col in num_cols:
            if result_df[col].isna().any():
                # Mediana por grupo jerárquico
                group_medians = result_df.groupby(existing_groups)[col].transform("median")
                result_df[col] = result_df[col].fillna(group_medians)
                # Fallback residual global si todo el grupo era nulo
                global_median = result_df[col].median()
                result_df[col] = result_df[col].fillna(global_median)

        return result_df
