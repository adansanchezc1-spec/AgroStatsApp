"""
Constantes de Red, Timeouts y Endpoints de Ingesta
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: PEP 8, 12-Factor App, Resiliencia HTTP
"""

# Configuración HTTP y Timeouts
HTTP_TIMEOUT_SECONDS: int = 30
MAX_HTTP_RETRIES: int = 4
RETRY_BACKOFF_FACTOR: float = 1.5
USER_AGENT: str = "AgroStats-Intelligence-Platform/1.0 (DANE-IDEAM Research Ingestor; contact@statsfirm.com)"

# Endpoints Base Oficiales
DATOS_GOV_API_URL: str = "https://www.datos.gov.co/resource"
DANE_BASE_URL: str = "https://www.dane.gov.co"

# Límites de Lotes para Consultas Paginadas
DEFAULT_BATCH_LIMIT: int = 5000
SAMPLE_BATCH_LIMIT: int = 200
