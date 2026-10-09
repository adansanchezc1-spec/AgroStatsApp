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
        con = sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")
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
        con = sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")
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
        conn: Optional[sqlite3.Connection] = None,
    ) -> int:
        """Resuelve o inserta un producto en dim_producto y retorna su id_producto."""
        norm_nombre = sanitize_text(nombre)
        norm_variedad = sanitize_text(variedad) or "SIN_VARIEDAD_ESPECIFICADA"
        norm_grupo = sanitize_text(grupo)

        own_conn = conn is None
        con = conn or sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")
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
            if own_conn:
                con.commit()
            return cur.lastrowid
        finally:
            if own_conn:
                con.close()

    def get_or_create_insumo(
        self,
        nombre: str,
        categoria: str = "",
        conn: Optional[sqlite3.Connection] = None,
    ) -> int:
        """Resuelve o inserta un insumo en dim_insumo y retorna su id_insumo."""
        norm_nombre = sanitize_text(nombre)
        norm_categoria = sanitize_text(categoria)

        own_conn = conn is None
        con = conn or sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")
            cur.execute("SELECT id_insumo FROM dim_insumo WHERE nombre_insumo = ?", (norm_nombre,))
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute(
                "INSERT INTO dim_insumo (nombre_insumo, categoria_insumo) VALUES (?, ?)",
                (norm_nombre, norm_categoria),
            )
            if own_conn:
                con.commit()
            return cur.lastrowid
        finally:
            if own_conn:
                con.close()

    def load_fact_eva(self, df_eva: pd.DataFrame) -> int:
        """Carga registros agrícolas en fact_produccion_eva de forma atómica y eficiente."""
        if df_eva.empty:
            return 0

        # Paso 1: Pre-resolver catálogo de productos en memoria para evitar contención de bloqueos
        prod_cache: Dict[Tuple[str, str], int] = {}
        unique_prods = df_eva[["cultivo", "variedad", "grupo_de_cultivo"]].drop_duplicates() if "grupo_de_cultivo" in df_eva.columns else df_eva[["cultivo", "variedad"]].drop_duplicates()

        for _, prow in unique_prods.iterrows():
            p_name = str(prow.get("cultivo", ""))
            p_var = str(prow.get("variedad", "SIN_VARIEDAD_ESPECIFICADA"))
            p_grp = str(prow.get("grupo_de_cultivo", ""))
            key = (sanitize_text(p_name), sanitize_text(p_var) or "SIN_VARIEDAD_ESPECIFICADA")
            if key not in prod_cache:
                prod_cache[key] = self.get_or_create_producto(p_name, p_var, p_grp)

        # Paso 2: Carga en lote de fact_produccion_eva dentro de una única conexión
        con = sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")
            
            fact_rows = []
            for _, row in df_eva.iterrows():
                anio = int(row.get("anio", 2022))
                id_tiempo = anio * 100 + 12  # Cierre anual de EVA en mes 12
                cod_mun = str(row.get("cod_municipio", "")).strip().zfill(5)
                prod_name = str(row.get("cultivo", ""))
                variedad = str(row.get("variedad", "SIN_VARIEDAD_ESPECIFICADA"))
                
                key = (sanitize_text(prod_name), sanitize_text(variedad) or "SIN_VARIEDAD_ESPECIFICADA")
                id_prod = prod_cache.get(key, 1)

                fact_rows.append((
                    id_tiempo,
                    cod_mun,
                    id_prod,
                    float(row.get("area_sembrada_ha", 0.0) or 0.0),
                    float(row.get("area_cosechada_ha", 0.0) or 0.0),
                    float(row.get("produccion_ton", 0.0) or 0.0),
                    float(row.get("rendimiento_ton_ha", 0.0) or 0.0),
                ))

            cur.executemany(
                """
                INSERT INTO fact_produccion_eva 
                (id_tiempo, cod_municipio, id_producto, area_sembrada_ha, area_cosechada_ha, produccion_ton, rendimiento_ton_ha)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                fact_rows,
            )
            con.commit()
            inserted = len(fact_rows)
            logger.info("fact_produccion_eva cargada con %d registros", inserted)
            return inserted
        finally:
            con.close()

    def load_fact_sipsa(self, df_sipsa: pd.DataFrame, cod_municipio: str = "11001") -> int:
        """Carga series de precios e índices de insumos SIPSA en fact_precios_sipsa."""
        if df_sipsa.empty:
            return 0

        date_col = "fecha" if "fecha" in df_sipsa.columns else "fecha_observacion"
        if date_col not in df_sipsa.columns:
            return 0

        con = sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")

            numeric_cols = [c for c in df_sipsa.columns if c not in {date_col, "anio", "mes", "fecha_corte"}]
            insumo_cache = {}
            for col in numeric_cols:
                nom = col.replace("_", " ").title()
                cat = "Fertilizantes" if any(w in col for w in ["fertilizante", "urea", "dap", "kcl", "sam"]) else "Insumos"
                insumo_cache[col] = self.get_or_create_insumo(nom, cat, conn=con)

            records = []
            for _, row in df_sipsa.iterrows():
                dt = pd.to_datetime(row[date_col], errors="coerce")
                if pd.isna(dt):
                    continue
                id_tiempo = int(dt.year * 100 + dt.month)
                for col in numeric_cols:
                    val = row.get(col)
                    if pd.notna(val) and val is not None:
                        val_num = float(val)
                        if val_num > 0:
                            id_ins = insumo_cache[col]
                            records.append((id_tiempo, cod_municipio, id_ins, val_num))

            cur.executemany(
                """
                INSERT INTO fact_precios_sipsa (id_tiempo, cod_municipio, id_insumo, precio_promedio)
                VALUES (?, ?, ?, ?)
                """,
                records,
            )
            con.commit()
            logger.info("fact_precios_sipsa cargada con %d registros", len(records))
            return len(records)
        finally:
            con.close()

    def load_fact_clima(self, df_clima: pd.DataFrame, default_cod_mun: str = "11001") -> int:
        """Carga observaciones meteorológicas (IDEAM) en fact_clima_ideam."""
        if df_clima.empty:
            return 0

        date_col = "fecha_observacion" if "fecha_observacion" in df_clima.columns else "fecha"
        if date_col not in df_clima.columns:
            return 0

        con = sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")

            records = []
            for _, row in df_clima.iterrows():
                dt = pd.to_datetime(row[date_col], errors="coerce")
                if pd.isna(dt):
                    continue
                id_tiempo = int(dt.year * 100 + dt.month)
                estacion = str(row.get("codigo_estacion", row.get("codigoestacion", "EST_GENERICA")))
                cod_mun = str(row.get("cod_municipio", default_cod_mun)).strip().zfill(5)
                val_obs = float(row.get("valor_observado", row.get("precipitacion_mm", 0.0)) or 0.0)

                desc = str(row.get("sensor_descripcion", "")).upper()
                precip = val_obs if "PRECIP" in desc or "PLUV" in desc else None
                temp = val_obs if "TEMP" in desc else None
                spi = float(row["spi_3"]) if "spi_3" in row and pd.notna(row["spi_3"]) else None
                z_temp = float(row["anomalia_termica_z"]) if "anomalia_termica_z" in row and pd.notna(row["anomalia_termica_z"]) else None

                records.append((id_tiempo, cod_mun, estacion, precip, temp, spi, z_temp))

            cur.executemany(
                """
                INSERT INTO fact_clima_ideam 
                (id_tiempo, cod_municipio, codigo_estacion, precipitacion_mensual_mm, temperatura_media_c, spi_3, anomalia_termica_z)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                records,
            )
            con.commit()
            logger.info("fact_clima_ideam cargada con %d registros", len(records))
            return len(records)
        finally:
            con.close()

    def load_mart_hypothesis(self, df_mart: pd.DataFrame) -> int:
        """Carga el Data Mart de inferencia estadística en mart_hypothesis_tests."""
        if df_mart.empty:
            return 0

        con = sqlite3.connect(str(self.db.db_file), timeout=30.0)
        try:
            cur = con.cursor()
            cur.execute("PRAGMA busy_timeout = 30000;")

            records = []
            for _, row in df_mart.iterrows():
                stat_val = float(row["estadistico"]) if pd.notna(row.get("estadistico")) else None
                p_val = float(row["p_valor"]) if pd.notna(row.get("p_valor")) else None
                records.append((
                    str(row.get("variable", "")),
                    str(row.get("categoria_prueba", "")),
                    str(row.get("prueba", "")),
                    stat_val,
                    p_val,
                    str(row.get("decision", "")),
                    str(row.get("interpretacion", "")),
                ))

            cur.executemany(
                """
                INSERT INTO mart_hypothesis_tests 
                (variable, categoria_prueba, prueba, estadistico, p_valor, decision, interpretacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                records,
            )
            con.commit()
            logger.info("mart_hypothesis_tests cargado con %d registros", len(records))
            return len(records)
        finally:
            con.close()
