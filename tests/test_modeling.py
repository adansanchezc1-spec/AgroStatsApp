import unittest
import numpy as np
import pandas as pd
from src.modeling.business_questions_engine import BusinessQuestionsEngine, GranularityHarmonizer

class TestBusinessQuestionsEngine(unittest.TestCase):
    def test_solve_a1_market_size(self):
        s = pd.Series([100.0, 200.0, 300.0])
        res = BusinessQuestionsEngine.solve_a1_market_size(s)
        self.assertEqual(res["size_parametric"], 600.0)
        self.assertEqual(res["size_non_parametric"], 600.0)

    def test_solve_b3_stability(self):
        s = pd.Series([10.0, 10.2, 9.8, 10.1, 9.9])
        res = BusinessQuestionsEngine.solve_b3_stability(s)
        self.assertTrue(res["is_stable"])
        self.assertLess(res["cv_parametric"], 0.1)

    def test_solve_c1_hhi(self):
        shares = np.array([50.0, 30.0, 20.0])
        res = BusinessQuestionsEngine.solve_c1_hhi(shares)
        self.assertGreater(res["hhi_parametric"], 2500)
        self.assertEqual(res["level"], "Altamente Concentrado")

    def test_granularity_harmonizer_station_to_divipola(self):
        df = pd.DataFrame({"codigoestacion": ["21206810"], "municipio": ["Bogotá, D.C"]})
        res = GranularityHarmonizer.station_to_divipola(df)
        self.assertIn("codigo_divipola", res.columns)
        self.assertEqual(len(res), 1)

if __name__ == "__main__":
    unittest.main()
