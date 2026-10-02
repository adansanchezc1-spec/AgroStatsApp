# Reporte de Calidad de Datos: `dane_csaa`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T19:23:06.700297  
**Estado General**: ⚠️ WARNING | **Score Global**: `95.9%`  
**Volumen**: 34 filas × 2 columnas

---
## 1. Desempeño por Dimensión de Calidad (DAMA-DMBOK 2)

| Dimensión | Puntuación | Estado |
|---|:---:|:---:|
| **Completeness** | 89.7% | ⚠️ Aceptable |
| **Uniqueness** | 97.1% | ✅ Óptimo |
| **Validity** | 98.0% | ✅ Óptimo |
| **Consistency** | 100.0% | ✅ Óptimo |
| **Timeliness** | 100.0% | ✅ Óptimo |
| **Accuracy** | 95.0% | ✅ Óptimo |

---
## 2. Detalle de Pruebas de Calidad (Quality Checks)

| Regla / Chequeo | Dimensión | Columna | Severidad | Métrica | Umbral | Resultado |
|---|---|---|:---:|:---:|:---:|:---:|
| null_rate_unnamed_1 | Completeness | `unnamed_1` | MEDIUM | 0.059 | 0.400 | ✅ PASS |
| null_rate_unnamed_2 | Completeness | `unnamed_2` | MEDIUM | 0.147 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.029 | 0.010 | ⚠️ WARN |