# Reporte de Calidad de Datos: `ideam_pluviometria`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T19:22:40.256215  
**Estado General**: ❌ FAILED | **Score Global**: `77.7%`  
**Volumen**: 100 filas × 13 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 100.0% | ✅ Óptimo |
| **Uniqueness** | 91.0% | ✅ Óptimo |
| **Validity** | 0.0% | ❌ Crítico |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 95.0% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_codigoestacion | Completeness | `codigoestacion` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_codigosensor | Completeness | `codigosensor` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_fechaobservacion | Completeness | `fechaobservacion` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_valorobservado | Completeness | `valorobservado` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_nombreestacion | Completeness | `nombreestacion` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_departamento | Completeness | `departamento` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_municipio | Completeness | `municipio` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_zonahidrografica | Completeness | `zonahidrografica` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_latitud | Completeness | `latitud` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_longitud | Completeness | `longitud` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_descripcionsensor | Completeness | `descripcionsensor` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_unidadmedida | Completeness | `unidadmedida` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_codigo_divipola | Completeness | `codigo_divipola` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `codigoestacion` | CRITICAL | 0.090 | 0.000 | ❌ FAIL |
| regex_divipola_codigo_divipola | Validity | `codigo_divipola` | HIGH | 1.000 | 0.050 | ⚠️ WARN |
| colombia_geobounds_consistency | Consistency | `latitud,longitud` | MEDIUM | 0.000 | 0.100 | ✅ PASS |
| timeliness_bounds_fechaobservacion | Timeliness | `fechaobservacion` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| extreme_outliers_iqr_codigoestacion | Accuracy | `codigoestacion` | LOW | 0.150 | 0.050 | ⚠️ WARN |
| extreme_outliers_iqr_latitud | Accuracy | `latitud` | LOW | 0.000 | 0.050 | ✅ PASS |
| extreme_outliers_iqr_longitud | Accuracy | `longitud` | LOW | 0.000 | 0.050 | ✅ PASS |