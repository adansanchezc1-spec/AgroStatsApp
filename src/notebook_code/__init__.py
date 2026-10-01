"""
Paquete Integral de Utilidades y Algoritmos para el Ciclo CRISP-DM
==================================================================
Proporciona la arquitectura modular de software para todas las fases de
investigación de AgroStatsApp: Carga Cruda, Perfilamiento, Imputación,
EDA, Gestión de Datos Maestros (MDM), Feature Engineering, ML y Evaluación.

Exporta:
- Ingesta y Perfilamiento: `RawDataLoader`, `DatasetProfiler`, `find_raw_data_dir`
- Imputación Inteligente: `NotebookImputerBridge`
- Análisis Exploratorio (EDA): `EdaAnalyzer`
- Datos Maestros y Entidades: `MasterDataManager`
- Limpieza y Features: `FeatureEngineer`
- Entrenamiento y Torneo ML: `ModelTrainer`
- Evaluación e Inferencia: `ModelEvaluator`, `InferenceService`
- Helpers funcionales: `load_raw_dataset`, `load_all_raw_datasets`, `explore_dataset`
"""

from typing import Any, Dict
import pandas as pd

from .data_loader import (
    RawDataLoader,
    find_raw_data_dir,
    CleanDataLoader,
    find_cleaned_data_dir,
    load_cleaned_dataset,
    load_all_cleaned_datasets,
)
from .data_profiler import DatasetProfiler
from .eda_analyzer import EdaAnalyzer
from .feature_engineer import FeatureEngineer
from .imputer_helper import NotebookImputerBridge
from .mdm_manager import MasterDataManager
from .ml_trainer import ModelTrainer
from .model_evaluator import InferenceService, ModelEvaluator


def load_raw_dataset(dataset_id: str, clean_column_names: bool = True) -> pd.DataFrame:
    """Función de una sola línea para cargar un dataset de data/RAW por su ID."""
    loader = RawDataLoader()
    return loader.load_dataset(dataset_id, clean_column_names=clean_column_names)


def load_all_raw_datasets() -> Dict[str, pd.DataFrame]:
    """Carga todos los datasets disponibles en data/RAW en un diccionario."""
    loader = RawDataLoader()
    return loader.load_all_datasets()


def explore_dataset(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """Genera el diagnóstico informático completo para un DataFrame."""
    return DatasetProfiler.inspect(df, dataset_name=dataset_name)


__all__ = [
    "RawDataLoader",
    "CleanDataLoader",
    "DatasetProfiler",
    "NotebookImputerBridge",
    "EdaAnalyzer",
    "MasterDataManager",
    "FeatureEngineer",
    "ModelTrainer",
    "ModelEvaluator",
    "InferenceService",
    "find_raw_data_dir",
    "find_cleaned_data_dir",
    "load_raw_dataset",
    "load_all_raw_datasets",
    "load_cleaned_dataset",
    "load_all_cleaned_datasets",
    "explore_dataset",
]