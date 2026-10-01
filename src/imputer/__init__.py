"""
Paquete AgroStats Imputer & Ingestor
====================================
Automatización de ingesta, auditoría criptográfica en data/RAW e imputación inteligente multivariada.

Módulos principales:
- `AgroDataIngestionPipeline`: Orquestador de descarga desde DANE y Socrata.
- `IntelligentImputer`: Motor de benchmark de imputación (Rubin, KNN, MICE, Interpolación, Mediana).
- `SocrataClient`: Conector para APIs abiertas gubernamentales.
- `DaneScraper`: Descargador resiliente de boletines y anexos SIPSA/IPP/IPC.
- `DATASET_REGISTRY`: Catálogo formal de las 10 fuentes estratégicas bajo DAMA-DMBOK.
"""

from .pipeline import AgroDataIngestionPipeline
from .imputation.imputation_engine import IntelligentImputer, ImputationBenchmarkResult
from .imputation.rubin_diagnostics import RubinDiagnostics, MissingPatternReport
from .ingestion.socrata_client import SocrataClient
from .ingestion.dane_scraper import DaneScraper
from .ingestion.dataset_registry import DATASET_REGISTRY, DatasetMetadata
from .config import DEFAULT_RAW_DIR, TOP_RAW_DIR

__version__ = "1.0.0"
__all__ = [
    "AgroDataIngestionPipeline",
    "IntelligentImputer",
    "ImputationBenchmarkResult",
    "RubinDiagnostics",
    "MissingPatternReport",
    "SocrataClient",
    "DaneScraper",
    "DATASET_REGISTRY",
    "DatasetMetadata",
    "DEFAULT_RAW_DIR",
    "TOP_RAW_DIR",
]
