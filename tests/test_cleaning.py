import unittest
import pandas as pd
from src.cleaning.sanitizer import DataSanitizer
from src.cleaning.pii_handler import PIIHandler

class TestCleaning(unittest.TestCase):
    def test_to_snake_case(self):
        self.assertEqual(DataSanitizer.to_snake_case("Nombre del Municipio (DIVIPOLA)"), "nombre_del_municipio_divipola")
        self.assertEqual(DataSanitizer.to_snake_case("Precio $/Kg"), "precio_kg")

    def test_sanitize_dataframe(self):
        df = pd.DataFrame({
            "Nombre Producto": ["Papa ", "  "],
            "VALOR": [100, None]
        })
        clean_df = DataSanitizer.sanitize_dataframe(df)
        self.assertIn("nombre_producto", clean_df.columns)
        self.assertIn("valor", clean_df.columns)

    def test_pii_handler(self):
        df = pd.DataFrame({"email": ["user@example.com"]})
        hashed_df = PIIHandler.sanitize_pii(df, ["email"])
        self.assertNotEqual(hashed_df["email"].iloc[0], "user@example.com")
        self.assertEqual(len(hashed_df["email"].iloc[0]), 64)

if __name__ == "__main__":
    unittest.main()
