"""
Orquestador Maestro del Ciclo Completo de Ingeniería de Datos (Lakehouse Medallion)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2, SWEBOK, ISO/IEC 25010, Clean Code, PEP 8
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

APP_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_ROOT))

from src.ingestion.socrata_client import SocrataClient
from src.ingestion.pdf_extractor import PDFExtractor
from src.ingestion.file_loader import FileLoader
from src.ingestion.sipsa_multiyear_loader import SipsaMultiyearLoader
from src.cleaning.table_unwrapper import TableUnwrapper
from src.cleaning.anomaly_treatment import AnomalyTreatmentEngine
from src.database.db_manager import DatabaseManager
from src.governance.lineage import DataLineageTracker
from src.governance.data_catalog import DataCatalog
from src.lakehouse.lakehouse_manager import MedallionLakehouseManager
from src.modeling.sarimax_model import AgroModeler
from src.modeling.statistical_profiler import StatisticalProfiler
from src.modeling.geospatial_engine import GeospatialEngine
from src.visualization.plots import AgroVisualizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("AgroStatsPipeline")


def load_dataset_source(source_identifier: str, target_table: str) -> Tuple[pd.DataFrame, str]:
    """Carga y desenrolla fuentes de datos garantizando orden cronológico descendente y esquemas limpios."""
    
    # Caso 1: SIPSA Multi-Anual (2025 -> 2019 Descendente)
    if target_table == "sipsa_abastecimientos":
        sipsa_dir = APP_ROOT / "data" / "RAW" / "datosagro" / "sipsa"
        if sipsa_dir.exists():
            df_multi = SipsaMultiyearLoader.load_all_years(sipsa_dir, sample_per_file=3500)
            if not df_multi.empty:
                return df_multi, "sipsa://multiyear_longitudinal_2025_2019"
        fallback_p = APP_ROOT / "data" / "processed" / f"{target_table}.parquet"
        if fallback_p.exists():
            return pd.read_parquet(fallback_p), f"fallback://{fallback_p.name}"

    # Caso 2: DANE IPC Desenrollado Longitudinal
    if target_table == "dane_ipc":
        full_p = APP_ROOT / source_identifier
        raw_ipc = FileLoader.load_file(str(full_p)) if full_p.exists() else pd.read_parquet(APP_ROOT / "data" / "processed" / "dane_ipc.parquet")
        df_tidy = TableUnwrapper.unwrap_dane_ipc(raw_ipc)
        return df_tidy, f"file://{source_identifier}#unwrapped_longitudinal"

    # Caso 3: DANE Cuenta Satélite Agroindustria (CSAA)
    if target_table == "dane_csaa":
        full_p = APP_ROOT / source_identifier
        raw_csaa = FileLoader.load_file(str(full_p)) if full_p.exists() else pd.read_parquet(APP_ROOT / "data" / "processed" / "dane_csaa.parquet")
        df_csaa = TableUnwrapper.unwrap_dane_csaa(raw_csaa)
        return df_csaa, f"file://{source_identifier}#unwrapped_csaa"

    # Caso 4: Landing Leads Store Deserializado
    if target_table == "landing_leads":
        candidates = [
            APP_ROOT.parent.parent / "Statsfirm" / "landing_page" / "data" / "leadsStore.js",
            APP_ROOT.parent.parent / "Statsfirm" / "Statsfirm" / "landing_page" / "data" / "leadsStore.js",
            Path("C:/Users/ADAN/OneDrive/Documentos/Statsfirm/Statsfirm/landing_page/data/leadsStore.js")
        ]
        for c in candidates:
            if c.exists():
                return TableUnwrapper.unwrap_leads_store(c), f"file://{c.name}#deserialized_pii_masked"
        fallback_p = APP_ROOT / "data" / "processed" / f"{target_table}.parquet"
        if fallback_p.exists():
            return pd.read_parquet(fallback_p), f"fallback://{fallback_p.name}"

    # Caso 5: API Socrata (57sv-p2fu)
    if source_identifier == "57sv-p2fu":
        try:
            client = SocrataClient(resource_id="57sv-p2fu")
            df = client.fetch_all(max_records=1000)
            if not df.empty:
                return df, f"socrata://datos.gov.co/{source_identifier}"
        except Exception as e:
            logger.warning(f"Extracción Socrata no disponible ({e}). Usando fallback procesado...")
        fallback_p = APP_ROOT / "data" / "processed" / f"{target_table}.parquet"
        if fallback_p.exists():
            return pd.read_parquet(fallback_p), f"fallback://{fallback_p.name}"

    # Caso 6: Archivo PDF Documentación
    if source_identifier.endswith(".pdf"):
        pdf_path = APP_ROOT / source_identifier
        if pdf_path.exists():
            extractor = PDFExtractor(str(pdf_path))
            return pd.DataFrame(extractor.extract_chunks()), f"file://{pdf_path.name}"
        fallback_p = APP_ROOT / "data" / "processed" / f"{target_table}.parquet"
        if fallback_p.exists():
            return pd.read_parquet(fallback_p), f"fallback://{fallback_p.name}"

    # Caso 7: Archivos de disco tabulares estándar
    full_p = APP_ROOT / source_identifier
    if full_p.exists():
        return FileLoader.load_file(str(full_p)), f"file://{full_p.relative_to(APP_ROOT)}"
    
    fallback_p = APP_ROOT / "data" / "processed" / f"{target_table}.parquet"
    if fallback_p.exists():
        return pd.read_parquet(fallback_p), f"fallback://{fallback_p.name}"
        
    return pd.DataFrame([{"id": 1, "valor": 100}]), f"mock://empty_fallback"


def run_pipeline():
    start_time = time.time()
    logger.info("================================================================================")
    logger.info("  AGRODATA INTELLIGENCE PLATFORM — ORQUESTADOR DE INGENIERÍA DE DATOS (PDCO)  ")
    logger.info("  Arquitectura: Medallion Lakehouse (Bronze -> Silver -> Gold) | DAMA-DMBOK 2   ")
    logger.info("  Integración Temporal: SIPSA 2025 -> 2019 Descendente | DANE DIVIPOLA 5-Dígitos")
    logger.info("================================================================================")

    db_path = APP_ROOT / "data" / "processed" / "agrostats_lakehouse.db"
    db_mgr = DatabaseManager(str(db_path))
    tracker = DataLineageTracker()
    catalog = DataCatalog()
    lakehouse = MedallionLakehouseManager(APP_ROOT, db_mgr)
    reports_dir = APP_ROOT / "docs" / "quality_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    pipeline_configs = [
        {
            "folder": "01_sipsa_abastecimientos",
            "source": "data/RAW/datosagro/sipsa/2019_SemI/2019_SemI.csv",
            "table": "sipsa_abastecimientos",
            "domain": "Abastecimiento Agroalimentario",
            "description": "Serie multi-anual consolidada (2025-2019) de flujos de carga origen-destino (DANE SIPSA).",
            "granularity": "Año x Mes x Municipio Origen (DIVIPOLA) x Central Destino",
            "primary_keys": ["anio", "fecha", "codigo_divipola_origen", "producto"],
            "pii_cols": [],
            "range_rules": {"cantidad_kg": (0.0, 1000000.0)}
        },
        {
            "folder": "02_sipsa_precios",
            "source": "data/processed/sipsa_precios.parquet",
            "table": "sipsa_precios",
            "domain": "Precios Mayoristas",
            "description": "Cotizaciones mayoristas diarias desenrolladas por central de abastos (DANE SIPSA).",
            "granularity": "Fecha x Mercado Mayorista x Producto",
            "primary_keys": ["producto"],
            "pii_cols": [],
            "range_rules": {"bogota_corabastos_precio": (0.0, 500000.0)}
        },
        {
            "folder": "03_sipsa_insumos",
            "source": "data/processed/sipsa_insumos.parquet",
            "table": "sipsa_insumos",
            "domain": "Costos e Insumos",
            "description": "Índices y precios mayoristas de fertilizantes y plaguicidas agrícolas.",
            "granularity": "Mes x Insumo Químico",
            "primary_keys": ["fecha"],
            "pii_cols": [],
            "range_rules": {"indice_total": (0.0, 10000.0)}
        },
        {
            "folder": "04_dane_ipc_ipp",
            "source": "data/processed/dane_ipc.parquet",
            "table": "dane_ipc",
            "domain": "Macroeconomía Agraria",
            "description": "Serie longitudinal (2003-2026) del Índice de Precios al Consumidor (IPC Alimentos).",
            "granularity": "Año x Mes (Longitudinal)",
            "primary_keys": ["anio", "mes_num"],
            "pii_cols": [],
            "range_rules": {"ipc_alimentos": (0.0, 500.0)}
        },
        {
            "folder": "05_ideam_climatologia",
            "source": "data/processed/ideam_pluviometria.parquet",
            "table": "ideam_pluviometria",
            "domain": "Hidrometeorología Agrícola",
            "description": "Registros pluviométricos y precipitación acumulada por estación meteorológica.",
            "granularity": "Fecha x Estación x Código DIVIPOLA",
            "primary_keys": ["codigoestacion", "fechaobservacion"],
            "pii_cols": [],
            "range_rules": {"valorobservado": (0.0, 1000.0)}
        },
        {
            "folder": "06_ideam_telemetria_57sv",
            "source": "57sv-p2fu",
            "table": "ideam_telemetria_realtime",
            "domain": "Telemetría en Tiempo Real",
            "description": "Observaciones sensoricas continuas de estaciones IDEAM (API 57sv-p2fu).",
            "granularity": "Timestamp x Código Sensor x DIVIPOLA",
            "primary_keys": ["codigoestacion", "fechaobservacion"],
            "pii_cols": [],
            "range_rules": {"valorobservado": (-10.0, 1000.0)}
        },
        {
            "folder": "07_dane_satelite_csaa",
            "source": "data/RAW/datosagro/satelite/anex-CSAA-2024.xlsx",
            "table": "dane_csaa",
            "domain": "Cuentas Nacionales",
            "description": "Cuenta Satélite de la Agroindustria: Valor Agregado Bruto (VAB) por fase productiva.",
            "granularity": "Código Cuadro x Cadena Agropecuaria",
            "primary_keys": ["codigo_cuadro"],
            "pii_cols": [],
            "range_rules": {}
        },
        {
            "folder": "08_boletin_pdf_webservice",
            "source": "data/RAW/datosagro/DANE-webservice-SIPSA.pdf",
            "table": "doc_webservice_chunks",
            "domain": "Documentación No Estructurada",
            "description": "Fragmentos procesados de la especificación técnica DANE WebService SIPSA.",
            "granularity": "Documento x Chunk ID",
            "primary_keys": ["chunk_id"],
            "pii_cols": [],
            "range_rules": {}
        },
        {
            "folder": "09_landing_leads_store",
            "source": "leadsStore",
            "table": "landing_leads",
            "domain": "Customer & Commercial Analytics",
            "description": "Prospectos de productores y clientes con seudonimización SHA-256 (Ley 1581).",
            "granularity": "ID Lead x Timestamp Registro",
            "primary_keys": ["id"],
            "pii_cols": ["email", "phone", "contactname"],
            "range_rules": {}
        }
    ]

    silver_datasets: Dict[str, pd.DataFrame] = {}

    for cfg in pipeline_configs:
        dataset_name = cfg["table"]
        logger.info(f"\n>>> [ETAPAS BRONZE & SILVER] Procesando: {dataset_name} ({cfg['domain']})")

        # 1. Ingesta Multi-Fuente y Desenrollado
        raw_df, source_uri = load_dataset_source(cfg["source"], cfg["table"])
        logger.info(f"   [Ingesta] Extraídos {len(raw_df):,} registros desde {source_uri}")

        # 2. Capa Bronze (Inmutable con Hash SHA-256)
        bronze_df = lakehouse.process_bronze(
            raw_df=raw_df,
            dataset_id=dataset_name,
            source_uri=source_uri,
            tracker=tracker
        )

        # 3. Capa Silver (Sanitización + PII + DIVIPOLA + Quality Gate)
        silver_df, dq_report = lakehouse.process_silver(
            bronze_df=bronze_df,
            dataset_id=dataset_name,
            tracker=tracker,
            catalog=catalog,
            domain=cfg["domain"],
            description=cfg["description"],
            granularity=cfg["granularity"],
            primary_keys=[pk for pk in cfg["primary_keys"] if pk in raw_df.columns or pk in silver_df.columns],
            pii_columns=cfg["pii_cols"],
            range_rules=cfg["range_rules"]
        )

        # 4. Tratamiento Estadístico de Anomalías
        if dataset_name == "sipsa_abastecimientos" and "cantidad_kg" in silver_df.columns:
            silver_df, qty_anom = AnomalyTreatmentEngine.treat_quantity_anomalies(silver_df, "cantidad_kg")
            # Enriquecimiento Geoespacial DIVIPOLA y cálculo de distancias
            silver_df = GeospatialEngine.enrich_with_divipola_coordinates(silver_df)
            silver_df = GeospatialEngine.calculate_origin_destination_distances(silver_df)
            GeospatialEngine.plot_origin_destination_flows(
                silver_df,
                reports_dir / "sipsa_od_flows.png"
            )

        if dataset_name == "sipsa_precios":
            price_cols = [c for c in silver_df.columns if "precio" in c]
            if price_cols:
                silver_df, p_anom = AnomalyTreatmentEngine.treat_price_anomalies(silver_df, price_cols[0])

        silver_datasets[dataset_name] = silver_df
        logger.info(
            f"   [Silver Quality Gate] Score: {dq_report.overall_score * 100:.1f}% | "
            f"Estado: {dq_report.status} | Registros: {len(silver_df):,}"
        )

        # 5. Rigor Estadístico: Perfilado de Ausencias (Missingno) y Distribuciones
        num_cols = silver_df.select_dtypes(include=["number"]).columns
        if len(num_cols) > 0 and len(silver_df) >= 10:
            target_col = num_cols[0]
            # Momentos duales y bondad de ajuste
            moments = StatisticalProfiler.calculate_dual_moments(silver_df[target_col])
            dist_fit = StatisticalProfiler.fit_distributions(silver_df[target_col])
            norm_test = StatisticalProfiler.test_normality(silver_df[target_col])
            
            logger.info(
                f"   [Rigor Estadístico] '{target_col}' -> Media: {moments.get('media_parametrica', 0):,.2f}, "
                f"Mediana: {moments.get('mediana_robusta', 0):,.2f}, Mejor Ajuste: {dist_fit.get('mejor_distribucion', 'N/A')}"
            )

            # Generar gráfico de rigor estadístico (Histograma + KDE + QQ-Plot + Boxplot)
            dist_plot_file = reports_dir / f"{dataset_name}_dist_profile.png"
            StatisticalProfiler.plot_statistical_distribution(
                silver_df[target_col], target_col, dist_plot_file
            )

            # Nelson SPC Rules
            anomalies = AgroModeler.detect_nelson_anomalies(silver_df[target_col].dropna())
            logger.info(f"   [SPC Nelson Rules] Detectadas {anomalies.sum()} anomalías estadísticas.")

        # Matriz Missingno
        missingno_plot_file = reports_dir / f"{dataset_name}_missingno.png"
        StatisticalProfiler.plot_missingness_profile(
            silver_df, dataset_name, missingno_plot_file
        )

    # 6. Capa Gold (Data Marts y Preguntas de Negocio A1-J1)
    logger.info("\n>>> [ETAPA GOLD] Construyendo Data Marts Analíticos...")
    gold_marts = lakehouse.build_gold_marts(silver_datasets, tracker, catalog)

    # 7. Optimización final de base de datos
    db_mgr.optimize()

    # 8. Exportar Linaje, DAG Mermaid y Catálogo de Datos
    manifest_file = APP_ROOT / "docs" / "lineage" / "pipeline_run_manifest.json"
    mermaid_file = APP_ROOT / "docs" / "lineage" / "lineage_dag.md"
    tracker.save_artifacts(manifest_file, mermaid_file)

    catalog_json = APP_ROOT / "docs" / "dictionaries" / "data_catalog.json"
    catalog_md = APP_ROOT / "docs" / "dictionaries" / "data_catalog.md"
    catalog.export_catalog(catalog_json, catalog_md)

    # 9. Actualizar metadata.json con trazabilidad transversal
    elapsed_total = round(time.time() - start_time, 2)
    meta_path = APP_ROOT / "metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["last_updated"] = time.strftime("%Y-%m-%d")
            meta["version"] = "1.5.0"
            meta["pdco_phase"] = "DEVELOPMENT"
            meta["active_skill"] = "03-development"
            meta["data_engineering_stats"] = {
                "execution_time_seconds": elapsed_total,
                "total_datasets_processed": len(pipeline_configs),
                "total_gold_marts_created": len(gold_marts),
                "lakehouse_db": "data/processed/agrostats_lakehouse.db",
                "quality_reports_dir": "docs/quality_reports/",
                "lineage_manifest": "docs/lineage/pipeline_run_manifest.json",
                "data_catalog": "docs/dictionaries/data_catalog.md"
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            logger.warning(f"No se pudo actualizar metadata.json: {e}")

    logger.info("================================================================================")
    logger.info(f"  PIPELINE EJECUTADO CON ÉXITO EN {elapsed_total:.2f}s  ")
    logger.info(f"  Base de datos Lakehouse: {db_path.name} ({len(db_mgr.list_tables())} tablas)")
    logger.info(f"  Manifiesto de linaje: {manifest_file.relative_to(APP_ROOT)}")
    logger.info(f"  Catálogo DAMA-DMBOK 2: {catalog_md.relative_to(APP_ROOT)}")
    logger.info("================================================================================")


if __name__ == "__main__":
    run_pipeline()
