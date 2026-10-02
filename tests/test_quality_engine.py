"""
Pruebas Unitarias para el Motor de Calidad de Datos (ISO/IEC 25010 & DAMA-DMBOK 2)
Fase PDCO: CONTROL | Active Skill: 04-testing
"""

import unittest
import pandas as pd
import numpy as np
from src.validation.quality_engine import DataQualityEngine, DataQualityReport


class TestDataQualityEngine(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame({
            "codigo_divipola": ["11001", "05001", "76001", "08001"],
            "producto": ["PAPA", "CEBOLLA", "TOMATE", "PLATANO"],
            "precio_kg": [2500.0, 3200.0, 4100.0, 1800.0],
            "fecha": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
            "latitud": [4.7110, 6.2442, 3.4516, 10.9685],
            "longitud": [-74.0721, -75.5812, -76.5320, -74.7813]
        })

    def test_evaluate_perfect_dataset(self):
        report = DataQualityEngine.evaluate(
            df=self.sample_df,
            dataset_name="test_perfect",
            primary_keys=["codigo_divipola", "producto"],
            numeric_range_rules={"precio_kg": (100.0, 10000.0)}
        )
        self.assertEqual(report.status, "PASSED")
        self.assertGreaterEqual(report.overall_score, 0.90)
        self.assertIn("Completeness", report.dimension_scores)
        self.assertIn("Validity", report.dimension_scores)
        self.assertIn("Uniqueness", report.dimension_scores)
        self.assertIn("Consistency", report.dimension_scores)
        self.assertIn("Timeliness", report.dimension_scores)

    def test_evaluate_null_exceeding_threshold(self):
        corrupted_df = self.sample_df.copy()
        corrupted_df["precio_kg"] = [np.nan, np.nan, np.nan, 2000.0]  # 75% nulos
        report = DataQualityEngine.evaluate(
            df=corrupted_df,
            dataset_name="test_nulls",
            max_null_threshold=0.30
        )
        self.assertIn(report.status, ["WARNING", "FAILED"])
        self.assertLess(report.dimension_scores["Completeness"], 0.90)

    def test_evaluate_duplicate_primary_keys(self):
        dup_df = pd.concat([self.sample_df, self.sample_df.iloc[[0]]], ignore_index=True)
        report = DataQualityEngine.evaluate(
            df=dup_df,
            dataset_name="test_duplicates",
            primary_keys=["codigo_divipola", "producto"]
        )
        self.assertIn(report.status, ["WARNING", "FAILED"])
        self.assertLess(report.dimension_scores["Uniqueness"], 1.0)

    def test_evaluate_out_of_range_values(self):
        out_df = self.sample_df.copy()
        out_df.loc[0, "precio_kg"] = -500.0  # Precio negativo inválido
        report = DataQualityEngine.evaluate(
            df=out_df,
            dataset_name="test_ranges",
            numeric_range_rules={"precio_kg": (0.0, 10000.0)}
        )
        # Debe marcar advertencia o fallo en Validity
        self.assertLess(report.dimension_scores["Validity"], 1.0)

    def test_to_markdown_and_dict(self):
        report = DataQualityEngine.evaluate(
            df=self.sample_df,
            dataset_name="test_export"
        )
        md = report.to_markdown()
        d = report.to_dict()
        self.assertIn("# Reporte de Calidad de Datos", md)
        self.assertIn("overall_score", d)
        self.assertEqual(d["dataset_name"], "test_export")


if __name__ == "__main__":
    unittest.main()
