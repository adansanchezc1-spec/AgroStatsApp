"""
Módulo de Ingesta Multi-Fuente
"""
from .socrata_client import SocrataClient
from .pdf_extractor import PDFExtractor
from .file_loader import FileLoader

__all__ = ["SocrataClient", "PDFExtractor", "FileLoader"]
