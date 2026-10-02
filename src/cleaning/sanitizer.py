"""
Sanitizador y Normalizador de Datos Tabulares
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: Clean Code, PEP 8, DAMA-DMBOK 2
"""

import re
import unicodedata
import logging
from typing import Optional, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataSanitizer:
    """Aplica transformaciones de limpieza: desenrollado multi-nivel, snake_case, imputación e inferencia de tipos."""
    
    @staticmethod
    def to_snake_case(name: str) -> str:
        """Convierte nombres de columnas a snake_case sin caracteres especiales ni acentos."""
        n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
        n = re.sub(r'[^\w\s]', '', n).strip().lower()
        n = re.sub(r'[\s-]+', '_', n)
        return n

    @classmethod
    def unwrap_hierarchical_headers(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta y desenrolla tablas con encabezados jerárquicos multi-nivel comunes en boletines DANE SIPSA
        (ej: Fila 1 = Mercado Mayorista con celdas combinadas, Fila 2 = Precio / Var %).
        """
        if df.empty or len(df) < 4:
            return df

        unnamed_ratio = sum(1 for c in df.columns if str(c).lower().startswith("unnamed")) / len(df.columns)
        if unnamed_ratio >= 0.70:
            for idx in range(min(5, len(df))):
                row_vals = [str(x).lower() for x in df.iloc[idx].values if pd.notna(x)]
                row_str = " ".join(row_vals)
                if "precio" in row_str and any(k in row_str for k in ["mercar", "corabastos", "cavasa", "cma", "abastos", "galer"]):
                    header_row = df.iloc[idx].ffill().fillna("")
                    sub_row = df.iloc[idx + 1].fillna("") if idx + 1 < len(df) else [""] * len(df.columns)

                    new_cols: List[str] = []
                    for i in range(len(df.columns)):
                        if i == 0:
                            new_cols.append("producto")
                        else:
                            h = cls.to_snake_case(str(header_row.iloc[i]))
                            s = cls.to_snake_case(str(sub_row.iloc[i])) if hasattr(sub_row, 'iloc') else cls.to_snake_case(str(sub_row[i]))
                            col = f"{h}_{s}".strip("_") if s else h
                            new_cols.append(col or f"col_{i}")

                    data_df = df.iloc[idx + 2:].copy()
                    data_df.columns = new_cols
                    # Filtrar filas de categorías que solo tienen texto en la primera columna
                    data_df = data_df[data_df.iloc[:, 1:].notna().any(axis=1)]
                    logger.info(f"Encabezados jerárquicos desenrollados exitosamente en {len(new_cols)} columnas.")
                    return data_df

        return df

    @classmethod
    def sanitize_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica sanitización general, desenrollado e inferencia de tipos a un DataFrame."""
        # 1. Desenrollar encabezados jerárquicos si existen
        clean_df = cls.unwrap_hierarchical_headers(df.copy())
        
        # 2. Renombrar columnas a snake_case
        clean_df.columns = [cls.to_snake_case(c) for c in clean_df.columns]
        
        # 3. Reemplazar strings vacíos o variantes de nulos por np.nan
        clean_df = clean_df.replace(r'^\s*$', np.nan, regex=True)
        clean_df = clean_df.replace(["null", "None", "nan", "NaN", "N/A", "n/a", "ND", "nd", "-", "*"], np.nan)
        
        # 4. Eliminar filas completamente vacías
        clean_df = clean_df.dropna(how="all")
        
        # Eliminar columnas unnamed que superen el 80% de nulos
        unnamed_cols = [c for c in clean_df.columns if c.startswith("unnamed") and clean_df[c].isna().mean() > 0.8]
        if unnamed_cols:
            clean_df = clean_df.drop(columns=unnamed_cols)

        # 5. Inferencia y casteo automático de tipos numéricos
        for col in clean_df.columns:
            if not pd.api.types.is_numeric_dtype(clean_df[col]) and not pd.api.types.is_datetime64_any_dtype(clean_df[col]):
                if not any(k in col for k in ["fecha", "date", "periodo", "nombre", "producto", "municipio", "departamento", "fuente", "grupo", "ali"]):
                    non_null = clean_df[col].dropna().astype(str).str.strip()
                    if len(non_null) > 0:
                        clean_str = non_null.str.replace(r'[\$,]', '', regex=True)
                        num_series = pd.to_numeric(clean_str, errors="coerce")
                        if num_series.notna().mean() >= 0.70:
                            clean_df[col] = pd.to_numeric(
                                clean_df[col].astype(str).str.replace(r'[\$,]', '', regex=True),
                                errors="coerce"
                            )
            
        logger.info(f"DataFrame sanitizado. Dimensiones: {clean_df.shape}")
        return clean_df
