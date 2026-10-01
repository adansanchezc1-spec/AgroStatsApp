"""
Orquestador Maestro del Ciclo Completo de Datos (Fases 01 a 08 por Dataset)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2, SWEBOK, ISO/IEC 25010
"""

import os
import sys
import json
import logging
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.ingestion.socrata_client import SocrataClient
from src.ingestion.pdf_extractor import PDFExtractor
from src.ingestion.file_loader import FileLoader
from src.cleaning.sanitizer import DataSanitizer
from src.cleaning.pii_handler import PIIHandler
from src.validation.schemas import DataValidator, QualityGateError
from src.database.db_manager import DatabaseManager
from src.modeling.sarimax_model import AgroModeler
from src.visualization.plots import AgroVisualizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

APP_ROOT = Path(__file__).resolve().parent

def generate_notebooks(dataset_name: str):
    """Genera los 8 notebooks de documentación y narración en notebooks/<dataset_name>/."""
    nb_dir = APP_ROOT / "notebooks" / dataset_name
    nb_dir.mkdir(parents=True, exist_ok=True)
    
    phases = [
        "01_entendimiento_documentacion",
        "02_ingestion",
        "03_exploracion_informatica_y_estadistica",
        "04_ingestion_como_dataframe",
        "05_limpieza_wrangling_governance",
        "06_modelo_base_de_datos",
        "07_modeling_and_integration",
        "08_visualization"
    ]
    
    for p in phases:
        nb_file = nb_dir / f"{p}.ipynb"
        if not nb_file.exists():
            nb_content = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [
                            f"# {p.upper()} - {dataset_name}\n",
                            f"**Proyecto**: AgroStatsApp  \n",
                            f"**Fase PDCO**: DEVELOPMENT | **DAMA-BOK Stage**: {p}\n\n",
                            f"Notebook ejecutable narrado del ciclo de vida de datos para `{dataset_name}`."
                        ]
                    }
                ],
                "metadata": {
                    "language_info": {"name": "python"}
                },
                "nbformat": 4,
                "nbformat_minor": 2
            }
            with open(nb_file, "w", encoding="utf-8") as f:
                json.dump(nb_content, f, indent=2)

def run_lifecycle():
    logger.info("=== INICIANDO EJECUCIÓN MAESTRA DEL CICLO DE DATOS (FASES 01 - 08) ===")
    
    db_mgr = DatabaseManager(str(APP_ROOT / "data" / "processed" / "agrostats_lakehouse.db"))
    
    # Lista de datasets a procesar con sus fuentes verificadas
    datasets_to_process = [
        ("01_sipsa_abastecimientos", "data/RAW/datosagro/sipsa/2019_SemI/2019_SemI.csv", "sipsa_abastecimientos"),
        ("02_sipsa_precios", "data/processed/sipsa_precios.parquet", "sipsa_precios"),
        ("03_sipsa_insumos", "data/processed/sipsa_insumos.parquet", "sipsa_insumos"),
        ("04_dane_ipc_ipp", "data/processed/dane_ipc.parquet", "dane_ipc"),
        ("05_ideam_climatologia", "data/processed/ideam_pluviometria.parquet", "ideam_pluviometria"),
        ("06_ideam_telemetria_57sv", "57sv-p2fu", "ideam_telemetria_realtime"),
        ("07_dane_satelite_csaa", "data/RAW/datosagro/satelite/anex-CSAA-2024.xlsx", "dane_csaa"),
        ("08_boletin_pdf_webservice", "data/RAW/datosagro/DANE-webservice-SIPSA.pdf", "doc_webservice_chunks"),
        ("09_landing_leads_store", "leadsStore", "landing_leads")
    ]
    
    inventory_summary = []
    
    for ds_folder, source_path, target_table in datasets_to_process:
        logger.info(f"\n--- PROCESANDO DATASET: {ds_folder} ---")
        
        # 1. Generar notebooks
        generate_notebooks(ds_folder)
        
        # 2. Ingesta (Fase 02)
        if source_path == "57sv-p2fu":
            client = SocrataClient(resource_id="57sv-p2fu")
            raw_df = client.fetch_all(max_records=1000)
        elif source_path.endswith(".pdf"):
            extractor = PDFExtractor(str(APP_ROOT / source_path))
            chunks = extractor.extract_chunks()
            raw_df = pd.DataFrame(chunks)
        elif source_path == "leadsStore":
            target_p = APP_ROOT.parent.parent / "Statsfirm" / "landing_page" / "data" / "leadsStore.js"
            raw_df = FileLoader.load_file(str(target_p))
        else:
            full_p = APP_ROOT / source_path
            raw_df = FileLoader.load_file(str(full_p))
            
        logger.info(f"Fase 02 Ingesta: {len(raw_df)} registros extraídos.")
        
        # 3. Exploración & Sanitización (Fase 03 & 05)
        clean_df = DataSanitizer.sanitize_dataframe(raw_df)
        
        # Aplicar seudonimización si aplica PII
        if "email" in clean_df.columns or "phone" in clean_df.columns:
            clean_df = PIIHandler.sanitize_pii(clean_df, ["email", "phone"])
            
        # 4. Validar Esquema (Fase 04 Quality Gate)
        cols_to_check = list(clean_df.columns[:2])
        DataValidator.validate_schema(clean_df, required_columns=cols_to_check)
        
        # 5. Persistencia en processed Parquet y SQL (Fase 05 & 06)
        parquet_path = APP_ROOT / "data" / "processed" / f"{target_table}.parquet"
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_parquet(parquet_path, index=False)
        
        rows_saved = db_mgr.save_dataframe(clean_df, target_table, mode="replace")
        
        # 6. Modelado / Inferencia (Fase 07)
        numeric_cols = clean_df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            anomalies = AgroModeler.detect_nelson_anomalies(clean_df[numeric_cols[0]].dropna())
            logger.info(f"Fase 07 Modelado SPC: {anomalies.sum()} anomalías en {numeric_cols[0]}")
            
        # 7. Visualización (Fase 08)
        if len(numeric_cols) > 0:
            plot_file = APP_ROOT / "docs" / "quality_reports" / f"{target_table}_plot.png"
            clean_df["idx"] = range(len(clean_df))
            AgroVisualizer.plot_time_series(
                clean_df.head(100), "idx", numeric_cols[0],
                f"Distribución {numeric_cols[0]} - {target_table}",
                str(plot_file)
            )
            
        inventory_summary.append({
            "dataset": ds_folder,
            "table": target_table,
            "raw_rows": len(raw_df),
            "cleaned_rows": len(clean_df),
            "parquet_saved": str(parquet_path.relative_to(APP_ROOT)),
            "status": "COMPLETED"
        })
        
    logger.info("\n=== EJECUCIÓN MAESTRA FINALIZADA CON ÉXITO DE TODOS LOS DATASETS ===")
    
    # Guardar manifest final de gobernanza
    manifest_path = APP_ROOT / "docs" / "lineage" / "execution_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(inventory_summary, f, indent=2)
    logger.info(f"Manifest de gobernanza guardado en: {manifest_path}")

if __name__ == "__main__":
    run_lifecycle()
