"""
Manejador de Anonimización y Protección de Datos Personales (PII)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Seguridad y Privacidad), GDPR / Ley 1581 Colombia
"""

import hashlib
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class PIIHandler:
    """Aplica hashing criptográfico SHA-256 a columnas sensibles (emails, teléfonos, nombres)."""
    
    @staticmethod
    def hash_value(val: str, salt: str = "AgroStats2026") -> str:
        if pd.isna(val) or val is None:
            return ""
        v = f"{salt}:{str(val).strip().lower()}"
        return hashlib.sha256(v.encode('utf-8')).hexdigest()

    @classmethod
    def sanitize_pii(cls, df: pd.DataFrame, pii_columns: list) -> pd.DataFrame:
        clean_df = df.copy()
        for col in pii_columns:
            if col in clean_df.columns:
                clean_df[col] = clean_df[col].apply(cls.hash_value)
                logger.info(f"Columna sensible '{col}' anonimizada con SHA-256.")
        return clean_df
