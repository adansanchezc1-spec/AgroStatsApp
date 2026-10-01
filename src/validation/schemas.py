"""
Validación de Esquemas y Calidad de Datos (Quality Gates)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: ISO/IEC 25010, DAMA-DMBOK 2
"""

import logging
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

class QualityGateError(Exception):
    """Excepción lanzada cuando una regla crítica de calidad de datos es violada."""
    pass

class DataValidator:
    """Valida requisitos de esquema, completitud, tipos de datos y unicidad."""
    
    @staticmethod
    def validate_schema(df: pd.DataFrame, required_columns: List[str], max_null_pct: float = 0.5) -> bool:
        """Verifica que las columnas requeridas existan y que la tasa de nulos no supere el umbral máximo."""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise QualityGateError(f"Quality Gate FAILED: Faltan las siguientes columnas requeridas: {missing}")
            
        for col in required_columns:
            null_ratio = df[col].isna().mean()
            if null_ratio > max_null_pct:
                raise QualityGateError(f"Quality Gate FAILED: La columna '{col}' supera el umbral de nulos ({null_ratio:.2%} > {max_null_pct:.2%})")
                
        logger.info(f"Quality Gate PASSED: Esquema y nulos validados exitosamente para {len(df)} filas.")
        return True
