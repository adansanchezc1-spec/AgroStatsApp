"""
Módulo de Configuración Central - AgroStats Imputer & Ingestor
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2, 12-Factor App, PEP 8
"""

from pathlib import Path

# Re-exportar constantes de red y endpoints desde el módulo de ingesta
from .ingestion.constants import (
    HTTP_TIMEOUT_SECONDS,
    MAX_HTTP_RETRIES,
    RETRY_BACKOFF_FACTOR,
    USER_AGENT,
    DATOS_GOV_API_URL,
    DANE_BASE_URL,
    DEFAULT_BATCH_LIMIT,
    SAMPLE_BATCH_LIMIT,
)

# Directorio raíz del módulo imputer
MODULE_DIR = Path(__file__).resolve().parent
SRC_DIR = MODULE_DIR.parent
APP_ROOT = SRC_DIR.parent

# Rutas de persistencia de datos (CRISPDM / data / RAW)
CRISPDM_RAW_DIR = APP_ROOT / "CRISPDM" / "data" / "RAW"
TOP_RAW_DIR = APP_ROOT / "data" / "RAW"

# Directorio de salida principal (garantiza existencia)
DEFAULT_RAW_DIR = CRISPDM_RAW_DIR
DEFAULT_RAW_DIR.mkdir(parents=True, exist_ok=True)

# También asegurar que TOP_RAW_DIR exista para interoperabilidad si se requiere
TOP_RAW_DIR.mkdir(parents=True, exist_ok=True)

# Identificadores de Recursos Socrata (datos.gov.co)
SOCRATA_RESOURCES = {
    "ideam_telemetria_realtime": "57sv-p2fu", # Mediciones/sensores telemétricos en tiempo real (Temperatura, Lluvia, etc.)
    "ideam_pluvio": "s54a-sgyg",        # Precipitaciones horarias y diarias por estación
    "ideam_temp_amb": "sbwg-7ju4",      # Temperatura ambiente del aire (2m)
    "ideam_temp_max": "ccvq-rp9s",      # Temperatura máxima del aire
    "ideam_temp_min": "afdg-3zpb",      # Temperatura mínima del aire (alerta heladas)
    "ideam_rad_solar": "rv9s-8nv6",     # Radiación global acumulada por estación
    "ideam_normales": "nsz2-kzcq",      # Normales climatológicas (base sequía y evapotranspiración)
    "sipsa_insumos_socrata": "gwbi-fnzs", # Índice de precios de insumos agrícolas (fertilizantes, plaguicidas)
    "sipsa_balanceados_aba": "wgj6-cvyj", # Índice de precios de alimentos balanceados animales
}

__all__ = [
    "MODULE_DIR",
    "SRC_DIR",
    "APP_ROOT",
    "CRISPDM_RAW_DIR",
    "TOP_RAW_DIR",
    "DEFAULT_RAW_DIR",
    "HTTP_TIMEOUT_SECONDS",
    "MAX_HTTP_RETRIES",
    "RETRY_BACKOFF_FACTOR",
    "USER_AGENT",
    "DATOS_GOV_API_URL",
    "DANE_BASE_URL",
    "DEFAULT_BATCH_LIMIT",
    "SAMPLE_BATCH_LIMIT",
    "SOCRATA_RESOURCES",
]
