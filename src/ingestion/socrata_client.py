"""
Cliente Socrata SODA 2.0 (datos.gov.co e IDEAM)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: 12-Factor App, DAMA-DMBOK 2, PEP 8
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class SocrataClient:
    """Cliente robusto para APIs Socrata de datos.gov.co con soporte para API Key/App Token, paginación y backoff."""
    
    def __init__(self, resource_id: str, app_token: Optional[str] = None, base_url: str = "https://www.datos.gov.co/resource"):
        self.resource_id = resource_id
        self.base_url = f"{base_url.rstrip('/')}/{resource_id}.json"
        self.app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        
        self.headers: Dict[str, str] = {
            "User-Agent": "AgroStatsIntelligencePlatform/1.0",
            "Accept": "application/json"
        }
        if self.app_token:
            self.headers["X-App-Token"] = self.app_token
            
    def fetch_all(self, batch_size: int = 50000, max_records: Optional[int] = None) -> pd.DataFrame:
        """Extrae todos los registros del dataset en lotes paginados con manejo de rate limit."""
        all_records: List[Dict[str, Any]] = []
        offset = 0
        
        logger.info(f"Iniciando extracción Socrata para recurso: {self.resource_id}")
        
        while True:
            limit = batch_size if max_records is None else min(batch_size, max_records - len(all_records))
            if limit <= 0:
                break
                
            params = {
                "$limit": limit,
                "$offset": offset,
            }
            
            success = False
            for retry in range(3):
                try:
                    response = requests.get(self.base_url, headers=self.headers, params=params, timeout=30)
                    if response.status_code == 429:
                        wait = (2 ** retry) * 5
                        logger.warning(f"Rate limit 429 alcanzado. Reintentando en {wait}s...")
                        time.sleep(wait)
                        continue
                    response.raise_for_status()
                    data = response.json()
                    success = True
                    break
                except Exception as e:
                    logger.error(f"Error en intento {retry+1} al consultar {self.base_url}: {e}")
                    time.sleep(2)
                    
            if not success or not data:
                break
                
            all_records.extend(data)
            offset += len(data)
            logger.info(f"Extraídos {len(all_records)} registros acumulados (Offset {offset})")
            
            if len(data) < limit:
                break
                
        df = pd.DataFrame(all_records)
        logger.info(f"Finalizada extracción. Total registros: {len(df)}")
        return df
