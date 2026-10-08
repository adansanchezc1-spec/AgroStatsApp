"""Gestor de Landing Inmutable para la Capa Bronze.
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 / SWEBOK v4
Persistencia en Parquet con cálculo de hash SHA-256 y manifiesto de linaje.
"""

from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("ingestion.landing_manager")


class LandingManager:
    """Administrador de persistencia inmutable para la zona Bronze."""

    def __init__(self, raw_base_dir: Optional[Path] = None) -> None:
        self.raw_dir = raw_base_dir or settings.RAW_DIR
        self.manifest_file = self.raw_dir / "manifest.json"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Crea las carpetas base de fuentes si no existen."""
        for category in ["ica", "ideam", "dane", "upra"]:
            (self.raw_dir / category).mkdir(parents=True, exist_ok=True)

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calcula el hash criptográfico SHA-256 de un archivo en disco."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def load_manifest(self) -> Dict[str, Any]:
        """Carga el manifiesto de linaje y hashes desde disco."""
        if not self.manifest_file.exists():
            return {"version": "1.0.0", "updated_at": "", "datasets": {}}
        try:
            with open(self.manifest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error("Error al leer el manifiesto: %s. Creando nuevo manifiesto.", exc)
            return {"version": "1.0.0", "updated_at": "", "datasets": {}}

    def _save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Persiste el manifiesto en disco."""
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def save_raw_dataset(
        self,
        df: pd.DataFrame,
        source_category: str,
        filename: str,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """
        Guarda un DataFrame en formato Parquet comprimido con Snappy,
        calcula su hash SHA-256 y registra la extracción en el manifiesto.
        """
        if df.empty:
            logger.warning("Intentando guardar un DataFrame vacío para %s/%s", source_category, filename)

        category_dir = self.raw_dir / source_category.lower()
        category_dir.mkdir(parents=True, exist_ok=True)
        
        target_name = filename if filename.endswith(".parquet") else f"{filename}.parquet"
        target_path = category_dir / target_name

        # Regla de Inmutabilidad
        if target_path.exists() and not overwrite:
            existing_sha256 = self._calculate_sha256(target_path)
            logger.info("Archivo inmutable existente en %s (SHA-256: %s...). Omitiendo sobrescritura.", target_path, existing_sha256[:10])
            manifest = self.load_manifest()
            entry = manifest.get("datasets", {}).get(f"{source_category}/{target_name}")
            if entry:
                return entry
            return {
                "file_path": str(target_path),
                "sha256": existing_sha256,
                "rows": len(df),
                "status": "EXISTING_UNCHANGED",
            }

        # Guardar en Parquet con compresión Snappy
        df.to_parquet(target_path, engine="pyarrow", compression="snappy", index=False)
        sha256_digest = self._calculate_sha256(target_path)
        file_size = target_path.stat().st_size

        metadata_entry = {
            "source_category": source_category,
            "filename": target_name,
            "file_path": str(target_path),
            "rows": len(df),
            "columns": list(df.columns),
            "size_bytes": file_size,
            "sha256": sha256_digest,
            "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        }

        # Actualizar manifiesto
        manifest = self.load_manifest()
        manifest["datasets"][f"{source_category}/{target_name}"] = metadata_entry
        self._save_manifest(manifest)

        logger.info("Dataset guardado en Bronze: %s (%d filas, %d bytes, SHA256: %s...)", target_path.name, len(df), file_size, sha256_digest[:10])
        return metadata_entry

    def verify_integrity(self) -> Dict[str, bool]:
        """Comprueba que todos los archivos registrados en el manifiesto conserven su hash intacto."""
        manifest = self.load_manifest()
        integrity_results: Dict[str, bool] = {}

        for key, entry in manifest.get("datasets", {}).items():
            path = Path(entry["file_path"])
            if not path.exists():
                logger.error("Archivo faltante en disco: %s", path)
                integrity_results[key] = False
                continue

            current_hash = self._calculate_sha256(path)
            is_valid = current_hash == entry["sha256"]
            integrity_results[key] = is_valid
            if not is_valid:
                logger.critical("¡VIOLACIÓN DE INMUTABILIDAD! El archivo %s ha sido alterado.", path)

        return integrity_results
