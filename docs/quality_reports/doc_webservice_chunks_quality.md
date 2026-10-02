# Reporte de Calidad de Datos: `doc_webservice_chunks`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T19:23:08.208138  
**Estado General**: ✅ PASSED | **Score Global**: `99.6%`  
**Volumen**: 39 filas × 5 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 100.0% | ✅ Óptimo |
| **Uniqueness** | 100.0% | ✅ Óptimo |
| **Validity** | 98.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 100.0% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_chunk_id | Completeness | `chunk_id` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_source_file | Completeness | `source_file` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_page_number | Completeness | `page_number` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_chunk_text | Completeness | `chunk_text` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_char_length | Completeness | `char_length` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `chunk_id` | CRITICAL | 0.000 | 0.000 | ✅ PASS |
| extreme_outliers_iqr_chunk_id | Accuracy | `chunk_id` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_page_number | Accuracy | `page_number` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_char_length | Accuracy | `char_length` | LOW | 0.000 | 0.050 | ✅ PASS |