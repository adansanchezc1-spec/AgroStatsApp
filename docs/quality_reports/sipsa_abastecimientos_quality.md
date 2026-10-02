# Reporte de Calidad de Datos: `sipsa_abastecimientos`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T20:01:49.229732  
**Estado General**: ❌ FAILED | **Score Global**: `77.4%`  
**Volumen**: 59,500 filas × 11 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 100.0% | ✅ Óptimo |
| **Uniqueness** | 37.5% | ❌ Crítico |
| **Validity** | 50.0% | ❌ Crítico |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 98.6% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_anio | Completeness | `anio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_periodo | Completeness | `periodo` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fecha | Completeness | `fecha` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fuente_destino | Completeness | `fuente_destino` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_codigo_departamento_origen | Completeness | `codigo_departamento_origen` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_codigo_divipola_origen | Completeness | `codigo_divipola_origen` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_departamento_origen | Completeness | `departamento_origen` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_municipio_origen | Completeness | `municipio_origen` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_grupo_alimento | Completeness | `grupo_alimento` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_producto | Completeness | `producto` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_cantidad_kg | Completeness | `cantidad_kg` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.208 | 0.010 | ❌ FAIL |
| primary_key_uniqueness | Uniqueness | `anio+fecha+codigo_divipola_origen+producto` | CRITICAL | 0.625 | 0.000 | ❌ FAIL |
| range_check_cantidad_kg | Validity | `cantidad_kg` | HIGH | 0.000 | 0.010 | ✅ PASS |
| regex_divipola_codigo_divipola_origen | Validity | `codigo_divipola_origen` | HIGH | 1.000 | 0.050 | ⚠️ WARN |
| timeliness_bounds_anio | Timeliness | `anio` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| timeliness_bounds_fecha | Timeliness | `fecha` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| extreme_outliers_iqr_anio | Accuracy | `anio` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_cantidad_kg | Accuracy | `cantidad_kg` | LOW | 0.028 | 0.050 | ✅ PASS |