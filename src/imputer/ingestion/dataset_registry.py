"""
Catálogo Maestro y Registro de Fuentes de Datos Agropecuarias (DAMA-DMBOK 2)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Metadata & Data Governance), SWEBOK Cap. 1 & 2
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DatasetMetadata:
    """
    Contrato de Metadatos y Gobernanza para una Fuente Oficial.
    """
    dataset_id: str
    official_name: str
    custodian: str
    data_type: str  # Logístico, Económico, Meteorológico, Macroeconómico
    temporal_granularity: str
    spatial_granularity: str
    extraction_type: str  # 'socrata' | 'dane_scrape'
    remote_resource_id: Optional[str] = None  # Socrata ID si aplica
    primary_format: str = "csv"  # csv, json, xlsx
    description: str = ""
    indicators: List[str] = field(default_factory=list)


DATASET_REGISTRY: Dict[str, DatasetMetadata] = {
    # 1. SIPSA Abastecimientos
    "sipsa_abastecimientos": DatasetMetadata(
        dataset_id="sipsa_abastecimientos",
        official_name="SIPSA - Componente Abastecimiento de Alimentos",
        custodian="DANE",
        data_type="Logístico / Flujos de Carga",
        temporal_granularity="Diaria",
        spatial_granularity="Matriz Origen-Destino (Municipio DIVIPOLA -> Central Mayorista)",
        extraction_type="dane_scrape",
        primary_format="xlsx",
        description="Registro de vehículos de carga y volúmenes (Ton) ingresados a centrales de abastos.",
        indicators=["Volumen total (Ton)", "Concentración logística HHI", "Cuencas de abastecimiento"],
    ),

    # 2. SIPSA Precios Mayoristas
    "sipsa_precios": DatasetMetadata(
        dataset_id="sipsa_precios",
        official_name="SIPSA - Componente Precios Mayoristas",
        custodian="DANE",
        data_type="Económico / Precios Mayoristas",
        temporal_granularity="Diaria",
        spatial_granularity="Central mayorista / Nodo urbano",
        extraction_type="dane_scrape",
        primary_format="xlsx",
        description="Precios diarios mínimos, medios y máximos por producto, variedad y calidad CPC.",
        indicators=["Precio medio ($/kg)", "Volatilidad de precios", "Reglas de Nelson SPC (ISO 7870)"],
    ),

    # 3. SIPSA Insumos Agrícolas
    "sipsa_insumos": DatasetMetadata(
        dataset_id="sipsa_insumos",
        official_name="SIPSA - Insumos Agrícolas y Factores de Producción",
        custodian="DANE / MADR",
        data_type="Económico / Costos de Producción",
        temporal_granularity="Mensual",
        spatial_granularity="Municipio / Almacén agropecuario",
        extraction_type="socrata",
        remote_resource_id="gwbi-fnzs",
        primary_format="json",
        description="Precios de fertilizantes (Urea, DAP, KCl), plaguicidas e índices de insumos agrícolas.",
        indicators=["Índice total insumos", "Precio fertilizantes", "Paridad insumo-producto (Guerra E.)"],
    ),

    # 4. Índice de Precios del Productor (IPP)
    "dane_ipp": DatasetMetadata(
        dataset_id="dane_ipp",
        official_name="Índice de Precios del Productor (IPP) Agropecuario",
        custodian="DANE",
        data_type="Macroeconómico / Inflación al Productor",
        temporal_granularity="Mensual",
        spatial_granularity="Nacional (Agregado)",
        extraction_type="dane_scrape",
        primary_format="xlsx",
        description="Evolución de precios en primera venta (puerta de finca) para cultivos y pecuario.",
        indicators=["Índice IPP Agro", "Variación mensual IPP", "Efecto látigo (Bullwhip effect)"],
    ),

    # 5. Índice de Precios al Consumidor (IPC)
    "dane_ipc": DatasetMetadata(
        dataset_id="dane_ipc",
        official_name="Índice de Precios al Consumidor (IPC) - Alimentos",
        custodian="DANE",
        data_type="Macroeconómico / Inflación Minorista",
        temporal_granularity="Mensual",
        spatial_granularity="23 Ciudades capitales y áreas metropolitanas",
        extraction_type="dane_scrape",
        primary_format="xlsx",
        description="Canasta COICOP División 01 (Alimentos y bebidas no alcohólicas).",
        indicators=["Índice IPC Alimentos", "Margen vertical mayorista-minorista", "Inflación anual alimentos"],
    ),

    # 6. IDEAM Monitor de Sequía / Normales
    "ideam_sequia": DatasetMetadata(
        dataset_id="ideam_sequia",
        official_name="IDEAM - Normales Climatológicas y Monitoreo de Sequía",
        custodian="IDEAM",
        data_type="Hidroclimático / Riesgo de Estrés Hídrico",
        temporal_granularity="Mensual / Normal Climatológica",
        spatial_granularity="Estación climatológica / Municipio",
        extraction_type="socrata",
        remote_resource_id="nsz2-kzcq",
        primary_format="json",
        description="Parámetros normales de lluvia y temperatura para cálculo de anomalías e índices SPI.",
        indicators=["Normal climatológica (mm)", "Anomalía porcentual", "Categoría sequía"],
    ),

    # 7. IDEAM Pluviometría
    "ideam_pluvio": DatasetMetadata(
        dataset_id="ideam_pluvio",
        official_name="IDEAM - Pluviometría y Precipitación por Estación",
        custodian="IDEAM",
        data_type="Meteorológico / Precipitación",
        temporal_granularity="Horaria y Diaria",
        spatial_granularity="Estación telemetrizada (Lat, Lon, Msnm)",
        extraction_type="socrata",
        remote_resource_id="s54a-sgyg",
        primary_format="json",
        description="Lámina de agua precipitada (mm) por estación pluviométrica a nivel nacional.",
        indicators=["Precipitación acumulada (mm)", "Días con lluvia", "Balance hídrico neto"],
    ),

    # 8. IDEAM Temperatura
    "ideam_temperatura": DatasetMetadata(
        dataset_id="ideam_temperatura",
        official_name="IDEAM - Temperatura Ambiente y Extremos",
        custodian="IDEAM",
        data_type="Meteorológico / Régimen Térmico",
        temporal_granularity="Horaria y Diaria",
        spatial_granularity="Estación meteorológica puntual",
        extraction_type="socrata",
        remote_resource_id="sbwg-7ju4",
        primary_format="json",
        description="Temperatura del aire a 2 metros (°C) para seguimiento térmico y heladas.",
        indicators=["Temperatura media (°C)", "Grados Día de Desarrollo (GDD)", "Riesgo de helada (T <= 0°C)"],
    ),

    # 9. IDEAM Evapotranspiración (ET0)
    "ideam_evapotranspiracion": DatasetMetadata(
        dataset_id="ideam_evapotranspiracion",
        official_name="IDEAM - Evapotranspiración y Demanda Atmosférica",
        custodian="IDEAM",
        data_type="Agrometeorológico / Balance Hídrico",
        temporal_granularity="Diaria / Mensual",
        spatial_granularity="Estación / Microcuenca",
        extraction_type="socrata",
        remote_resource_id="nsz2-kzcq",
        primary_format="json",
        description="Evapotranspiración de referencia ET0 (FAO-56 Penman-Monteith / Hargreaves).",
        indicators=["ET0 referencia (mm/día)", "Requerimiento hídrico cultivo ETc", "Déficit hídrico de suelo"],
    ),

    # 10. IDEAM Radiación Solar
    "ideam_radiacion": DatasetMetadata(
        dataset_id="ideam_radiacion",
        official_name="IDEAM - Radiación Solar Global Acumulada",
        custodian="IDEAM",
        data_type="Biofísico / Energético",
        temporal_granularity="Mensual y Anual acumulada",
        spatial_granularity="Estación meteorológica puntual",
        extraction_type="socrata",
        remote_resource_id="rv9s-8nv6",
        primary_format="json",
        description="Radiación global incidente acumulada por estación (MJ/m²/día o Wh/m²).",
        indicators=["Radiación global acumulada", "Potencial fotosintético de biomasa", "Heliofanía"],
    ),
}
