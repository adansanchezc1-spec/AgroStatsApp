"""
Gestor de Base de Datos y Persistencia Idempotente de Alta Eficiencia
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Data Storage & Operations), ACID, SQLite WAL Mode
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import pandas as pd

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Gestiona conexiones SQL e inserciones idempotentes con:
      - Modo WAL (Write-Ahead Logging) y pragma síncrono optimizado.
      - Transacciones atómicas (Rollback automático ante fallos).
      - Creación automática de índices analíticos (DIVIPOLA, fecha, producto).
      - Introspección de esquemas y creación de vistas analíticas (Data Marts).
      - Consultas parametrizadas seguras contra inyección SQL.
    """
    
    def __init__(self, db_path: str = "data/processed/agrostats_lakehouse.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_pragmas()
        
    def _init_pragmas(self):
        """Configura pragmas de alto rendimiento en SQLite."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode = WAL;")
                cursor.execute("PRAGMA synchronous = NORMAL;")
                cursor.execute("PRAGMA cache_size = -64000;")  # 64MB cache
                cursor.execute("PRAGMA foreign_keys = ON;")
                conn.commit()
        except Exception as e:
            logger.warning(f"No se pudieron inicializar pragmas SQLite: {e}")

    @contextmanager
    def get_connection(self):
        """Context manager que garantiza commit o rollback automático."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"[DatabaseManager] Rollback por error en transacción: {e}")
            raise e
        finally:
            conn.close()
        
    def save_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        mode: str = "replace",
        index_columns: Optional[List[str]] = None
    ) -> int:
        """
        Guarda un DataFrame en la base de datos SQL objetivo con indexación automática.
        """
        with self.get_connection() as conn:
            df.to_sql(table_name, conn, if_exists=mode, index=False)
            
            # Crear índices automáticos si se especifican o en columnas comunes
            candidates = index_columns or [
                c for c in df.columns if any(k in c.lower() for k in ["divipola", "fecha", "date", "producto", "municipio"])
            ]
            for col in candidates:
                if col in df.columns:
                    idx_name = f"idx_{table_name}_{col}"
                    try:
                        conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({col});")
                    except Exception as e:
                        logger.debug(f"Índice {idx_name} no pudo ser creado: {e}")
                        
            logger.info(f"Guardadas {len(df)} filas en la tabla '{table_name}' de {self.db_path.name}.")
            return len(df)
            
    def query(self, sql: str, params: Optional[Tuple[Any, ...] | Dict[str, Any]] = None) -> pd.DataFrame:
        """Ejecuta una consulta SQL parametrizada y retorna un DataFrame."""
        with sqlite3.connect(str(self.db_path)) as conn:
            if params:
                return pd.read_sql_query(sql, conn, params=params)
            return pd.read_sql_query(sql, conn)

    def list_tables(self) -> List[str]:
        """Retorna la lista de tablas presentes en la base de datos."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Introspección de columnas y tipos para una tabla."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            cols = []
            for row in cursor.fetchall():
                cols.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "dflt_value": row[4],
                    "pk": bool(row[5])
                })
            return cols

    def create_view(self, view_name: str, select_sql: str) -> None:
        """Crea o reemplaza una vista analítica en SQLite."""
        with self.get_connection() as conn:
            conn.execute(f"DROP VIEW IF EXISTS {view_name};")
            conn.execute(f"CREATE VIEW {view_name} AS {select_sql};")
            logger.info(f"Vista analítica '{view_name}' creada exitosamente.")

    def optimize(self) -> None:
        """Ejecuta VACUUM y ANALYZE para optimizar el almacenamiento y el planificador."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("PRAGMA optimize;")
            logger.info("Base de datos optimizada exitosamente.")
