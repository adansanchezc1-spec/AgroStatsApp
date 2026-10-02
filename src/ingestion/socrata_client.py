"""
Cliente Socrata SODA 2.0 (datos.gov.co e IDEAM)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: 12-Factor App, DAMA-DMBOK 2, PEP 8, ISO/IEC 25010
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
import requests
import pandas as pd

from .resilience import retry_with_backoff, CircuitBreaker

logger = logging.getLogger(__name__)


class SocrataClient:
    """
    Cliente robusto para APIs Socrata de datos.gov.co con soporte para:
      - Autenticación segura vía X-App-Token / API Key
      - Paginación determinista ($limit, $offset)
      - Retroceso exponencial con Jitter ante Rate Limits (HTTP 429)
      - Circuit Breaker para prevenir sobrecargas
      - Auditoría de latencia y volumen
    """
    
    def __init__(
        self,
        resource_id: str,
        app_token: Optional[str] = None,
        base_url: str = "https://www.datos.gov.co/resource",
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.resource_id = resource_id
        self.base_url = f"{base_url.rstrip('/')}/{resource_id}.json"
        self.app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        self.circuit_breaker = circuit_breaker or CircuitBreaker(failure_threshold=4, recovery_timeout=20.0)
        
        self.headers: Dict[str, str] = {
            "User-Agent": "AgroStatsIntelligencePlatform/2.0",
            "Accept": "application/json"
        }
        if self.app_token:
            self.headers["X-App-Token"] = self.app_token

    @retry_with_backoff(retries=3, initial_delay=1.5, backoff_factor=2.0)
    def _fetch_page(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Llamada individual paginada con protección de Circuit Breaker y retry."""
        if not self.circuit_breaker.can_execute():
            logger.warning("[SocrataClient] CircuitBreaker activo. Omitiendo llamada remota temporalmente.")
            return []
            
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 429:
                logger.warning("[SocrataClient] Rate limit 429 alcanzado.")
                time.sleep(5.0)
                response.raise_for_status()
            response.raise_for_status()
            data = response.json()
            self.circuit_breaker.record_success()
            return data if isinstance(data, list) else []
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise e
            
    def fetch_all(self, batch_size: int = 50000, max_records: Optional[int] = None) -> pd.DataFrame:
        """Extrae registros del dataset en lotes paginados con manejo de rate limit y métricas."""
        all_records: List[Dict[str, Any]] = []
        offset = 0
        start_time = time.time()
        
        logger.info(f"Iniciando extracción Socrata para recurso: {self.resource_id}")
        
        while True:
            limit = batch_size if max_records is None else min(batch_size, max_records - len(all_records))
            if limit <= 0:
                break
                
            params = {
                "$limit": limit,
                "$offset": offset,
            }
            
            try:
                data = self._fetch_page(params)
            except Exception as e:
                logger.error(f"Error irrecuperable en paginación offset {offset}: {e}")
                break
                
            if not data:
                break
                
            all_records.extend(data)
            offset += len(data)
            logger.info(f"Extraídos {len(all_records)} registros acumulados (Offset {offset})")
            
            if len(data) < limit:
                break
                
        df = pd.DataFrame(all_records)
        elapsed = time.time() - start_time
        logger.info(f"Finalizada extracción en {elapsed:.2f}s. Total registros: {len(df)}")
        return df
