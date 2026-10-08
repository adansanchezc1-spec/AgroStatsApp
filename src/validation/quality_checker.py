"""Motor de Verificación de Calidad y Puertas de Enlace (Quality Checker).
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 / SWEBOK v4
Validación por lotes, particionamiento conforme/no-conforme y auditoría de unicidad.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Type
import pandas as pd

from src.utils.logger import get_logger
from src.validation.contracts import ValidationError

logger = get_logger("validation.quality_checker")


class QualityChecker:
    """Validador sistemático de lotes de datos contra contratos de calidad."""

    @staticmethod
    def validate_dataset(
        df: pd.DataFrame,
        contract_cls: Any,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Valida cada registro de un DataFrame contra un contrato de datos.
        Retorna: (df_conformes, df_no_conformes, reporte_metricas).
        """
        if df.empty:
            logger.warning("validate_dataset invocado con un DataFrame vacío")
            return pd.DataFrame(), pd.DataFrame(), {
                "total_records": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "compliance_rate_pct": 100.0,
                "error_summary": {},
            }

        valid_records: List[Dict[str, Any]] = []
        invalid_records: List[Dict[str, Any]] = []
        error_counts: Dict[str, int] = {}

        for idx, row in df.iterrows():
            record_dict = row.to_dict()
            try:
                validated_dict = contract_cls.validate(record_dict)
                valid_records.append(validated_dict)
            except ValidationError as exc:
                err_msg = str(exc)
                record_dict["_validation_error"] = err_msg
                invalid_records.append(record_dict)
                for err in err_msg.split("; "):
                    error_key = err.split("(")[0].strip()
                    error_counts[error_key] = error_counts.get(error_key, 0) + 1
            except Exception as exc:
                err_msg = f"Error inesperado de parseo: {exc}"
                record_dict["_validation_error"] = err_msg
                invalid_records.append(record_dict)
                error_counts["ErrorInesperado"] = error_counts.get("ErrorInesperado", 0) + 1

        total = len(df)
        valid_count = len(valid_records)
        invalid_count = len(invalid_records)
        compliance_rate = round((valid_count / total) * 100.0, 2) if total > 0 else 0.0

        valid_df = pd.DataFrame(valid_records)
        invalid_df = pd.DataFrame(invalid_records)

        metrics = {
            "total_records": total,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "compliance_rate_pct": compliance_rate,
            "error_summary": error_counts,
        }

        logger.info(
            "Validación %s completada: %d/%d conformes (%.2f%%)",
            contract_cls.__name__, valid_count, total, compliance_rate
        )
        return valid_df, invalid_df, metrics

    @staticmethod
    def check_composite_key_uniqueness(
        df: pd.DataFrame,
        key_columns: List[str],
    ) -> Dict[str, Any]:
        """
        Verifica la unicidad de una clave compuesta en el conjunto de datos.
        """
        missing_cols = [c for c in key_columns if c not in df.columns]
        if missing_cols:
            raise KeyError(f"Columnas de clave no presentes en DataFrame: {missing_cols}")

        if df.empty:
            return {
                "key_columns": key_columns,
                "total_rows": 0,
                "unique_keys": 0,
                "duplicate_rows": 0,
                "is_unique": True,
            }

        total_rows = len(df)
        subset_df = df[key_columns]
        duplicates_mask = subset_df.duplicated(keep=False)
        duplicate_rows_count = int(duplicates_mask.sum())
        unique_keys_count = int(len(subset_df.drop_duplicates()))
        is_unique = duplicate_rows_count == 0

        logger.info(
            "Verificación de clave %s: %d filas, %d duplicados (Unicidad: %s)",
            key_columns, total_rows, duplicate_rows_count, is_unique
        )

        return {
            "key_columns": key_columns,
            "total_rows": total_rows,
            "unique_keys": unique_keys_count,
            "duplicate_rows": duplicate_rows_count,
            "is_unique": is_unique,
            "duplicate_samples": df[duplicates_mask].head(10).to_dict(orient="records") if not is_unique else [],
        }

    @staticmethod
    def generate_markdown_report(metrics: Dict[str, Any], dataset_name: str) -> str:
        """Genera un informe formal en formato Markdown con el veredicto del Quality Gate."""
        compliance = metrics.get("compliance_rate_pct", 0.0)
        status = "PASÓ (GREEN)" if compliance >= 80.0 else "RECHAZADO (RED)"
        
        md_lines = [
            f"### Reporte de Quality Gate: {dataset_name}",
            f"- **Estado de Puerta de Calidad**: `{status}`",
            f"- **Total Registros Evaluados**: `{metrics.get('total_records', 0)}`",
            f"- **Registros Conformes**: `{metrics.get('valid_records', 0)}`",
            f"- **Registros No Conformes**: `{metrics.get('invalid_records', 0)}`",
            f"- **Tasa de Conformidad**: `{compliance}%`",
            "",
            "#### Desglose de No Conformidades:",
        ]

        errors = metrics.get("error_summary", {})
        if errors:
            md_lines.append("| Regla / Campo Violado | Ocurrencias |")
            md_lines.append("|---|:---:|")
            for err, cnt in errors.items():
                md_lines.append(f"| `{err}` | {cnt} |")
        else:
            md_lines.append("*Cero violaciones detectadas.*")

        return "\n".join(md_lines)
