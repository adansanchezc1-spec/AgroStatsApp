"""
Gestor de Base de Datos y Persistencia Idempotente
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Arquitectura de Datos), ACID, SQLite/DuckDB
"""

import os
import sqlite3
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestiona conexiones SQL e inserciones/upserts de DataFrames en tablas SQLite/DuckDB."""
    
    def __init__(self, db_path: str = "data/processed/agrostats_lakehouse.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def get_connection(self):
        return sqlite3.connect(str(self.db_path))
        
    def save_dataframe(self, df: pd.DataFrame, table_name: str, mode: str = "replace") -> int:
        """Guarda un DataFrame en la base de datos SQL objetivo."""
        with self.get_connection() as conn:
            df.to_sql(table_name, conn, if_exists=mode, index=False)
            logger.info(f"Guardadas {len(df)} filas en la tabla '{table_name}' de {self.db_path.name}.")
            return len(df)
            
    def query(self, sql: str) -> pd.DataFrame:
        """Ejecuta una consulta SQL y retorna un DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(sql, conn)
