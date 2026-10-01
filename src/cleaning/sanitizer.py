"""
Sanitizador y Normalizador de Datos Tabulares
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: Clean Code, PEP 8, DAMA-DMBOK 2
"""

import re
import unicodedata
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DataSanitizer:
    """Aplica transformaciones de limpieza: renombrado snake_case, imputación de nulos y casteo de tipos."""
    
    @staticmethod
    def to_snake_case(name: str) -> str:
        """Convierte nombres de columnas a snake_case sin caracteres especiales ni acentos."""
        n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
        n = re.sub(r'[^\w\s]', '', n).strip().lower()
        n = re.sub(r'[\s-]+', '_', n)
        return n

    @classmethod
    def sanitize_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica sanitización general a un DataFrame de pandas."""
        clean_df = df.copy()
        
        # 1. Renombrar columnas a snake_case
        clean_df.columns = [cls.to_snake_case(c) for c in clean_df.columns]
        
        # 2. Reemplazar strings vacíos o "null", "none", "nan" por np.nan
        clean_df = clean_df.replace(r'^\s*$', np.nan, regex=True)
        clean_df = clean_df.replace(["null", "None", "nan", "NaN", "N/A"], np.nan)
        
        # 3. Eliminar filas y columnas completamente vacías o columnas unnamed mayoritariamente nulas
        clean_df = clean_df.dropna(how="all")
        
        # Eliminar columnas unnamed que superen el 80% de nulos
        unnamed_cols = [c for c in clean_df.columns if c.startswith("unnamed") and clean_df[c].isna().mean() > 0.8]
        if unnamed_cols:
            clean_df = clean_df.drop(columns=unnamed_cols)
            
        logger.info(f"DataFrame sanitizado. Dimensiones: {clean_df.shape}")
        return clean_df
