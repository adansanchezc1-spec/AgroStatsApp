"""Administrador de Conexiones y Esquemas de Base de Datos.
Fase PDCO: DEVELOPMENT | Estándar: Ralph Kimball / Clean Architecture
Soporte dual SQLite / DuckDB para almacenamiento OLAP local de alto rendimiento.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional, Union
import pandas as pd

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("database.db_manager")

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False


class DatabaseManager:
    """Gestor de base de datos relacional para el esquema dimensional."""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        use_duckdb: bool = False,
    ) -> None:
        self.db_dir = settings.DATABASE_DIR
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.use_duckdb = use_duckdb and HAS_DUCKDB

        if self.use_duckdb:
            self.db_file = db_path or (self.db_dir / "agrostats_olap.duckdb")
        else:
            self.db_file = db_path or (self.db_dir / "agrostats_relational.sqlite3")

    def initialize_schema(self, ddl_path: Optional[Path] = None) -> None:
        """Aplica el archivo de DDL para crear tablas, dimensiones, hechos y vistas."""
        schema_file = ddl_path or (Path(__file__).parent / "ddl_schema.sql")
        if not schema_file.exists():
            raise FileNotFoundError(f"Archivo DDL no encontrado: {schema_file}")

        with open(schema_file, "r", encoding="utf-8") as f:
            ddl_sql = f.read()

        if self.use_duckdb:
            con = duckdb.connect(str(self.db_file))
            try:
                # Filtrar comandos específicos de SQLite que DuckDB no usa (como PRAGMA foreign_keys)
                clean_statements = [
                    stmt.strip() for stmt in ddl_sql.split(";") 
                    if stmt.strip() and not stmt.strip().upper().startswith("PRAGMA")
                ]
                for stmt in clean_statements:
                    con.execute(stmt)
                logger.info("Esquema relacional inicializado exitosamente en DuckDB: %s", self.db_file)
            finally:
                con.close()
        else:
            con = sqlite3.connect(str(self.db_file))
            try:
                con.executescript(ddl_sql)
                con.commit()
                logger.info("Esquema relacional inicializado exitosamente en SQLite: %s", self.db_file)
            finally:
                con.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Ejecuta una consulta SQL y retorna los resultados como un DataFrame de Pandas."""
        if self.use_duckdb:
            con = duckdb.connect(str(self.db_file))
            try:
                if params:
                    return con.execute(query, params).df()
                return con.execute(query).df()
            finally:
                con.close()
        else:
            con = sqlite3.connect(str(self.db_file))
            try:
                return pd.read_sql_query(query, con, params=params)
            finally:
                con.close()

    def execute_statement(self, statement: str, params: Optional[tuple] = None) -> int:
        """Ejecuta una sentencia de inserción, actualización o eliminación."""
        con = sqlite3.connect(str(self.db_file))
        try:
            cur = con.cursor()
            if params:
                cur.execute(statement, params)
            else:
                cur.execute(statement)
            con.commit()
            return cur.rowcount
        finally:
            con.close()
