"""
Validación de Esquemas y Calidad de Datos (Quality Gates)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: ISO/IEC 25010, DAMA-DMBOK 2
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from .quality_engine import DataQualityEngine, DataQualityReport, QualityCheckResult

logger = logging.getLogger(__name__)


class QualityGateError(Exception):
    """Excepción lanzada cuando una regla crítica de calidad de datos es violada."""
    pass


class DataValidator:
    """Valida requisitos de esquema, completitud, tipos de datos, rangos y calidad multidimensional."""
    
    @staticmethod
    def validate_schema(df: pd.DataFrame, required_columns: List[str], max_null_pct: float = 0.5) -> bool:
        """Verifica que las columnas requeridas existan y que la tasa de nulos no supere el umbral máximo."""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise QualityGateError(f"Quality Gate FAILED: Faltan las siguientes columnas requeridas: {missing}")
            
        for col in required_columns:
            null_ratio = df[col].isna().mean()
            if null_ratio > max_null_pct:
                raise QualityGateError(
                    f"Quality Gate FAILED: La columna '{col}' supera el umbral de nulos ({null_ratio:.2%} > {max_null_pct:.2%})"
                )
                
        logger.info(f"Quality Gate PASSED: Esquema y nulos validados exitosamente para {len(df)} filas.")
        return True

    @staticmethod
    def evaluate_quality(
        df: pd.DataFrame,
        dataset_name: str,
        primary_keys: Optional[List[str]] = None,
        max_null_threshold: float = 0.40,
        numeric_range_rules: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> DataQualityReport:
        """Ejecuta una evaluación exhaustiva de calidad según DAMA-DMBOK 2 / ISO 25010."""
        return DataQualityEngine.evaluate(
            df=df,
            dataset_name=dataset_name,
            primary_keys=primary_keys,
            max_null_threshold=max_null_threshold,
            numeric_range_rules=numeric_range_rules
        )
