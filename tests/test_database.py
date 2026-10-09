"""Pruebas Unitarias para el Módulo de Base de Datos y MDM (Modelo Estrella).
Fase PDCO: CONTROL | Estándar: ISO/IEC 25010 / Ralph Kimball / Clean Code
Casos de prueba: TC-601 a TC-604.
"""

from pathlib import Path
import pytest
import pandas as pd

from src.database.mdm_manager import (
    MDMManager,
    levenshtein_similarity,
    jaro_winkler_similarity,
)
from src.database.db_manager import DatabaseManager
from src.database.sql_loader import SQLLoader


class TestMDMManager:
    """TC-601: Pruebas unitarias para reconciliación difusa y Golden Records."""

    def test_string_similarity_metrics(self):
        """Verifica comportamiento de similitud Levenshtein y Jaro-Winkler."""
        assert levenshtein_similarity("MEDELLIN", "MEDELLIN") == 1.0
        assert jaro_winkler_similarity("BOGOTA", "BOGOTA") == 1.0

        # Errores tipográficos comunes
        sim_lev = levenshtein_similarity("BOGOTA", "BOGOTAA")
        assert sim_lev >= 0.8

        sim_jw = jaro_winkler_similarity("MEDELLIN", "MEDELIN")
        assert sim_jw > 0.9

    def test_mdm_reconciliation_exact_and_fuzzy(self):
        """Verifica registro canónico y reconciliación difusa con umbral."""
        mdm = MDMManager(match_threshold=0.80)
        divipola = pd.DataFrame(
            {
                "cod_municipio": ["05001", "11001"],
                "nombre_municipio": ["MEDELLIN", "BOGOTA, D.C."],
                "cod_departamento": ["05", "11"],
                "nombre_departamento": ["ANTIOQUIA", "BOGOTA D.C."],
            }
        )
        mdm.register_canonical_municipios(divipola)

        # 1. Exact Match
        res_exact = mdm.match_municipio("Medellín")
        assert res_exact is not None
        assert res_exact["cod_municipio"] == "05001"
        assert res_exact["match_type"] == "EXACT"

        # 2. Fuzzy Match (variación tipográfica leve)
        res_fuzzy = mdm.match_municipio("Medellin D.C.")
        assert res_fuzzy is not None
        assert res_fuzzy["cod_municipio"] == "05001"

        # 3. No Match (término completamente ajeno)
        res_none = mdm.match_municipio("PARIS")
        assert res_none is None


