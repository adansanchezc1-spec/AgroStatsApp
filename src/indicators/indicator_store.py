"""Almacén y Consolidación de Indicadores Gold (IndicatorStore).
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 / Clean Architecture
Consolidación multidimensional de índices agroclimáticos y de mercado por llave canónica.
"""

from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("indicators.indicator_store")


class IndicatorStore:
    """Gestor de persistencia e integración de la capa de indicadores (Gold)."""

    def __init__(self, indicators_dir: Optional[Path] = None) -> None:
        self.indicators_dir = indicators_dir or settings.INDICATORS_DIR
        self.indicators_dir.mkdir(parents=True, exist_ok=True)

    def save_indicator_dataset(
        self,
        df: pd.DataFrame,
        dataset_name: str,
    ) -> Dict[str, Any]:
        """
        Persiste un DataFrame consolidado de indicadores en formato Parquet Snappy.
        Calcula hash SHA-256 y estadísticas de almacenamiento.
        """
        if df.empty:
            logger.warning("Intento de guardar DataFrame de indicadores vacío: %s", dataset_name)

        filename = dataset_name if dataset_name.endswith(".parquet") else f"{dataset_name}.parquet"
        target_path = self.indicators_dir / filename

        df.to_parquet(target_path, engine="pyarrow", compression="snappy", index=False)

        # Cálculo de huella criptográfica SHA-256
        sha256_hash = hashlib.sha256()
        with open(target_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256_hash.update(chunk)
        digest = sha256_hash.hexdigest()

        metadata = {
            "dataset_name": dataset_name,
            "filename": filename,
            "target_path": str(target_path),
            "rows": len(df),
            "columns": len(df.columns),
            "file_size_bytes": target_path.stat().st_size,
            "sha256": digest,
        }

        logger.info(
            "Indicadores guardados exitosamente: %s (%d filas, %d columnas, SHA-256: %s...)",
            filename, len(df), len(df.columns), digest[:12]
        )
        return metadata

    def load_indicator_dataset(self, dataset_name: str) -> pd.DataFrame:
        """Carga un dataset de indicadores previamente generado."""
        filename = dataset_name if dataset_name.endswith(".parquet") else f"{dataset_name}.parquet"
        target_path = self.indicators_dir / filename
        if not target_path.exists():
            raise FileNotFoundError(f"Dataset de indicadores no encontrado: {target_path}")
        return pd.read_parquet(target_path)

    def consolidate_features(
        self,
        df_base: pd.DataFrame,
        df_indicators: List[pd.DataFrame],
        join_keys: List[str],
    ) -> pd.DataFrame:
        """
        Fusiona de manera segura múltiples dataframes de indicadores sobre las llaves canónicas.
        """
        consolidated = df_base.copy()
        for df_item in df_indicators:
            if df_item.empty:
                continue
            common_keys = [k for k in join_keys if k in consolidated.columns and k in df_item.columns]
            if common_keys:
                consolidated = pd.merge(consolidated, df_item, on=common_keys, how="left")
        return consolidated
