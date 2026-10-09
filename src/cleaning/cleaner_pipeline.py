"""Pipeline Orquestador de Limpieza y Saneamiento (Capa Silver).
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 / Clean Architecture
Ejecución secuencial de sanitización, deduplicación y tipado estricto.
"""

from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

from src.config.settings import settings
from src.utils.logger import get_logger
from src.cleaning.transformers import (
    sanitize_text,
    cast_datatypes,
    handle_missing_values,
    deduplicate_dataset,
)

logger = get_logger("cleaning.cleaner_pipeline")


class CleanerPipeline:
    """Orquestador de saneamiento de datos desde Bronze hacia Silver."""

    def __init__(self, cleaned_base_dir: Optional[Path] = None) -> None:
        self.cleaned_dir = cleaned_base_dir or settings.CLEANED_DIR
        self.cleaned_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def clean_eva_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """Sanea y normaliza el dataset de Evaluaciones Agropecuarias Municipales."""
        if df.empty:
            return df.copy()

        df_out = df.copy()
        
        # 1. Normalización de nombres de columnas
        rename_map = {
            "c_d_dep": "cod_departamento",
            "c_d_mun": "cod_municipio",
            "a_o": "anio",
            "desagregaci_n_regional_y": "variedad",
            "rea_sembrada_ha": "area_sembrada_ha",
            "rea_cosechada_ha": "area_cosechada_ha",
            "producci_n_t": "produccion_ton",
            "rendimiento_t_ha": "rendimiento_ton_ha",
        }
        df_out = df_out.rename(columns={k: v for k, v in rename_map.items() if k in df_out.columns})

        # 2. Sanitización de texto
        text_cols = ["departamento", "municipio", "cultivo", "variedad", "grupo_de_cultivo"]
        for col in text_cols:
            if col in df_out.columns:
                df_out[col] = df_out[col].apply(sanitize_text)

        # 3. Imputación de variedades faltantes
        if "variedad" in df_out.columns:
            df_out = handle_missing_values(df_out, categorical_cols=["variedad"], default_fill="SIN_VARIEDAD_ESPECIFICADA")

        # 4. Tipado estricto
        type_schema = {
            "cod_departamento": "string",
            "cod_municipio": "string",
            "anio": "int64",
            "area_sembrada_ha": "float64",
            "area_cosechada_ha": "float64",
            "produccion_ton": "float64",
            "rendimiento_ton_ha": "float64",
        }
        df_out = cast_datatypes(df_out, type_schema)

        # 5. Deduplicación temporal
        keys = ["cod_municipio", "anio", "cultivo", "variedad"]
        if "periodo" in df_out.columns:
            keys.append("periodo")
        df_out = deduplicate_dataset(df_out, subset_keys=keys)

        return df_out

    @staticmethod
    def clean_ideam_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """Sanea y normaliza series meteorológicas de IDEAM."""
        if df.empty:
            return df.copy()

        df_out = df.copy()

        rename_map = {
            "codigoestacion": "codigo_estacion",
            "nombreestacion": "nombre_estacion",
            "fechaobservacion": "fecha_observacion",
            "valorobservado": "valor_observado",
            "descripcionsensor": "sensor_descripcion",
            "unidadmedida": "unidad_medida",
        }
        df_out = df_out.rename(columns={k: v for k, v in rename_map.items() if k in df_out.columns})

        if "sensor_descripcion" in df_out.columns:
            df_out["sensor_descripcion"] = df_out["sensor_descripcion"].apply(sanitize_text)

        type_schema = {
            "codigo_estacion": "string",
            "fecha_observacion": "datetime64[ns]",
            "valor_observado": "float64",
        }
        df_out = cast_datatypes(df_out, type_schema)

        keys = ["codigo_estacion", "fecha_observacion", "sensor_descripcion"]
        df_out = deduplicate_dataset(df_out, subset_keys=keys)

        return df_out

    @staticmethod
    def clean_sipsa_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """Sanea y normaliza series de insumos y precios SIPSA / DANE."""
        if df.empty:
            return df.copy()

        df_out = df.copy()

        rename_map = {
            "preciopromedio": "precio_promedio",
            "cod_municipio": "cod_municipio",
            "municipio": "municipio",
            "articulo": "articulo",
        }
        df_out = df_out.rename(columns={k: v for k, v in rename_map.items() if k in df_out.columns})

        text_cols = ["articulo", "municipio", "fuente"]
        for col in text_cols:
            if col in df_out.columns:
                df_out[col] = df_out[col].apply(sanitize_text)

        type_schema = {
            "anio": "int64",
            "mes": "int64",
            "precio_promedio": "float64",
            "cod_municipio": "string",
        }
        df_out = cast_datatypes(df_out, type_schema)

        keys = ["cod_municipio", "anio", "mes", "articulo"]
        df_out = deduplicate_dataset(df_out, subset_keys=keys)

        return df_out

    @staticmethod
    def clean_trade_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """Sanea y normaliza series de exportaciones de bioinsumos y comercio agropecuario."""
        if df.empty:
            return df.copy()

        df_out = df.copy()

        rename_map = {
            "a_o": "anio",
            "cod_depto": "cod_departamento",
            "exportaciones_en_valor_usd": "valor_usd",
            "exportaciones_en_volumen": "volumen_kg",
        }
        df_out = df_out.rename(columns={k: v for k, v in rename_map.items() if k in df_out.columns})

        text_cols = ["departamento", "producto", "descripcion_partida4_dig", "partida", "tradici_n_producto"]
        for col in text_cols:
            if col in df_out.columns:
                df_out[col] = df_out[col].apply(sanitize_text)

        type_schema = {
            "anio": "int64",
            "cod_departamento": "string",
            "partida": "string",
            "valor_usd": "float64",
            "volumen_kg": "float64",
        }
        df_out = cast_datatypes(df_out, type_schema)

        keys = ["anio", "mes", "cod_departamento", "producto", "partida"]
        df_out = deduplicate_dataset(df_out, subset_keys=keys)

        return df_out

    def process_and_save(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        cleaner_type: str,
    ) -> Dict[str, Any]:
        """Ejecuta el saneamiento específico y persiste en la capa Silver en formato Parquet Snappy."""
        initial_rows = len(df)
        cleaner_type_lower = cleaner_type.lower()

        if cleaner_type_lower == "eva":
            cleaned_df = self.clean_eva_dataset(df)
        elif cleaner_type_lower in {"trade", "bioinsumos", "exportaciones"}:
            cleaned_df = self.clean_trade_dataset(df)
        elif cleaner_type_lower == "ideam":
            cleaned_df = self.clean_ideam_dataset(df)
        elif cleaner_type_lower == "sipsa":
            cleaned_df = self.clean_sipsa_dataset(df)
        else:
            # Limpieza genérica básica
            cleaned_df = df.copy()
            for c in cleaned_df.select_dtypes(include=["object"]).columns:
                cleaned_df[c] = cleaned_df[c].apply(sanitize_text)
            cleaned_df = deduplicate_dataset(cleaned_df, subset_keys=list(cleaned_df.columns))

        target_file = dataset_name if dataset_name.endswith(".parquet") else f"{dataset_name}.parquet"
        target_path = self.cleaned_dir / target_file

        cleaned_df.to_parquet(target_path, engine="pyarrow", compression="snappy", index=False)

        # Cálculo de hash de la versión Silver
        sha256_hash = hashlib.sha256()
        with open(target_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256_hash.update(chunk)
        sha256_digest = sha256_hash.hexdigest()

        final_rows = len(cleaned_df)
        summary = {
            "dataset_name": dataset_name,
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "removed_duplicates": initial_rows - final_rows,
            "target_path": str(target_path),
            "sha256": sha256_digest,
            "file_size_bytes": target_path.stat().st_size,
        }

        logger.info(
            "Capa Silver generada para %s: %d filas (reducción: %d duplicados)",
            dataset_name, final_rows, initial_rows - final_rows
        )
        return summary
