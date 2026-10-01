"""
Cargador de Archivos Heterogéneos y Tabulares (CSV, XLSX, Stata DTA, SPSS SAV, JS Store)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
"""

import os
import json
import re
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class FileLoader:
    """Carga archivos tabulares en múltiples formatos con autodetección de codificación, separador y estructura."""
    
    @staticmethod
    def load_file(file_path: str, nrows: int = 10000) -> pd.DataFrame:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        ext = path.suffix.lower()
        logger.info(f"Cargando archivo {path.name} de formato {ext} (muestra de {nrows} filas si es masivo)...")
        
        if ext == ".csv":
            # Probar separadores comunes: ',', ';', '\t'
            for sep in [",", ";", "\t", "|"]:
                try:
                    df = pd.read_csv(path, encoding="utf-8", sep=sep, nrows=nrows, on_bad_lines="skip")
                    if df.shape[1] > 1:
                        logger.info(f"CSV cargado exitosamente con separador '{sep}' y encoding UTF-8")
                        return df
                except Exception:
                    pass
            # Probar con encoding latin-1
            for sep in [";", ",", "\t", "|"]:
                try:
                    df = pd.read_csv(path, encoding="latin-1", sep=sep, nrows=nrows, on_bad_lines="skip")
                    if df.shape[1] > 1:
                        logger.info(f"CSV cargado exitosamente con separador '{sep}' y encoding latin-1")
                        return df
                except Exception:
                    pass
            # Fallback por defecto
            return pd.read_csv(path, encoding="latin-1", on_bad_lines="skip", nrows=nrows)
                
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(path, nrows=nrows)
            
        elif ext == ".parquet":
            return pd.read_parquet(path)
            
        elif ext == ".json":
            return pd.read_json(path)
            
        elif ext == ".dta":
            try:
                return pd.read_stata(path, iterator=True).read(nrows)
            except Exception as e:
                logger.warning(f"Error al leer Stata .dta: {e}")
                import pyreadstat
                df, _ = pyreadstat.read_dta(str(path), row_limit=nrows)
                return df
                
        elif ext in [".sav", ".zsav"]:
            import pyreadstat
            df, _ = pyreadstat.read_sav(str(path), row_limit=nrows)
            return df
            
        elif ext == ".js":
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r"=\s*(\[.*\]|\{.*\});?", content, re.DOTALL)
            if match:
                json_str = match.group(1)
                json_str = re.sub(r'(\w+):', r'"\1":', json_str)
                json_str = json_str.replace("'", '"')
                try:
                    data = json.loads(json_str)
                    return pd.DataFrame(data if isinstance(data, list) else [data])
                except Exception:
                    return pd.DataFrame([{"raw_content": content}])
            return pd.DataFrame([{"raw_content": content}])
            
        else:
            raise ValueError(f"Formato no soportado: {ext}")
