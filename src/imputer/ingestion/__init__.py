"""
Subpaquete de Ingesta y Conectores de Datos Externos
"""

from .base_client import ResilientHttpClient
from .socrata_client import SocrataClient
from .dane_scraper import DaneScraper
from .dataset_registry import DATASET_REGISTRY, DatasetMetadata

__all__ = [
    "ResilientHttpClient",
    "SocrataClient",
    "DaneScraper",
    "DATASET_REGISTRY",
    "DatasetMetadata",
]
