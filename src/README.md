# Componentes de Código Fuente de AgroStats (`src/`)

**Plataforma**: AgroData Intelligence Platform (AgroStatsApp)  
**Fase PDCO**: **DEVELOPMENT** | **Active Skill**: `03-development`  
**Estándares**: SWEBOK, DAMA-DMBOK 2, Clean Architecture, PEP 8.

---

## 1. Módulos del Sistema

| Carpeta | Propósito y Responsabilidades |
|---|---|
| [`imputer/`](file:///c:/Users/ADAN/OneDrive/Documentos/Statsfirm/AgroStats%20AndTech/AgroStatsApp/src/imputer) | **Ingesta Automatizada & Motor de Imputación Multivariada**: Descarga las 10 fuentes oficiales de DANE e IDEAM, las persiste de forma inmutable en `CRISPDM/data/RAW` con auditoría SHA-256 y diagnostica/imputa faltantes bajo el marco de Rubin. |
| [`notebook_code/`](file:///c:/Users/ADAN/OneDrive/Documentos/Statsfirm/AgroStats%20AndTech/AgroStatsApp/src/notebook_code) | Utilidades compartidas y librerías auxiliares para los notebooks de investigación CRISP-DM. |
| [`dash_code/`](file:///c:/Users/ADAN/OneDrive/Documentos/Statsfirm/AgroStats%20AndTech/AgroStatsApp/src/dash_code) | Backend y frontend analítico para visualización de indicadores territoriales y series temporales. |

---

## 2. Ingesta Rápida de Datos

Para ejecutar la ingesta completa de las 10 fuentes oficiales:

```bash
python -m imputer.cli --download-all --limit 500
```