class TestDatabaseManagerAndLoader:
    """TC-602, TC-603, TC-604: Pruebas de inicialización DDL, carga masiva y vistas OLAP."""

    @pytest.fixture
    def db_env(self, tmp_path: Path):
        db_file = tmp_path / "test_agrostats.sqlite3"
        mgr = DatabaseManager(db_path=db_file, use_duckdb=False)
        mgr.initialize_schema()
        loader = SQLLoader(db_manager=mgr)
        return mgr, loader

    def test_schema_initialization(self, db_env):
        """TC-602: Verifica creación de tablas dimensionales y hechos."""
        mgr, _ = db_env
        df_tables = mgr.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
        table_names = list(df_tables["name"])
        assert "dim_tiempo" in table_names
        assert "dim_municipio" in table_names
        assert "dim_producto" in table_names
        assert "fact_produccion_eva" in table_names

    def test_sql_loader_dimensions_and_facts(self, db_env):
        """TC-603: Verifica carga de dimensiones y hechos."""
        mgr, loader = db_env

        # 1. Dim Tiempo
        t_count = loader.load_dim_tiempo(start_year=2022, end_year=2023)
        assert t_count == 24  # 2 años * 12 meses

        # 2. Dim Municipio
        df_mun = pd.DataFrame(
            {
                "cod_municipio": ["05001"],
                "cod_departamento": ["05"],
                "nombre_municipio": ["Medellín"],
                "nombre_departamento": ["Antioquia"],
            }
        )
        m_count = loader.load_dim_municipio(df_mun)
        assert m_count == 1

        # 3. Fact EVA
        df_eva = pd.DataFrame(
            {
                "anio": [2022],
                "cod_municipio": ["05001"],
                "cultivo": ["Café"],
                "variedad": ["Caturra"],
                "grupo_de_cultivo": ["Otros permanentes"],
                "area_sembrada_ha": [100.0],
                "area_cosechada_ha": [95.0],
                "produccion_ton": [210.0],
                "rendimiento_ton_ha": [2.21],
            }
        )
        eva_count = loader.load_fact_eva(df_eva)
        assert eva_count == 1

        # Verificar que el producto fue creado en dim_producto
        df_prod = mgr.execute_query("SELECT * FROM dim_producto;")
        assert len(df_prod) == 1
        assert df_prod["nombre_producto"].iloc[0] == "CAFE"

        # 4. Insumo
        id_insumo = loader.get_or_create_insumo("Urea 46%", "Fertilizante")
        assert id_insumo >= 1
        # Re-consulta de insumo existente retorna el mismo ID
        id_insumo_existente = loader.get_or_create_insumo("Urea 46%")
        assert id_insumo == id_insumo_existente

        # 5. execute_statement
        rows_affected = mgr.execute_statement(
            "UPDATE dim_insumo SET categoria_insumo = ? WHERE id_insumo = ?",
            ("Nitrogenados", id_insumo),
        )
        assert rows_affected == 1

    def test_analytical_view_query(self, db_env):
        """TC-604: Verifica consulta sobre view_indicadores_agroclimaticos."""
        mgr, loader = db_env

        loader.load_dim_tiempo(start_year=2022, end_year=2022)
        df_mun = pd.DataFrame(
            {
                "cod_municipio": ["11001"],
                "cod_departamento": ["11"],
                "nombre_municipio": ["Bogotá, D.C."],
                "nombre_departamento": ["Bogotá D.C."],
            }
        )
        loader.load_dim_municipio(df_mun)

        df_eva = pd.DataFrame(
            {
                "anio": [2022],
                "cod_municipio": ["11001"],
                "cultivo": ["Papa"],
                "variedad": ["Pastusa"],
                "area_sembrada_ha": [50.0],
                "area_cosechada_ha": [50.0],
                "produccion_ton": [750.0],
                "rendimiento_ton_ha": [15.0],
            }
        )
        loader.load_fact_eva(df_eva)

        # Consulta analítica desnormalizada
        df_view = mgr.execute_query("SELECT * FROM view_indicadores_agroclimaticos;")
        assert len(df_view) == 1
        row = df_view.iloc[0]
        assert row["anio"] == 2022
        assert row["nombre_municipio"] == "BOGOTA, D.C."
        assert row["nombre_producto"] == "PAPA"
        assert row["rendimiento_ton_ha"] == 15.0

    def test_load_fact_clima_sipsa_and_mart(self, db_env):
        """TC-605: Verifica carga de hechos meteorológicos, precios SIPSA y data mart estadístico."""
        mgr, loader = db_env
        loader.load_dim_tiempo(start_year=2022, end_year=2022)

        # 1. Fact Clima
        df_clima = pd.DataFrame({
            "fecha": ["2022-05-15", "2022-06-15"],
            "codigo_estacion": ["001", "001"],
            "valor_observado": [120.5, 85.0],
            "sensor_descripcion": ["PRECIPITACION", "PRECIPITACION"],
            "cod_municipio": ["11001", "11001"],
            "spi_3": [0.45, -0.2],
            "anomalia_termica_z": [0.1, 0.3],
        })
        n_clima = loader.load_fact_clima(df_clima)
        assert n_clima == 2
        df_clima_db = mgr.execute_query("SELECT * FROM fact_clima_ideam;")
        assert len(df_clima_db) == 2

        # 2. Fact SIPSA
        df_sipsa = pd.DataFrame({
            "fecha": ["2022-05-01", "2022-06-01"],
            "urea_46": [150000.0, 160000.0],
            "dap_18_46": [180000.0, 190000.0],
        })
        n_sipsa = loader.load_fact_sipsa(df_sipsa, cod_municipio="11001")
        assert n_sipsa == 4  # 2 meses * 2 insumos
        df_sipsa_db = mgr.execute_query("SELECT * FROM fact_precios_sipsa;")
        assert len(df_sipsa_db) == 4

        # 3. Data Mart de Hipótesis
        df_mart = pd.DataFrame({
            "variable": ["precipitacion"],
            "categoria_prueba": ["Normalidad"],
            "prueba": ["JARQUE_BERA"],
            "estadistico": [4.5],
            "p_valor": [0.10],
            "decision": ["NO_RECHAZA_H0"],
            "interpretacion": ["Distribución normal"],
        })
        n_mart = loader.load_mart_hypothesis(df_mart)
        assert n_mart == 1
        df_mart_db = mgr.execute_query("SELECT * FROM mart_hypothesis_tests;")
        assert len(df_mart_db) == 1
        assert df_mart_db["prueba"].iloc[0] == "JARQUE_BERA"
