"""
Cargador e Integrador Multi-Anual de SIPSA Abastecimiento (2025 -> 2019 Descendente)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Data Integration & Temporal Granularity), PEP 8, Clean Code
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SipsaMultiyearLoader:
    """
    Integra recursivamente todos los boletines y archivos cuatrimestrales/semestrales de SIPSA
    desde 2025 hasta 2019 en orden cronológico descendente.
    Normaliza el esquema canónico origen-destino y estandariza DIVIPOLA.
    """

    CANONICAL_COLUMNS = [
        "anio",
        "periodo",
        "fecha",
        "fuente_destino",
        "codigo_departamento_origen",
        "codigo_divipola_origen",
        "departamento_origen",
        "municipio_origen",
        "grupo_alimento",
        "producto",
        "cantidad_kg"
    ]

    @staticmethod
    def extract_year_from_path(file_path: Path) -> int:
        """Extrae el año numérico del nombre del archivo o directorio."""
        full_str = f"{file_path.parent.name} {file_path.name}"
        match = re.search(r"20(19|20|21|22|23|24|25|26)", full_str)
        if match:
            return int(match.group(0))
        return 2019

    @staticmethod
    def extract_period_label(file_path: Path) -> str:
        """Determina la etiqueta semestral o cuatrimestral."""
        full_str = f"{file_path.parent.name}_{file_path.name}".lower()
        if "iiicuatrim" in full_str or "iii cuatrimestre" in full_str:
            return "Cuatrimestre III"
        elif "iicuatrim" in full_str or "ii cuatrimestre" in full_str:
            return "Cuatrimestre II"
        elif "icuatrim" in full_str or "i cuatrimestre" in full_str or "c1" in full_str:
            return "Cuatrimestre I"
        elif "iisem" in full_str or "ii semestre" in full_str or "ii.semestre" in full_str:
            return "Semestre II"
        elif "isem" in full_str or "i semestre" in full_str:
            return "Semestre I"
        return "Semestre I"

    @classmethod
    def standardize_sipsa_columns(cls, df: pd.DataFrame, anio: int, periodo: str) -> pd.DataFrame:
        """Mapea las variantes de encabezados históricos de DANE SIPSA a las columnas canónicas."""
        col_map = {}
        for c in df.columns:
            c_clean = str(c).strip().lower()
            if any(k in c_clean for k in ["fuente", "mercado mayorista"]):
                col_map[c] = "fuente_destino"
            elif any(k in c_clean for k in ["fechaencuesta", "fecha"]):
                col_map[c] = "fecha"
            elif any(k in c_clean for k in ["cod. depto", "código departamento", "divipola depto"]):
                col_map[c] = "codigo_departamento_origen"
            elif any(k in c_clean for k in ["cod. municipio", "código municipio", "divipola municipio"]):
                col_map[c] = "codigo_divipola_origen"
            elif any(k in c_clean for k in ["departamento proc", "departamento"]):
                col_map[c] = "departamento_origen"
            elif any(k in c_clean for k in ["municipio proc", "municipio de colombia"]):
                col_map[c] = "municipio_origen"
            elif "grupo" in c_clean:
                col_map[c] = "grupo_alimento"
            elif any(k in c_clean for k in ["ali", "alimento", "producto"]):
                col_map[c] = "producto"
            elif any(k in c_clean for k in ["cant kg", "cantidad", "cant_kg"]):
                col_map[c] = "cantidad_kg"

        renamed = df.rename(columns=col_map)
        
        # Enriquecer con Año y Periodo
        renamed["anio"] = anio
        renamed["periodo"] = periodo

        # Normalizar fecha a formato ISO YYYY-MM-DD
        if "fecha" in renamed.columns:
            renamed["fecha"] = pd.to_datetime(renamed["fecha"], dayfirst=True, errors="coerce")

        # Asegurar columnas canónicas
        for expected in cls.CANONICAL_COLUMNS:
            if expected not in renamed.columns:
                renamed[expected] = np.nan

        # Limpiar cantidades numéricas
        renamed["cantidad_kg"] = (
            renamed["cantidad_kg"]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
        )
        renamed["cantidad_kg"] = pd.to_numeric(renamed["cantidad_kg"], errors="coerce")

        # Formatear códigos DIVIPOLA a 5 dígitos
        if "codigo_divipola_origen" in renamed.columns:
            renamed["codigo_divipola_origen"] = (
                renamed["codigo_divipola_origen"]
                .astype(str)
                .str.replace(r"\.0$", "", regex=True)
                .str.zfill(5)
            )

        return renamed[cls.CANONICAL_COLUMNS]

    @classmethod
    def load_all_years(
        cls,
        raw_sipsa_dir: Path,
        sample_per_file: int = 3000
    ) -> pd.DataFrame:
        """
        Escanea todos los archivos SIPSA de 2025 a 2019 y los consolida ordenados
        de forma descendente por año (2025 -> 2019).
        """
        all_dfs: List[pd.DataFrame] = []
        csv_files = list(raw_sipsa_dir.rglob("*.csv"))

        logger.info(f"Localizados {len(csv_files)} archivos CSV históricos de SIPSA.")

        # Ordenar archivos por año descendente
        files_with_year = [(cls.extract_year_from_path(f), f) for f in csv_files]
        files_with_year.sort(key=lambda x: x[0], reverse=True)

        for anio, file_path in files_with_year:
            periodo = cls.extract_period_label(file_path)
            try:
                # Detección de separador y codificación
                raw_df = pd.read_csv(
                    file_path,
                    sep=";",
                    encoding="latin-1",
                    nrows=sample_per_file,
                    on_bad_lines="skip"
                )
                if raw_df.shape[1] <= 1:
                    raw_df = pd.read_csv(
                        file_path,
                        sep=",",
                        encoding="latin-1",
                        nrows=sample_per_file,
                        on_bad_lines="skip"
                    )

                standard_df = cls.standardize_sipsa_columns(raw_df, anio=anio, periodo=periodo)
                standard_df = standard_df.dropna(subset=["cantidad_kg", "producto"])
                
                if len(standard_df) > 0:
                    all_dfs.append(standard_df)
                    logger.info(
                        f"SIPSA {anio} ({periodo}): {len(standard_df):,} registros extraídos de {file_path.name}"
                    )
            except Exception as e:
                logger.warning(f"Error procesando {file_path.name}: {e}")

        if not all_dfs:
            logger.error("No se pudo cargar ningún archivo SIPSA. Generando fallback.")
            return pd.DataFrame(columns=cls.CANONICAL_COLUMNS)

        master_df = pd.concat(all_dfs, ignore_index=True)

        # Ordenar estrictamente de mayor a menor año (2025 -> 2019) y por fecha
        master_df = master_df.sort_values(by=["anio", "fecha"], ascending=[False, False]).reset_index(drop=True)
        logger.info(
            f"Consolidado Multi-Anual SIPSA finalizado: {len(master_df):,} registros "
            f"desde {master_df['anio'].min()} hasta {master_df['anio'].max()}."
        )
        return master_df
