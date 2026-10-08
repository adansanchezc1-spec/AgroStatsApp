# Reporte de Calidad de Datos: `landing_leads`
**Estándar**: ISO/IEC 25010 & DAMA-DMBOK 2 | **Fecha**: 2026-10-01T20:02:20.759737  
**Estado General**: ✅ PASSED | **Score Global**: `99.1%`  
**Volumen**: 1 filas × 17 columnas

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
| null_rate_id | Completeness | `id` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_ticketid | Completeness | `ticketid` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_companyname | Completeness | `companyname` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_contactname | Completeness | `contactname` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_email | Completeness | `email` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_phone | Completeness | `phone` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_industry | Completeness | `industry` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_services | Completeness | `services` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_datavolumetb | Completeness | `datavolumetb` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_budgetusd | Completeness | `budgetusd` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_urgency | Completeness | `urgency` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_challengedescription | Completeness | `challengedescription` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_score | Completeness | `score` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_priority | Completeness | `priority` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_status | Completeness | `status` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_assignedto | Completeness | `assignedto` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| null_rate_createdat | Completeness | `createdat` | MEDIUM | 0.000 | 0.400 | ✅ PASS |
| row_deduplication_check | Uniqueness | `Global` | MEDIUM | 0.000 | 0.010 | ✅ PASS |
| primary_key_uniqueness | Uniqueness | `id` | CRITICAL | 0.000 | 0.000 | ✅ PASS |