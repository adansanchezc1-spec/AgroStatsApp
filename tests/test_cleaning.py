"""Pruebas Unitarias para el Módulo de Limpieza y Transformación (Capa Silver).
Fase PDCO: CONTROL | Estándar: ISO/IEC 25010 / Clean Code
Casos de prueba: TC-401 a TC-405.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.cleaning.transformers import (
    sanitize_text,
    cast_datatypes,
    handle_missing_values,
    deduplicate_dataset,
)
from src.cleaning.cleaner_pipeline import CleanerPipeline


class TestSanitizeText:
    """TC-401: Pruebas unitarias para sanitize_text."""

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("  Antioquia  ", "ANTIOQUIA"),
            ("Boyacá", "BOYACA"),
            ("SAN VICENTE DEL CAGUÁN", "SAN VICENTE DEL CAGUAN"),
            ("café    arábigo  suave", "CAFE ARABIGO SUAVE"),
            ("CÒRDOBA", "CORDOBA"),
            ("", ""),
            (None, ""),
            (np.nan, ""),
        ],
    )
    def test_sanitize_text_normalization_and_idempotency(self, input_text, expected):
        """Verifica remoción de acentos, colapso de espacios, mayúsculas e idempotencia."""
        result = sanitize_text(input_text)
        assert result == expected
        # Idempotencia: f(f(x)) == f(x)
        assert sanitize_text(result) == result


class TestCastDatatypes:
    """TC-402: Pruebas unitarias para cast_datatypes."""

    def test_cast_datatypes_standard_conversions(self):
        """Verifica casteo correcto a int64, float64, string, category y datetime."""
        raw_data = {
            "entero": ["1", "2", "3", "invalid"],
            "flotante": ["10.5", "20.7", "nan", "30.0"],
            "texto": [123, 456, 789, None],
            "fecha": ["2023-01-01", "2023-02-01", "invalid_date", "2023-04-01"],
            "categoria": ["A", "B", "A", "C"],
        }
        df = pd.DataFrame(raw_data)
        schema = {
            "entero": "int64",
            "flotante": "float64",
            "texto": "string",
            "fecha": "datetime64[ns]",
            "categoria": "category",
        }

        df_cast = cast_datatypes(df, schema)

        assert df_cast["entero"].dtype.name == "int64"
        assert df_cast["entero"].iloc[3] == 0  # Reemplazo seguro de nulos antes de entero
        assert df_cast["flotante"].dtype.name == "float64"
        assert pd.isna(df_cast["flotante"].iloc[2])
        assert df_cast["texto"].dtype.name == "string"
        assert np.issubdtype(df_cast["fecha"].dtype, np.datetime64)
        assert df_cast["categoria"].dtype.name == "category"

    def test_cast_datatypes_empty_dataframe(self):
        """Garantiza que un DataFrame vacío retorna copia intacta sin error."""
        df_empty = pd.DataFrame()
        result = cast_datatypes(df_empty, {"col1": "int64"})
        assert result.empty


class TestHandleMissingValues:
    """TC-403: Pruebas unitarias para handle_missing_values."""

    def test_handle_missing_categorical_imputation(self):
        """Verifica que nulos, cadenas vacías y 'NAN' se reemplacen por default_fill."""
        df = pd.DataFrame(
            {
                "variedad": ["CATURRA", None, "   ", "NAN", "CASTILLO"],
                "otro": [1, 2, 3, 4, 5],
            }
        )
        df_imputed = handle_missing_values(df, categorical_cols=["variedad"])

        expected = ["CATURRA", "SIN_VARIEDAD_ESPECIFICADA", "SIN_VARIEDAD_ESPECIFICADA", "SIN_VARIEDAD_ESPECIFICADA", "CASTILLO"]
        assert list(df_imputed["variedad"]) == expected

    def test_handle_missing_numeric_fill(self):
        """Verifica imputación de valores numéricos opcional."""
        df = pd.DataFrame({"valor": [10.0, np.nan, 30.0]})
        df_imputed = handle_missing_values(df, numeric_fill=-999.0)
        assert df_imputed["valor"].iloc[1] == -999.0


class TestDeduplicateDataset:
    """TC-404: Pruebas unitarias para deduplicate_dataset."""

    def test_deduplicate_dataset_with_subset(self):
        """Verifica eliminación de duplicados según subconjunto de claves."""
        df = pd.DataFrame(
            {
                "codigo": ["05001", "05001", "11001"],
                "anio": [2021, 2021, 2021],
                "valor": [100, 200, 300],
            }
        )
        dedup = deduplicate_dataset(df, subset_keys=["codigo", "anio"], sort_by="valor", ascending=False)
        assert len(dedup) == 2
        # Al ordenar por valor descendente, debe conservar el valor 200 para '05001'
        record_05001 = dedup[dedup["codigo"] == "05001"].iloc[0]
        assert record_05001["valor"] == 200

    def test_deduplicate_dataset_no_valid_keys(self):
        """Verifica comportamiento cuando ninguna clave coincide."""
        df = pd.DataFrame({"a": [1, 1, 2], "b": [2, 2, 3]})
        dedup = deduplicate_dataset(df, subset_keys=["non_existent"])
        assert len(dedup) == 2


class TestCleanerPipeline:
    """TC-405: Pruebas para la clase CleanerPipeline y sus métodos específicos."""

    @pytest.fixture
    def pipeline(self, tmp_path: Path):
        return CleanerPipeline(cleaned_base_dir=tmp_path)

    def test_clean_eva_dataset(self, pipeline):
        """Verifica pipeline de limpieza de EVA: renombramiento, sanitización, tipado y deduplicación."""
        df_raw = pd.DataFrame(
            {
                "c_d_dep": ["05", "05"],
                "c_d_mun": ["05001", "05001"],
                "departamento": ["Antioquia", "Antioquia"],
                "municipio": ["Medellín", "Medellín"],
                "cultivo": ["Café", "Café"],
                "desagregaci_n_regional_y": [None, "Caturra"],
                "a_o": ["2022", "2022"],
                "rea_sembrada_ha": ["120.5", "120.5"],
                "rea_cosechada_ha": ["110.0", "110.0"],
                "producci_n_t": ["250.0", "250.0"],
                "rendimiento_t_ha": ["2.27", "2.27"],
            }
        )
        cleaned = pipeline.clean_eva_dataset(df_raw)

        assert "cod_municipio" in cleaned.columns
        assert "variedad" in cleaned.columns
        assert cleaned["departamento"].iloc[0] == "ANTIOQUIA"
        assert cleaned["municipio"].iloc[0] == "MEDELLIN"
        assert cleaned["cultivo"].iloc[0] == "CAFE"
        assert cleaned["anio"].dtype.name == "int64"
        assert cleaned["area_sembrada_ha"].dtype.name == "float64"
        assert len(cleaned) == 2  # Una tiene variedad SIN_VARIEDAD_ESPECIFICADA y la otra CATURRA

    def test_clean_ideam_dataset(self, pipeline):
        """Verifica limpieza de dataset meteorológico IDEAM."""
        df_raw = pd.DataFrame(
            {
                "codigoestacion": ["001", "001"],
                "nombreestacion": ["Estación Norte", "Estación Norte"],
                "fechaobservacion": ["2023-01-01 12:00:00", "2023-01-01 12:00:00"],
                "valorobservado": ["15.4", "15.4"],
                "descripcionsensor": ["Temperatura Aire", "Temperatura Aire"],
            }
        )
        cleaned = pipeline.clean_ideam_dataset(df_raw)
        assert len(cleaned) == 1  # Duplicado exacto eliminado
        assert cleaned["sensor_descripcion"].iloc[0] == "TEMPERATURA AIRE"
        assert cleaned["valor_observado"].dtype.name == "float64"

    def test_clean_sipsa_dataset(self, pipeline):
        """Verifica limpieza de dataset de precios SIPSA."""
        df_raw = pd.DataFrame(
            {
                "cod_municipio": ["11001"],
                "municipio": ["Bogotá, D.C."],
                "articulo": ["Papa Pastusa"],
                "preciopromedio": ["3500.5"],
                "anio": ["2023"],
                "mes": ["5"],
            }
        )
        cleaned = pipeline.clean_sipsa_dataset(df_raw)
        assert cleaned["municipio"].iloc[0] == "BOGOTA, D.C."
        assert cleaned["articulo"].iloc[0] == "PAPA PASTUSA"
        assert cleaned["precio_promedio"].iloc[0] == 3500.5
        assert cleaned["anio"].iloc[0] == 2023
        assert cleaned["mes"].iloc[0] == 5

    def test_process_and_save_generates_parquet_and_sha256(self, pipeline, tmp_path):
        """Verifica persistencia en parquet Snappy y reporte con hash SHA-256."""
        df_sample = pd.DataFrame(
            {
                "c_d_dep": ["05"],
                "c_d_mun": ["05001"],
                "departamento": ["Antioquia"],
                "municipio": ["Medellín"],
                "cultivo": ["Aguacate"],
                "a_o": [2022],
                "rea_sembrada_ha": [50.0],
            }
        )
        summary = pipeline.process_and_save(df_sample, dataset_name="test_eva_silver", cleaner_type="eva")

        assert summary["initial_rows"] == 1
        assert summary["final_rows"] == 1
        assert Path(summary["target_path"]).exists()
        assert len(summary["sha256"]) == 64  # Longitud SHA-256 hexadecimal
        assert summary["file_size_bytes"] > 0
