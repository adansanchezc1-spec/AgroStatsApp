"""Paquete de Ingestión Multifuente de Datos."""
from src.ingestion.base_client import BaseAPIClient
from src.ingestion.socrata_client import SocrataClient
from src.ingestion.ica_client import ICAClient
from src.ingestion.landing_manager import LandingManager

__all__ = ["BaseAPIClient", "SocrataClient", "ICAClient", "LandingManager"]
