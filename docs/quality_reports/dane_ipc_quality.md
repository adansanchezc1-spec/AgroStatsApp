# Reporte de Calidad de Datos: `dane_ipc`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T19:22:39.564150  
**Estado General**: ⚠️ WARNING | **Score Global**: `90.8%`  
**Volumen**: 19 filas × 25 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 68.6% | ❌ Crítico |
| **Uniqueness** | 100.0% | ✅ Óptimo |
| **Validity** | 98.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 90.3% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_unnamed_0 | Completeness | `unnamed_0` | MEDIUM | 0.053 | 0.400 | ✅ PASS |
| null_rate_unnamed_1 | Completeness | `unnamed_1` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_2 | Completeness | `unnamed_2` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_3 | Completeness | `unnamed_3` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_4 | Completeness | `unnamed_4` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_5 | Completeness | `unnamed_5` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_6 | Completeness | `unnamed_6` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_7 | Completeness | `unnamed_7` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_8 | Completeness | `unnamed_8` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_9 | Completeness | `unnamed_9` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_10 | Completeness | `unnamed_10` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_11 | Completeness | `unnamed_11` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_12 | Completeness | `unnamed_12` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_13 | Completeness | `unnamed_13` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_14 | Completeness | `unnamed_14` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_15 | Completeness | `unnamed_15` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_16 | Completeness | `unnamed_16` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_17 | Completeness | `unnamed_17` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_18 | Completeness | `unnamed_18` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_19 | Completeness | `unnamed_19` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_20 | Completeness | `unnamed_20` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_21 | Completeness | `unnamed_21` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_22 | Completeness | `unnamed_22` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_23 | Completeness | `unnamed_23` | MEDIUM | 0.316 | 0.400 | ✅ PASS |
| null_rate_unnamed_24 | Completeness | `unnamed_24` | MEDIUM | 0.526 | 0.400 | ⚠️ WARN |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| extreme_outliers_iqr_unnamed_1 | Accuracy | `unnamed_1` | LOW | 0.154 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_2 | Accuracy | `unnamed_2` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_3 | Accuracy | `unnamed_3` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_4 | Accuracy | `unnamed_4` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_5 | Accuracy | `unnamed_5` | LOW | 0.231 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_6 | Accuracy | `unnamed_6` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_7 | Accuracy | `unnamed_7` | LOW | 0.154 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_8 | Accuracy | `unnamed_8` | LOW | 0.154 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_9 | Accuracy | `unnamed_9` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_10 | Accuracy | `unnamed_10` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_11 | Accuracy | `unnamed_11` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_12 | Accuracy | `unnamed_12` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_13 | Accuracy | `unnamed_13` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_14 | Accuracy | `unnamed_14` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_15 | Accuracy | `unnamed_15` | LOW | 0.154 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_16 | Accuracy | `unnamed_16` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_17 | Accuracy | `unnamed_17` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_18 | Accuracy | `unnamed_18` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_19 | Accuracy | `unnamed_19` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_20 | Accuracy | `unnamed_20` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_21 | Accuracy | `unnamed_21` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_22 | Accuracy | `unnamed_22` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_unnamed_23 | Accuracy | `unnamed_23` | LOW | 0.077 | 0.050 | ⚠️ WARN |