# Reporte de Calidad de Datos: `dane_csaa`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T20:02:16.507258  
**Estado General**: ✅ PASSED | **Score Global**: `99.1%`  
**Volumen**: 22 filas × 3 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 100.0% | ✅ Óptimo |
| **Uniqueness** | 100.0% | ✅ Óptimo |
| **Validity** | 98.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 95.0% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_codigo_cuadro | Completeness | `codigo_cuadro` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_descripcion_indicador | Completeness | `descripcion_indicador` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fase_cadena | Completeness | `fase_cadena` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `codigo_cuadro` | CRITICAL | 0.000 | 0.000 | ✅ PASS |