"""
Pruebas Unitarias para la Arquitectura Medallion Lakehouse y Persistencia
Fase PDCO: CONTROL | Active Skill: 04-testing
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np

from src.database.db_manager import DatabaseManager
from src.governance.lineage import DataLineageTracker
from src.governance.data_catalog import DataCatalog
from src.lakehouse.lakehouse_manager import MedallionLakehouseManager


class TestMedallionLakehouse(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_lakehouse.db"
        self.db_manager = DatabaseManager(str(self.db_path))
        self.tracker = DataLineageTracker()
        self.catalog = DataCatalog()
        self.lakehouse = MedallionLakehouseManager(self.temp_dir, self.db_manager)

        self.sample_raw_df = pd.DataFrame({
            "Código Estación": ["21206810", "21206820"],
            "Municipio": ["Bogotá, D.C.", "Medellín"],
            "Valor Observado": [14.5, 22.1],
            "Fecha Observación": ["2024-01-01", "2024-01-02"]
        })

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bronze_stage_execution(self):
        bronze_df = self.lakehouse.process_bronze(
            raw_df=self.sample_raw_df,
            dataset_id="test_sensor",
            source_uri="test://sensor_stream",
            tracker=self.tracker
        )
        self.assertIn("_lakehouse_bronze_ingested_at", bronze_df.columns)
        self.assertIn("_lakehouse_payload_sha256", bronze_df.columns)
        bronze_file = self.temp_dir / "data" / "lakehouse" / "bronze" / "test_sensor" / "data.parquet"
        self.assertTrue(bronze_file.exists())

    def test_silver_stage_execution(self):
        bronze_df = self.lakehouse.process_bronze(
            raw_df=self.sample_raw_df,
            dataset_id="test_sensor",
            source_uri="test://sensor_stream",
            tracker=self.tracker
        )
        silver_df, dq_report = self.lakehouse.process_silver(
            bronze_df=bronze_df,
            dataset_id="test_sensor",
            tracker=self.tracker,
            catalog=self.catalog,
            domain="Clima",
            description="Sensores de prueba",
            granularity="Estación × Fecha",
            primary_keys=["codigo_divipola"]
        )
        self.assertIn("codigo_divipola", silver_df.columns)
        self.assertNotIn("_lakehouse_bronze_ingested_at", silver_df.columns)
        self.assertGreaterEqual(dq_report.overall_score, 0.70)
        silver_file = self.temp_dir / "data" / "lakehouse" / "silver" / "test_sensor.parquet"
        self.assertTrue(silver_file.exists())
        self.assertIn("test_sensor", self.db_manager.list_tables())

    def test_gold_marts_creation(self):
        silver_dfs = {
            "sipsa_abastecimientos": pd.DataFrame({"cantidad_kg": [1000.0, 2000.0]}),
            "sipsa_precios": pd.DataFrame({"precio_kg": [3000.0, 3100.0, 2900.0]}),
            "ideam_telemetria_realtime": pd.DataFrame({"valor": [15.0, 16.0, 15.5]})
        }
        gold_marts = self.lakehouse.build_gold_marts(silver_dfs, self.tracker, self.catalog)
        self.assertIn("dim_municipio_divipola", gold_marts)
        self.assertIn("dim_producto_agro", gold_marts)
        self.assertIn("mart_business_questions", gold_marts)
        
        mart_df = gold_marts["mart_business_questions"]
        self.assertTrue((mart_df["pregunta_id"] == "A1").any())
        self.assertTrue((mart_df["pregunta_id"] == "C1").any())


if __name__ == "__main__":
    unittest.main()
