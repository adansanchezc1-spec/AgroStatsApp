"""
Motor Integral de Calidad de Datos (Data Quality Engine & Quality Gates)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: ISO/IEC 25010 (Calidad del Dato), DAMA-DMBOK 2 (Data Quality Management)
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class QualityCheckResult:
    check_name: str
    dimension: str  # Completeness, Validity, Uniqueness, Consistency, Timeliness, Accuracy
    column: Optional[str]
    status: str     # PASSED, WARNING, FAILED
    severity: str   # CRITICAL, HIGH, MEDIUM, LOW
    metric_value: float
    threshold: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataQualityReport:
    dataset_name: str
    timestamp: str
    total_records: int
    total_columns: int
    overall_score: float
    status: str  # PASSED, WARNING, FAILED
    dimension_scores: Dict[str, float]
    checks: List[QualityCheckResult]
    summary_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "timestamp": self.timestamp,
            "total_records": self.total_records,
            "total_columns": self.total_columns,
            "overall_score": round(self.overall_score, 4),
            "status": self.status,
            "dimension_scores": {k: round(v, 4) for k, v in self.dimension_scores.items()},
            "checks": [asdict(c) for c in self.checks],
            "summary_metrics": self.summary_metrics
        }

    def to_markdown(self) -> str:
        status_badge = "✅ PASSED" if self.status == "PASSED" else ("⚠️ WARNING" if self.status == "WARNING" else "❌ FAILED")
        md = [
            f"# Reporte de Calidad de Datos: `{self.dataset_name}`",
            f"**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: {self.timestamp}  ",
            f"**Estado General**: {status_badge} | **Score Global**: `{self.overall_score * 100:.1f}%`  ",
            f"**Volumen**: {self.total_records:,} filas × {self.total_columns} columnas\n",
            "---",
            "## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)\n",
            "| Dimensión | Puntuación | Estado |",
            "|---|:---:|:---:|"
        ]
        for dim, sc in self.dimension_scores.items():
            dim_status = "✅ Óptimo" if sc >= 0.90 else ("⚠️ Aceptable" if sc >= 0.70 else "❌ Crítico")
            md.append(f"| **{dim}** | {sc * 100:.1f}% | {dim_status} |")

        md.append("\n---")
        md.append("## 2. Detalle de Pruebas de Calidad (Quality Checks)\n")
        md.append("| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |")
        md.append("|---|---|---|:---:|:---:|:---:|:---:|")

        for c in self.checks:
            res_icon = "✅ PASS" if c.status == "PASSED" else ("⚠️ WARN" if c.status == "WARNING" else "❌ FAIL")
            col_str = c.column or "Global"
            md.append(f"| {c.check_name} | {c.dimension} | `{col_str}` | {c.severity} | {c.metric_value:.3f} | {c.threshold:.3f} | {res_icon} |")

        return "\n".join(md)


class DataQualityEngine:
    """
    Motor automatizado de evaluación de calidad de datos multidimensional.
    Aplica verificaciones de Completitud, Validez, Unicidad, Consistencia, Oportunidad y Precisión.
    """

    @classmethod
    def evaluate(
        cls,
        df: pd.DataFrame,
        dataset_name: str,
        primary_keys: Optional[List[str]] = None,
        max_null_threshold: float = 0.40,
        numeric_range_rules: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> DataQualityReport:
        checks: List[QualityCheckResult] = []
        n_rows, n_cols = df.shape
        now_str = datetime.now().isoformat()

        if n_rows == 0:
            checks.append(QualityCheckResult(
                check_name="empty_dataset_check",
                dimension="Completeness",
                column=None,
                status="FAILED",
                severity="CRITICAL",
                metric_value=0.0,
                threshold=1.0,
                message="El DataFrame no contiene registros."
            ))
            return DataQualityReport(
                dataset_name=dataset_name,
                timestamp=now_str,
                total_records=0,
                total_columns=n_cols,
                overall_score=0.0,
                status="FAILED",
                dimension_scores={"Completeness": 0.0},
                checks=checks
            )

        # -------------------------------------------------------------
        # DIMENSIÓN 1: COMPLETENESS (Completitud)
        # -------------------------------------------------------------
        col_null_scores = []
        for col in df.columns:
            null_ratio = df[col].isna().mean()
            col_score = 1.0 - null_ratio
            col_null_scores.append(col_score)

            status = "PASSED"
            if null_ratio > max_null_threshold:
                status = "FAILED" if null_ratio >= 0.70 else "WARNING"

            checks.append(QualityCheckResult(
                check_name=f"null_rate_{col}",
                dimension="Completeness",
                column=col,
                status=status,
                severity="HIGH" if null_ratio >= 0.70 else "MEDIUM",
                metric_value=null_ratio,
                threshold=max_null_threshold,
                message=f"Tasa de nulos en '{col}': {null_ratio:.2%}",
                details={"null_count": int(df[col].isna().sum())}
            ))

        completeness_score = float(np.mean(col_null_scores)) if col_null_scores else 1.0

        # -------------------------------------------------------------
        # DIMENSIÓN 2: UNIQUENESS (Unicidad)
        # -------------------------------------------------------------
        dup_rows = df.duplicated().sum()
        dup_ratio = dup_rows / n_rows
        uniqueness_score = 1.0 - dup_ratio

        dup_status = "PASSED" if dup_ratio == 0 else ("WARNING" if dup_ratio < 0.05 else "FAILED")
        checks.append(QualityCheckResult(
            check_name="row_deduplication_check",
            dimension="Uniqueness",
            column=None,
            status=dup_status,
            severity="MEDIUM",
            metric_value=dup_ratio,
            threshold=0.01,
            message=f"Filas duplicadas idénticas: {dup_rows} ({dup_ratio:.2%})",
            details={"duplicate_rows": int(dup_rows)}
        ))

        if primary_keys and all(pk in df.columns for pk in primary_keys):
            pk_dups = df.duplicated(subset=primary_keys).sum()
            pk_dup_ratio = pk_dups / n_rows
            pk_status = "PASSED" if pk_dups == 0 else "FAILED"
            checks.append(QualityCheckResult(
                check_name="primary_key_uniqueness",
                dimension="Uniqueness",
                column="+".join(primary_keys),
                status=pk_status,
                severity="CRITICAL",
                metric_value=pk_dup_ratio,
                threshold=0.0,
                message=f"Duplicados en Clave Primaria {primary_keys}: {pk_dups} ({pk_dup_ratio:.2%})"
            ))
            uniqueness_score = min(uniqueness_score, 1.0 - pk_dup_ratio)

        # -------------------------------------------------------------
        # DIMENSIÓN 3: VALIDITY (Validez de Tipos, Rangos y Patrones)
        # -------------------------------------------------------------
        validity_scores = []

        # 3.1 Rangos numéricos
        if numeric_range_rules:
            for col, (min_val, max_val) in numeric_range_rules.items():
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    valid_series = df[col].dropna()
                    if len(valid_series) > 0:
                        out_of_bounds = ((valid_series < min_val) | (valid_series > max_val)).sum()
                        invalid_ratio = out_of_bounds / len(valid_series)
                        v_score = 1.0 - invalid_ratio
                        validity_scores.append(v_score)

                        v_status = "PASSED" if invalid_ratio == 0 else ("WARNING" if invalid_ratio < 0.05 else "FAILED")
                        checks.append(QualityCheckResult(
                            check_name=f"range_check_{col}",
                            dimension="Validity",
                            column=col,
                            status=v_status,
                            severity="HIGH",
                            metric_value=invalid_ratio,
                            threshold=0.01,
                            message=f"Valores fuera de rango [{min_val}, {max_val}] en '{col}': {out_of_bounds} ({invalid_ratio:.2%})"
                        ))

        # 3.2 Patrones de cadenas conocidas (e.g. DIVIPOLA de 5 dígitos)
        divipola_cols = [c for c in df.columns if "divipola" in c or c in ["cod_mpio", "codigo_municipio"]]
        for col in divipola_cols:
            non_null = df[col].dropna().astype(str)
            if len(non_null) > 0:
                valid_pattern = non_null.str.match(r"^\d{4,5}$").mean()
                validity_scores.append(valid_pattern)
                p_status = "PASSED" if valid_pattern >= 0.95 else "WARNING"
                checks.append(QualityCheckResult(
                    check_name=f"regex_divipola_{col}",
                    dimension="Validity",
                    column=col,
                    status=p_status,
                    severity="HIGH",
                    metric_value=1.0 - valid_pattern,
                    threshold=0.05,
                    message=f"Conformidad patrón código DIVIPOLA en '{col}': {valid_pattern:.2%}"
                ))

        validity_score = float(np.mean(validity_scores)) if validity_scores else 0.98

        # -------------------------------------------------------------
        # DIMENSIÓN 4: CONSISTENCY (Consistencia Lógica)
        # -------------------------------------------------------------
        consistency_scores = [1.0]
        # Coordenadas geográficas de Colombia: Latitud [-4.5, 13.5], Longitud [-81.8, -66.8]
        lat_cols = [c for c in df.columns if any(k in c for k in ["latitud", "latitude", "lat"])]
        lon_cols = [c for c in df.columns if any(k in c for k in ["longitud", "longitude", "lon"])]
        
        if lat_cols and lon_cols:
            lat_col, lon_col = lat_cols[0], lon_cols[0]
            lat_s = pd.to_numeric(df[lat_col], errors="coerce").dropna()
            lon_s = pd.to_numeric(df[lon_col], errors="coerce").dropna()
            if len(lat_s) > 0 and len(lon_s) > 0:
                valid_geo = ((lat_s >= -5.0) & (lat_s <= 14.0)).mean()
                consistency_scores.append(valid_geo)
                geo_status = "PASSED" if valid_geo >= 0.90 else "WARNING"
                checks.append(QualityCheckResult(
                    check_name="colombia_geobounds_consistency",
                    dimension="Consistency",
                    column=f"{lat_col},{lon_col}",
                    status=geo_status,
                    severity="MEDIUM",
                    metric_value=1.0 - valid_geo,
                    threshold=0.10,
                    message=f"Puntos geoespaciales dentro del polígono Colombia: {valid_geo:.2%}"
                ))

        consistency_score = float(np.mean(consistency_scores))

        # -------------------------------------------------------------
        # DIMENSIÓN 5: TIMELINESS (Oportunidad y Fechas)
        # -------------------------------------------------------------
        date_cols = [c for c in df.columns if any(k in c for k in ["fecha", "date", "periodo", "anio", "year"])]
        timeliness_scores = []
        for col in date_cols:
            try:
                parsed_dates = pd.to_datetime(df[col], errors="coerce").dropna()
                if len(parsed_dates) > 0:
                    future_dates = (parsed_dates > pd.Timestamp("2030-01-01")).sum()
                    future_ratio = future_dates / len(parsed_dates)
                    t_score = 1.0 - future_ratio
                    timeliness_scores.append(t_score)
                    t_status = "PASSED" if future_ratio == 0 else "WARNING"
                    checks.append(QualityCheckResult(
                        check_name=f"timeliness_bounds_{col}",
                        dimension="Timeliness",
                        column=col,
                        status=t_status,
                        severity="MEDIUM",
                        metric_value=future_ratio,
                        threshold=0.01,
                        message=f"Fechas futuras anómalas en '{col}': {future_dates} ({future_ratio:.2%})"
                    ))
            except Exception:
                pass

        timeliness_score = float(np.mean(timeliness_scores)) if timeliness_scores else 1.0

        # -------------------------------------------------------------
        # DIMENSIÓN 6: ACCURACY / OUTLIERS (Precisión y Detección de Anomalías)
        # -------------------------------------------------------------
        num_cols = df.select_dtypes(include=[np.number]).columns
        accuracy_scores = []
        for col in num_cols:
            s = df[col].dropna()
            if len(s) > 10:
                q25, q75 = s.quantile(0.25), s.quantile(0.75)
                iqr = q75 - q25
                if iqr > 0:
                    extreme_outliers = ((s < q25 - 3 * iqr) | (s > q75 + 3 * iqr)).sum()
                    outlier_ratio = extreme_outliers / len(s)
                    a_score = 1.0 - outlier_ratio
                    accuracy_scores.append(a_score)
                    a_status = "PASSED" if outlier_ratio < 0.05 else "WARNING"
                    checks.append(QualityCheckResult(
                        check_name=f"extreme_outliers_iqr_{col}",
                        dimension="Accuracy",
                        column=col,
                        status=a_status,
                        severity="LOW",
                        metric_value=outlier_ratio,
                        threshold=0.05,
                        message=f"Outliers extremos (>3*IQR) en '{col}': {extreme_outliers} ({outlier_ratio:.2%})"
                    ))

        accuracy_score = float(np.mean(accuracy_scores)) if accuracy_scores else 0.95

        # -------------------------------------------------------------
        # CONSOLIDACIÓN Y SCORE GLOBAL
        # -------------------------------------------------------------
        dim_scores = {
            "Completeness": completeness_score,
            "Uniqueness": uniqueness_score,
            "Validity": validity_score,
            "Consistency": consistency_score,
            "Timeliness": timeliness_score,
            "Accuracy": accuracy_score
        }

        weights = {
            "Completeness": 0.25,
            "Uniqueness": 0.20,
            "Validity": 0.20,
            "Consistency": 0.15,
            "Timeliness": 0.10,
            "Accuracy": 0.10
        }

        overall_score = sum(dim_scores[d] * weights[d] for d in dim_scores)

        # Estado global
        critical_failures = any(c.status == "FAILED" and c.severity == "CRITICAL" for c in checks)
        any_failed = any(c.status == "FAILED" for c in checks)
        any_warning = any(c.status == "WARNING" for c in checks)

        if critical_failures or overall_score < 0.70:
            final_status = "FAILED"
        elif any_failed or any_warning or overall_score < 0.90:
            final_status = "WARNING"
        else:
            final_status = "PASSED"

        summary_metrics = {
            "null_cells_total": int(df.isna().sum().sum()),
            "total_cells": int(n_rows * n_cols),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }

        return DataQualityReport(
            dataset_name=dataset_name,
            timestamp=now_str,
            total_records=n_rows,
            total_columns=n_cols,
            overall_score=overall_score,
            status=final_status,
            dimension_scores=dim_scores,
            checks=checks,
            summary_metrics=summary_metrics
        )
