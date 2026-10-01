"""
Modelado Estadístico, Control Estadístico de Procesos (SPC) e Inferencia
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class AgroModeler:
    """Implementa Nelson Rules (SPC) y descomposiciones de series de tiempo para datos agrometeorológicos y de mercado."""
    
    @staticmethod
    def detect_nelson_anomalies(series: pd.Series) -> pd.Series:
        """Detecta puntos fuera de límites (Regla 1 de Nelson: |z| > 3)."""
        mean = series.mean()
        std = series.std()
        if std == 0:
            return pd.Series(False, index=series.index)
        z_scores = np.abs((series - mean) / std)
        anomalies = z_scores > 3
        logger.info(f"SPC Nelson Rule 1: {anomalies.sum()} anomalías detectadas de {len(series)} puntos.")
        return anomalies
