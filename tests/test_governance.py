"""
Pruebas Unitarias para Gobernanza, Linaje y Catálogo de Datos (DAMA-DMBOK 2)
Fase PDCO: CONTROL | Active Skill: 04-testing
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
from src.governance.lineage import DataLineageTracker
from src.governance.data_catalog import DataCatalog


class TestDataGovernance(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tracker = DataLineageTracker()
        self.catalog = DataCatalog()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_lineage_tracker_and_mermaid_generation(self):
        df = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
        checksum = self.tracker.calculate_checksum(df)

        self.tracker.record_stage(
            node_id="bronze_test",
            layer="BRONZE",
            dataset_name="test",
            target_path_or_table="test.parquet",
            input_records=2,
            output_records=2,
            checksum=checksum,
            execution_time_sec=0.05
        )
        self.tracker.record_stage(
            node_id="silver_test",
            layer="SILVER",
            dataset_name="test",
            target_path_or_table="test_silver.parquet",
            input_records=2,
            output_records=2,
            checksum=checksum,
            execution_time_sec=0.08,
            upstream_nodes=["bronze_test"]
        )

        manifest = self.tracker.to_manifest()
        self.assertEqual(manifest["total_nodes"], 2)
        self.assertIn("bronze_test", manifest["nodes"])

        mermaid_str = self.tracker.generate_mermaid_dag()
        self.assertIn("```mermaid", mermaid_str)
        self.assertIn("bronze_test --> silver_test", mermaid_str)

        manifest_file = self.temp_dir / "manifest.json"
        mermaid_file = self.temp_dir / "dag.md"
        self.tracker.save_artifacts(manifest_file, mermaid_file)
        self.assertTrue(manifest_file.exists())
        self.assertTrue(mermaid_file.exists())

    def test_data_catalog_registration_and_export(self):
        df = pd.DataFrame({
            "codigo_divipola": ["11001"],
            "email_contacto": ["user@agro.com"],
            "precio": [2500.0]
        })
        self.catalog.register_table(
            table_name="cat_test",
            layer="SILVER",
            domain="Economía",
            description="Tabla de prueba de catálogo",
            granularity="Municipio",
            primary_key=["codigo_divipola"],
            frequency="Diaria",
            df=df
        )

        json_file = self.temp_dir / "catalog.json"
        md_file = self.temp_dir / "catalog.md"
        self.catalog.export_catalog(json_file, md_file)
        self.assertTrue(json_file.exists())
        self.assertTrue(md_file.exists())

        md_content = md_file.read_text(encoding="utf-8")
        self.assertIn("Catálogo de Datos", md_content)
        self.assertIn("`CONFIDENTIAL_PII`", md_content)


if __name__ == "__main__":
    unittest.main()
