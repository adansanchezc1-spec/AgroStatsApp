import unittest
import pandas as pd
from src.validation.schemas import DataValidator, QualityGateError

class TestValidation(unittest.TestCase):
    def test_validate_schema_pass(self):
        df = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
        self.assertTrue(DataValidator.validate_schema(df, required_columns=["id", "val"]))

    def test_validate_schema_missing_column(self):
        df = pd.DataFrame({"id": [1, 2]})
        with self.assertRaises(QualityGateError):
            DataValidator.validate_schema(df, required_columns=["id", "missing_col"])

if __name__ == "__main__":
    unittest.main()
