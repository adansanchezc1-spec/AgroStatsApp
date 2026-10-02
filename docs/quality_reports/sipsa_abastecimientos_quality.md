# Reporte de Calidad de Datos: `sipsa_abastecimientos`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T19:22:36.481083  
**Estado General**: ⚠️ WARNING | **Score Global**: `96.8%`  
**Volumen**: 10,000 filas × 9 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 100.0% | ✅ Óptimo |
| **Uniqueness** | 86.8% | ⚠️ Aceptable |
| **Validity** | 98.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 98.3% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_fuente | Completeness | `fuente` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fechaencuesta | Completeness | `fechaencuesta` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cod_depto_proc | Completeness | `cod_depto_proc` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cod_municipio_proc | Completeness | `cod_municipio_proc` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_departamento_proc | Completeness | `departamento_proc` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_municipio_proc | Completeness | `municipio_proc` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_grupo | Completeness | `grupo` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_ali | Completeness | `ali` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cant_kg | Completeness | `cant_kg` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.132 | 0.010 | ❌ FAIL |
| timeliness_bounds_fechaencuesta | Timeliness | `fechaencuesta` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| extreme_outliers_iqr_cant_kg | Accuracy | `cant_kg` | LOW | 0.017 | 0.050 | ✅ PASS |