import unittest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.ingestion.socrata_client import SocrataClient

class TestIngestion(unittest.TestCase):
    def test_socrata_client_fetch_all(self):
        client = SocrataClient(resource_id="test-1234")
        mock_data = [{"id": 1, "nombre": "Test 1"}, {"id": 2, "nombre": "Test 2"}]
        
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_data
            mock_get.return_value = mock_resp
            
            df = client.fetch_all(batch_size=10, max_records=2)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 2)
            self.assertIn("nombre", df.columns)

if __name__ == "__main__":
    unittest.main()
