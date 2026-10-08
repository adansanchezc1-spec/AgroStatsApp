"""Módulo de Configuración Centralizada y Gestión de Parámetros.
Fase PDCO: DEVELOPMENT | Estándar: Twelve-Factor App & PEP 8
AgroStatsApp - Configuración tipada con Standard Library (Dataclasses) sin dependencias externas.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class SocrataDatasetConfig:
    """Metadatos de cada recurso en la API Socrata SODA 2.0 (datos.gov.co)."""
    resource_id: str
    nombre: str
    entidad: str
    descripcion: str
    url_json: str

    @classmethod
    def create(cls, resource_id: str, nombre: str, entidad: str, descripcion: str) -> SocrataDatasetConfig:
        return cls(
            resource_id=resource_id,
            nombre=nombre,
            entidad=entidad,
            descripcion=descripcion,
            url_json=f"https://www.datos.gov.co/resource/{resource_id}.json",
        )


@dataclass
class AppSettings:
    """Configuración principal del sistema AgroStatsApp."""
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    SOCRATA_APP_TOKEN: str = field(default_factory=lambda: os.getenv("SOCRATA_APP_TOKEN", ""))
    SOCRATA_SECRET_TOKEN: str = field(default_factory=lambda: os.getenv("SOCRATA_SECRET_TOKEN", ""))
    SOCRATA_BASE_URL: str = field(default_factory=lambda: os.getenv("SOCRATA_BASE_URL", "https://www.datos.gov.co/resource"))

    ICA_RESOURCE_KEY: str = field(default_factory=lambda: os.getenv("ICA_RESOURCE_KEY", "a7581d79-b3bb-416f-a7c5-5034e5ca7a7"))
    ICA_TENANT_ID: str = field(default_factory=lambda: os.getenv("ICA_TENANT_ID", "b7aeda0c-64cd-49d2-9a4d-3062367432e3"))
    ICA_ENDPOINT_URL: str = field(
        default_factory=lambda: os.getenv(
            "ICA_ENDPOINT_URL",
            "https://wabi-us-north-central-a-primary-redirect.analysis.windows.net/powerbi/api/v1.0/public/reports/querydata?synchronous=true"
        )
    )

    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    DATA_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data")
    RAW_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "RAW")
    CLEANED_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "CLEANED")
    INDICATORS_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "INDICATORS")
    EXTERNAL_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "EXTERNAL")
    DATABASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "DATABASE")
    LOGS_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "logs")

    DATABASE_URL: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/DATABASE/agrostats.db"))
    DUCKDB_PATH: str = field(default_factory=lambda: os.getenv("DUCKDB_PATH", "data/DATABASE/agrostats.duckdb"))

    SOCRATA_DATASETS: Dict[str, SocrataDatasetConfig] = field(
        default_factory=lambda: {
            # 7 Endpoints IDEAM
            "ideam_telemetria": SocrataDatasetConfig.create("57sv-p2fu", "Telemetría Sensores Realtime", "IDEAM", "Lecturas en tiempo real"),
            "ideam_pluviometria": SocrataDatasetConfig.create("s54a-sgyg", "Pluviometría y Precipitación", "IDEAM", "Precipitación diaria"),
            "ideam_temp_media": SocrataDatasetConfig.create("sbwg-7ju4", "Temperatura Ambiente 2m", "IDEAM", "Temperatura media"),
            "ideam_temp_maxima": SocrataDatasetConfig.create("ccvq-rp9s", "Temperatura Máxima", "IDEAM", "Temperatura máxima"),
            "ideam_temp_minima": SocrataDatasetConfig.create("afdg-3zpb", "Temperatura Mínima", "IDEAM", "Temperatura mínima"),
            "ideam_radiacion": SocrataDatasetConfig.create("rv9s-8nv6", "Radiación Solar Global", "IDEAM", "Radiación solar"),
            "ideam_normales_spi": SocrataDatasetConfig.create("nsz2-kzcq", "Normales Climatológicas & SPI", "IDEAM", "Normales y sequía"),
            # 2 Endpoints DANE / SIPSA
            "sipsa_insumos": SocrataDatasetConfig.create("gwbi-fnzs", "SIPSA Insumos Agrícolas", "DANE", "Precios de insumos"),
            "sipsa_aba": SocrataDatasetConfig.create("wgj6-cvyj", "SIPSA Alimentos Balanceados (ABA)", "DANE", "Precios balanceados"),
            # 2 Endpoints UPRA
            "upra_exportaciones": SocrataDatasetConfig.create("gaic-b8aw", "Exportaciones & Bioinsumos", "UPRA", "Comercio exterior"),
            "upra_eva": SocrataDatasetConfig.create("2pnw-mmge", "Evaluaciones Agropecuarias (EVA)", "UPRA", "Estadísticas agrícolas EVA"),
        }
    )


# Instancia singleton de configuración
settings = AppSettings()
