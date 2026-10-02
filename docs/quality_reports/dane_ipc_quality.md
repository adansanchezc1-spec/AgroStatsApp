# Reporte de Calidad de Datos: `dane_ipc`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T20:02:08.436516  
**Estado General**: ✅ PASSED | **Score Global**: `99.8%`  
**Volumen**: 284 filas × 7 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 99.3% | ✅ Óptimo |
| **Uniqueness** | 100.0% | ✅ Óptimo |
| **Validity** | 100.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 100.0% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_anio | Completeness | `anio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_mes_num | Completeness | `mes_num` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_mes_nombre | Completeness | `mes_nombre` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fecha | Completeness | `fecha` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_ipc_alimentos | Completeness | `ipc_alimentos` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_variacion_mensual_pct | Completeness | `variacion_mensual_pct` | MEDIUM | 0.004 | 0.400 | ✅ PASS |
| null_rate_variacion_anual_pct | Completeness | `variacion_anual_pct` | MEDIUM | 0.042 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `anio+mes_num` | CRITICAL | 0.000 | 0.000 | ✅ PASS |
| range_check_ipc_alimentos | Validity | `ipc_alimentos` | HIGH | 0.000 | 0.010 | ✅ PASS |
| timeliness_bounds_anio | Timeliness | `anio` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| timeliness_bounds_fecha | Timeliness | `fecha` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| extreme_outliers_iqr_anio | Accuracy | `anio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_mes_num | Accuracy | `mes_num` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_ipc_alimentos | Accuracy | `ipc_alimentos` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_variacion_mensual_pct | Accuracy | `variacion_mensual_pct` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_variacion_anual_pct | Accuracy | `variacion_anual_pct` | LOW | 0.000 | 0.050 | ✅ PASS |