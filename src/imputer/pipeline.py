"""
Pipeline Orquestador de Ingesta y Persistencia Inmutable en data/RAW
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Linaje de Datos y Auditoría SHA-256), SWEBOK
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from .config import DEFAULT_RAW_DIR, TOP_RAW_DIR, DEFAULT_BATCH_LIMIT, SAMPLE_BATCH_LIMIT
from .ingestion.base_client import ResilientHttpClient
from .ingestion.socrata_client import SocrataClient
from .ingestion.dane_scraper import DaneScraper
from .ingestion.dataset_registry import DATASET_REGISTRY, DatasetMetadata
from .imputation.imputation_engine import IntelligentImputer

logger = logging.getLogger(__name__)


def calculate_sha256(filepath: Path) -> str:
    """Calcula el hash SHA-256 para garantizar inmutabilidad (DAMA-DMBOK 2)."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class AgroDataIngestionPipeline:
    """
    Orquestador maestro para la ingesta automatizada desde internet de las 10 fuentes
    agropecuarias y su almacenamiento estandarizado en data/RAW.
    """

    def __init__(
        self,
        raw_dir: Optional[Path] = None,
        socrata_app_token: Optional[str] = None,
    ) -> None:
        self.raw_dir = Path(raw_dir or DEFAULT_RAW_DIR)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
        # También asegurar que la carpeta hermana exista para compatibilidad
        self.top_raw_dir = Path(TOP_RAW_DIR)
        self.top_raw_dir.mkdir(parents=True, exist_ok=True)

        self.http_client = ResilientHttpClient()
        self.socrata_client = SocrataClient(app_token=socrata_app_token, http_client=self.http_client)
        self.dane_scraper = DaneScraper(http_client=self.http_client)
        self.imputer = IntelligentImputer()

    def _save_payload(
        self,
        dataset_id: str,
        df: Optional[pd.DataFrame] = None,
        source_file: Optional[Path] = None,
        metadata: Optional[DatasetMetadata] = None,
    ) -> Dict[str, Any]:
        """
        Persiste el dataset en data/RAW tanto en CSV como en JSON y registra el hash SHA-256.
        """
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        saved_files: List[str] = []

        if df is not None:
            csv_path = self.raw_dir / f"{dataset_id}_{timestamp_str}.csv"
            json_path = self.raw_dir / f"{dataset_id}_{timestamp_str}.json"

            df.to_csv(csv_path, index=False, encoding="utf-8")
            df.to_json(json_path, orient="records", date_format="iso", indent=2)

            # Replicar en TOP_RAW_DIR para interoperabilidad transparente
            try:
                df.to_csv(self.top_raw_dir / f"{dataset_id}_{timestamp_str}.csv", index=False, encoding="utf-8")
            except Exception:
                pass

            file_hash = calculate_sha256(csv_path)
            row_count = len(df)
            columns = list(df.columns)
            saved_files.extend([csv_path.name, json_path.name])
        elif source_file and source_file.exists():
            dest_path = self.raw_dir / f"{dataset_id}_{timestamp_str}_{source_file.name}"
            with open(source_file, "rb") as sf, open(dest_path, "wb") as df_out:
                df_out.write(sf.read())

            file_hash = calculate_sha256(dest_path)
            row_count = -1
            columns = []
            saved_files.append(dest_path.name)

            # Si es Excel, intentar parsear a CSV para disponibilidad inmediata
            if dest_path.suffix.lower() in [".xlsx", ".xls"]:
                try:
                    parsed_df = pd.read_excel(dest_path)
                    csv_partner = self.raw_dir / f"{dataset_id}_{timestamp_str}.csv"
                    parsed_df.to_csv(csv_partner, index=False, encoding="utf-8")
                    saved_files.append(csv_partner.name)
                    row_count = len(parsed_df)
                    columns = list(parsed_df.columns)
                except Exception as e:
                    logger.debug("No se pudo auto-convertir %s a CSV: %s", dest_path.name, e)
        else:
            raise ValueError(f"No se proporcionó ni DataFrame ni archivo para {dataset_id}")

        manifest_entry = {
            "dataset_id": dataset_id,
            "official_name": metadata.official_name if metadata else dataset_id,
            "custodian": metadata.custodian if metadata else "UNKNOWN",
            "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": file_hash,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
            "files": saved_files,
            "storage_path": str(self.raw_dir),
        }

        return manifest_entry

    def ingest_dataset(
        self,
        dataset_id: str,
        limit: int = DEFAULT_BATCH_LIMIT,
    ) -> Dict[str, Any]:
        """
        Ejecuta la descarga de un conjunto de datos específico según su contrato de extracción.
        """
        if dataset_id not in DATASET_REGISTRY:
            raise KeyError(f"Dataset '{dataset_id}' no encontrado en el catálogo DATASET_REGISTRY.")

        meta = DATASET_REGISTRY[dataset_id]
        logger.info("Iniciando ingesta para [%s] - %s", dataset_id, meta.official_name)

        # 1. Estrategia Socrata (datos.gov.co / IDEAM)
        if meta.extraction_type == "socrata" and meta.remote_resource_id:
            df = self.socrata_client.fetch_dataframe(
                resource_id=meta.remote_resource_id,
                max_records=limit,
            )
            return self._save_payload(dataset_id=dataset_id, df=df, metadata=meta)

        # 2. Estrategia DANE Scraper (SIPSA Precios, Abastecimiento, Insumos, IPP, IPC)
        if meta.extraction_type == "dane_scrape":
            urls: List[str] = []
            if dataset_id == "sipsa_precios":
                urls = self.dane_scraper.get_latest_sipsa_precios_urls()
            elif dataset_id == "sipsa_abastecimientos":
                urls = self.dane_scraper.get_sipsa_abastecimiento_urls()
            elif dataset_id == "dane_ipp":
                urls = self.dane_scraper.get_ipp_urls()
            elif dataset_id == "dane_ipc":
                urls = self.dane_scraper.get_ipc_urls()

            # Descargar la primera URL disponible
            for url in urls:
                try:
                    filename = Path(url.split("?")[0]).name
                    temp_dest = self.raw_dir / f"temp_{filename}"
                    self.dane_scraper.download_to(url, temp_dest)
                    manifest = self._save_payload(
                        dataset_id=dataset_id, source_file=temp_dest, metadata=meta
                    )
                    temp_dest.unlink(missing_ok=True)
                    return manifest
                except Exception as exc:
                    logger.warning("Fallo al descargar URL %s: %s. Probando siguiente...", url, exc)

            raise RuntimeError(f"No se pudo descargar ningún archivo oficial para {dataset_id}")

        raise NotImplementedError(f"Estrategia '{meta.extraction_type}' no soportada para {dataset_id}")

    def ingest_all_sources(
        self,
        limit_per_socrata: int = SAMPLE_BATCH_LIMIT,
    ) -> Dict[str, Any]:
        """
        Automatiza la ingesta completa de las 10 fuentes oficiales y escribe el manifiesto maestro.
        """
        manifest_entries: List[Dict[str, Any]] = []
        errors: Dict[str, str] = {}

        for dataset_id in DATASET_REGISTRY.keys():
            try:
                entry = self.ingest_dataset(dataset_id=dataset_id, limit=limit_per_socrata)
                manifest_entries.append(entry)
                logger.info("Ingesta completada para %s", dataset_id)
            except Exception as exc:
                logger.error("Error durante ingesta de %s: %s", dataset_id, exc)
                errors[dataset_id] = str(exc)

        # Actualizar manifiesto global en data/RAW
        manifest_path = self.raw_dir / "raw_manifest.json"
        full_manifest = {
            "pipeline_run_at_utc": datetime.now(timezone.utc).isoformat(),
            "sources_attempted": len(DATASET_REGISTRY),
            "sources_successful": len(manifest_entries),
            "sources_failed": len(errors),
            "datasets": manifest_entries,
            "errors": errors,
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(full_manifest, f, indent=2, ensure_ascii=False)

        # Replicar en TOP_RAW_DIR
        try:
            with open(self.top_raw_dir / "raw_manifest.json", "w", encoding="utf-8") as f:
                json.dump(full_manifest, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        logger.info("Manifiesto de ingesta guardado en: %s", manifest_path)
        return full_manifest
