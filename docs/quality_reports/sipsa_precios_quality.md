# Reporte de Calidad de Datos: `sipsa_precios`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T19:22:37.645682  
**Estado General**: ⚠️ WARNING | **Score Global**: `97.5%`  
**Volumen**: 36 filas × 29 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 92.3% | ✅ Óptimo |
| **Uniqueness** | 100.0% | ✅ Óptimo |
| **Validity** | 98.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 97.7% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_producto | Completeness | `producto` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_armenia_mercar_precio | Completeness | `armenia_mercar_precio` | MEDIUM | 0.111 | 0.400 | ✅ PASS |
| null_rate_armenia_mercar_var | Completeness | `armenia_mercar_var` | MEDIUM | 0.139 | 0.400 | ✅ PASS |
| null_rate_bogota_corabastos_precio | Completeness | `bogota_corabastos_precio` | MEDIUM | 0.028 | 0.400 | ✅ PASS |
| null_rate_bogota_corabastos_var | Completeness | `bogota_corabastos_var` | MEDIUM | 0.028 | 0.400 | ✅ PASS |
| null_rate_bucaramanga_centroabastos_precio | Completeness | `bucaramanga_centroabastos_precio` | MEDIUM | 0.083 | 0.400 | ✅ PASS |
| null_rate_bucaramanga_centroabastos_var | Completeness | `bucaramanga_centroabastos_var` | MEDIUM | 0.083 | 0.400 | ✅ PASS |
| null_rate_cali_cavasa_precio | Completeness | `cali_cavasa_precio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cali_cavasa_var | Completeness | `cali_cavasa_var` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cucuta_cenabastos_precio | Completeness | `cucuta_cenabastos_precio` | MEDIUM | 0.167 | 0.400 | ✅ PASS |
| null_rate_cucuta_cenabastos_var | Completeness | `cucuta_cenabastos_var` | MEDIUM | 0.167 | 0.400 | ✅ PASS |
| null_rate_ibague_plaza_la_21_precio | Completeness | `ibague_plaza_la_21_precio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_ibague_plaza_la_21_var | Completeness | `ibague_plaza_la_21_var` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_manizales_centro_galerias_precio | Completeness | `manizales_centro_galerias_precio` | MEDIUM | 0.139 | 0.400 | ✅ PASS |
| null_rate_manizales_centro_galerias_var | Completeness | `manizales_centro_galerias_var` | MEDIUM | 0.139 | 0.400 | ✅ PASS |
| null_rate_medellin_cma_precio | Completeness | `medellin_cma_precio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_medellin_cma_var | Completeness | `medellin_cma_var` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_neiva_surabastos_precio | Completeness | `neiva_surabastos_precio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_neiva_surabastos_var | Completeness | `neiva_surabastos_var` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_pasto_el_potrerillo_precio | Completeness | `pasto_el_potrerillo_precio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_pasto_el_potrerillo_var | Completeness | `pasto_el_potrerillo_var` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_pereira_la_41impala_precio | Completeness | `pereira_la_41impala_precio` | MEDIUM | 0.250 | 0.400 | ✅ PASS |
| null_rate_pereira_la_41impala_var | Completeness | `pereira_la_41impala_var` | MEDIUM | 0.278 | 0.400 | ✅ PASS |
| null_rate_pereira_mercasa_precio | Completeness | `pereira_mercasa_precio` | MEDIUM | 0.083 | 0.400 | ✅ PASS |
| null_rate_pereira_mercasa_var | Completeness | `pereira_mercasa_var` | MEDIUM | 0.083 | 0.400 | ✅ PASS |
| null_rate_santa_marta_precio | Completeness | `santa_marta_precio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_santa_marta_var | Completeness | `santa_marta_var` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_tunja_precio | Completeness | `tunja_precio` | MEDIUM | 0.222 | 0.400 | ✅ PASS |
| null_rate_tunja_var | Completeness | `tunja_var` | MEDIUM | 0.222 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `producto` | CRITICAL | 0.000 | 0.000 | ✅ PASS |
| extreme_outliers_iqr_armenia_mercar_precio | Accuracy | `armenia_mercar_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_bogota_corabastos_precio | Accuracy | `bogota_corabastos_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_bogota_corabastos_var | Accuracy | `bogota_corabastos_var` | LOW | 0.029 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_bucaramanga_centroabastos_precio | Accuracy | `bucaramanga_centroabastos_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_bucaramanga_centroabastos_var | Accuracy | `bucaramanga_centroabastos_var` | LOW | 0.061 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_cucuta_cenabastos_precio | Accuracy | `cucuta_cenabastos_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_cucuta_cenabastos_var | Accuracy | `cucuta_cenabastos_var` | LOW | 0.067 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_manizales_centro_galerias_precio | Accuracy | `manizales_centro_galerias_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_manizales_centro_galerias_var | Accuracy | `manizales_centro_galerias_var` | LOW | 0.032 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_medellin_cma_precio | Accuracy | `medellin_cma_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_medellin_cma_var | Accuracy | `medellin_cma_var` | LOW | 0.056 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_pereira_la_41impala_precio | Accuracy | `pereira_la_41impala_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_pereira_la_41impala_var | Accuracy | `pereira_la_41impala_var` | LOW | 0.077 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_pereira_mercasa_precio | Accuracy | `pereira_mercasa_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_pereira_mercasa_var | Accuracy | `pereira_mercasa_var` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_tunja_precio | Accuracy | `tunja_precio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_tunja_var | Accuracy | `tunja_var` | LOW | 0.071 | 0.050 | ⚠️ WARN |