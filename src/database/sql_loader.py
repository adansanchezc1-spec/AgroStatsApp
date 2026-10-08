"""Cargador Masivo de Datos y Mapeo Dimensional (SQL Loader).
Fase PDCO: DEVELOPMENT | Estándar: Ralph Kimball / Clean Architecture
Carga transaccional e idempotente de dimensiones y tablas de hechos en el modelo estrella.
"""

from __future__ import annotations
import sqlite3
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.database.db_manager import DatabaseManager
from src.utils.logger import get_logger
from src.cleaning.transformers import sanitize_text

logger = get_logger("database.sql_loader")


class SQLLoader:
    """Orquestador de carga masiva de dimensiones y hechos en el modelo estrella relacional."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def load_dim_tiempo(self, start_year: int = 2015, end_year: int = 2026) -> int:
        """Puebla de forma determinística la dimensión tiempo por mes."""
        records = []
        for anio in range(start_year, end_year + 1):
            for mes in range(1, 13):
                id_tiempo = anio * 100 + mes
                trimestre = (mes - 1) // 3 + 1
                semestre = (mes - 1) // 6 + 1
                records.append((id_tiempo, anio, mes, trimestre, semestre))

        sql = """
        INSERT OR IGNORE INTO dim_tiempo (id_tiempo, anio, mes, trimestre, semestre)
        VALUES (?, ?, ?, ?, ?)
        """
        con = sqlite3.connect(str(self.db.db_file))
        try:
            cur = con.cursor()
            cur.executemany(sql, records)
            con.commit()
            count = cur.rowcount
            logger.info("dim_tiempo poblada con %d períodos mensuales", len(records))
            return len(records)
        finally:
            con.close()

    def load_dim_municipio(self, df_municipios: pd.DataFrame) -> int:
        """Carga el catálogo de municipios en dim_municipio."""
        if df_municipios.empty:
            return 0

        records = []
        for _, row in df_municipios.iterrows():
            cod_mun = str(row.get("cod_municipio", "")).strip().zfill(5)
            cod_dep = str(row.get("cod_departamento", "")).strip().zfill(2)
            nom_mun = sanitize_text(row.get("nombre_municipio", ""))
            nom_dep = sanitize_text(row.get("nombre_departamento", ""))
            if cod_mun and nom_mun:
                records.append((cod_mun, cod_dep, nom_mun, nom_dep))

        sql = """
        INSERT OR REPLACE INTO dim_municipio (cod_municipio, cod_departamento, nombre_municipio, nombre_departamento)
        VALUES (?, ?, ?, ?)
        """
        con = sqlite3.connect(str(self.db.db_file))
        try:
            cur = con.cursor()
            cur.executemany(sql, records)
            con.commit()
            logger.info("dim_municipio actualizada con %d registros", len(records))
            return len(records)
        finally:
            con.close()

    def get_or_create_producto(
        self,
        nombre: str,
        variedad: str = "SIN_VARIEDAD_ESPECIFICADA",
        grupo: str = "",
    ) -> int:
        """Resuelve o inserta un producto en dim_producto y retorna su id_producto."""
        norm_nombre = sanitize_text(nombre)
        norm_variedad = sanitize_text(variedad) or "SIN_VARIEDAD_ESPECIFICADA"
        norm_grupo = sanitize_text(grupo)

        con = sqlite3.connect(str(self.db.db_file))
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT id_producto FROM dim_producto WHERE nombre_producto = ? AND variedad = ?",
                (norm_nombre, norm_variedad),
            )
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute(
                "INSERT INTO dim_producto (nombre_producto, grupo_cultivo, variedad) VALUES (?, ?, ?)",
                (norm_nombre, norm_grupo, norm_variedad),
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def get_or_create_insumo(self, nombre: str, categoria: str = "") -> int:
        """Resuelve o inserta un insumo en dim_insumo y retorna su id_insumo."""
        norm_nombre = sanitize_text(nombre)
        norm_categoria = sanitize_text(categoria)

        con = sqlite3.connect(str(self.db.db_file))
        try:
            cur = con.cursor()
            cur.execute("SELECT id_insumo FROM dim_insumo WHERE nombre_insumo = ?", (norm_nombre,))
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute(
                "INSERT INTO dim_insumo (nombre_insumo, categoria_insumo) VALUES (?, ?)",
                (norm_nombre, norm_categoria),
            )
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def load_fact_eva(self, df_eva: pd.DataFrame) -> int:
        """Carga registros agrícolas en fact_produccion_eva."""
        if df_eva.empty:
            return 0

        con = sqlite3.connect(str(self.db.db_file))
        inserted = 0
        try:
            cur = con.cursor()
            for _, row in df_eva.iterrows():
                anio = int(row.get("anio", 2022))
                id_tiempo = anio * 100 + 12  # Cierre anual de EVA en mes 12
                cod_mun = str(row.get("cod_municipio", "")).strip().zfill(5)
                prod_name = str(row.get("cultivo", ""))
                variedad = str(row.get("variedad", "SIN_VARIEDAD_ESPECIFICADA"))
                grupo = str(row.get("grupo_de_cultivo", ""))

                id_prod = self.get_or_create_producto(prod_name, variedad, grupo)

                cur.execute(
                    """
                    INSERT INTO fact_produccion_eva 
                    (id_tiempo, cod_municipio, id_producto, area_sembrada_ha, area_cosechada_ha, produccion_ton, rendimiento_ton_ha)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        id_tiempo,
                        cod_mun,
                        id_prod,
                        float(row.get("area_sembrada_ha", 0.0) or 0.0),
                        float(row.get("area_cosechada_ha", 0.0) or 0.0),
                        float(row.get("produccion_ton", 0.0) or 0.0),
                        float(row.get("rendimiento_ton_ha", 0.0) or 0.0),
                    ),
                )
                inserted += 1

            con.commit()
            logger.info("fact_produccion_eva cargada con %d registros", inserted)
            return inserted
        finally:
            con.close()
