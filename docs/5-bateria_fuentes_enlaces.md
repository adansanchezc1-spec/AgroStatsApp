# Batería de Fuentes, Enlaces y Enzimas de Datos Agropecuarios
**Proyecto**: AgroData Intelligence Platform (AgroStatsApp)  
**Documento**: `docs/5-bateria_fuentes_enlaces.md`  
**Fase PDCO**: PLAN | **SDLC Stage**: Requirements / Data Ingestion Design  
**Última actualización**: 2026-10-01  

---

## Visión General

Este documento constituye la **batería estructurada de enlaces, endpoints de API y repositorios oficiales de datos agropecuarios, bioinsumos, agroinsumos y variables macroeconómicas** de Colombia. 

Su propósito es servir como **inventario maestro de fuentes de ingesta** para los pipelines automatizados de `AgroStatsApp` (`SocrataClient`, `DaneScraper`, `DataIngestionPipeline`).

---

## 1. Datos Abiertos & APIs de Comercio / Bioinsumos (Datos.gov.co)

Datasets del Portal Único de Datos Abiertos de Colombia (Socrata API).

| ID Recurso | Tipo / Formato | Descripción | Frecuencia | Enlace / Endpoint |
|---|---|---|---|---|
| **GAIC-B8AW (API Directa)** | Endpoint CSV Socrata | API de conexión directa con registros de exportaciones agrícolas, bioinsumos y agroinsumos | Mensual / Dinámico | [Descarga CSV Directa](https://www.datos.gov.co/resource/gaic-b8aw.csv) |
| **GAIC-B8AW (Portal)** | Portal Metadata HTML | Ficha técnica y diccionario de datos de exportaciones agrícolas tradicionales y no tradicionales | Documental | [Ver About Data](https://www.datos.gov.co/Agricultura-y-Desarrollo-Rural/Exportaciones-agr-colas-no-tradicionales-y-tradici/gaic-b8aw/about_data) |
| **57SV-P2FU (API Directa)** | Endpoint CSV Socrata | API Socrata con observaciones meteorológicas telemétricas en tiempo real del IDEAM (Temperatura aire/suelo, Precipitación, Radiación, etc.) | Tiempo Real / Horario | [Descarga CSV Directa](https://www.datos.gov.co/resource/57sv-p2fu.csv) |
| **57SV-P2FU (Portal)** | Portal Metadata HTML | Ficha técnica de datos meteorológicos y sensores telemétricos en tiempo real del IDEAM | Documental | [Ver About Data](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/IDEAM-Observaciones-Meteorologicas-en-Tiempo-Real/57sv-p2fu/about_data) |

### 🛠️ Código de Ingesta Recomendado (Python Socrata Client)
```python
import pandas as pd

# Endpoints de consulta Socrata (Datos Abiertos Colombia)
EXPORTACIONES_DATASET_ID = "gaic-b8aw"
IDEAM_SENSORES_DATASET_ID = "57sv-p2fu"

CSV_EXPORTACIONES_URL = f"https://www.datos.gov.co/resource/{EXPORTACIONES_DATASET_ID}.csv?$limit=50000"
CSV_IDEAM_TELEMETRIA_URL = f"https://www.datos.gov.co/resource/{IDEAM_SENSORES_DATASET_ID}.csv?$limit=50000"

def cargar_datos_ideam_telemetria():
    df = pd.read_csv(CSV_IDEAM_TELEMETRIA_URL)
    print(f"Registros telemétricos IDEAM cargados: {len(df)}")
    return df
```

---

## 2. Estadísticas e Indicadores de Agroinsumos y Bioinsumos (UPRA)

Publicaciones periódicas sobre el comportamiento de precios, oferta e importaciones de insumos agrícolas y pecuarios.

| Fuente | Tipo de Recurso | Descripción | Frecuencia | Enlace Directo |
|---|---|---|---|---|
| **UPRA - Insumos** | Portal de Estadísticas | Sala de prensa, boletines periódicos y análisis de mercado de agroinsumos | Mensual / Trimestral | [Boletines y Estadísticas de Agroinsumos](https://upra.gov.co/es-co/sala-de-prensa/boletines-y-estadisticas#agroinsumos) |

---

## 3. Informes Macroeconómicos y PIB Agropecuario (UPRA)

Reportes técnicos oficiales sobre la evolución del Producto Interno Bruto (PIB) y el Valor Agregado Bruto (VAB) del sector agropecuario en Colombia.

| Periodo | Relevancia | Contenido Principal | Formato | Enlace Directo PDF |
|---|---|---|---|---|
| **PIB I Trimestre 2024** | Histórico | Desempeño agrícola, pecuario y silvícola T1 2024 | PDF | [PIB I Trimestre 2024 PDF](https://upra.gov.co/sites/default/files/2025-04/PIB%20I%20trimestre%202024.pdf) |
| **PIB II Trimestre 2024** | Histórico | Evolución trimestral T2 2024 y comparativa anual | PDF | [PIB II Trimestre 2024 PDF](https://upra.gov.co/sites/default/files/2025-10/PIB%20II%20trimestre%202024.pdf) |
| **PIB III Trimestre 2024** | Histórico | Comportamiento macroeconómico sectorial T3 2024 | PDF | [PIB III Trimestre 2024 PDF](https://upra.gov.co/sites/default/files/2025-04/PIB%20III%20trimestre%202024.pdf) |
| **PIB IV Trimestre 2024** | 🔑 **RECURSO CLAVE** | Consolidado anual 2024, cierre de PIB agrícola y análisis estructural | PDF | [PIB IV Trimestre 2024 PDF (Clave)](https://upra.gov.co/sites/default/files/2025-04/PIB%20IV%20trimestre%202024.pdf) |
| **PIB IV Trimestre 2025** | Cierre Reciente (Febrero 2026) | Consolidado preliminar 2025 y perspectivas de inicio de año | PDF | [PIB IV Trimestre 2025 PDF (2026-02)](https://upra.gov.co/sites/default/files/2026-02/20260216%20PIB%20IV%20trimestre%202025.pdf) |

---

## 4. Microdatos y Archivos Estructurales (DANE)

Catálogos de microdatos a nivel de formulario/registro anonimizado del Archivo Nacional de Datos (ANDA).

| Sistema | Catálogo ID | Descripción | Enlace Directo |
|---|---|---|---|
| **DANE ANDA** | Catalog 859 | Inventario de microdatos del Departamento Administrativo Nacional de Estadística (Estadísticas agrícolas / Encuestas) | [Catálogo DANE #859](https://microdatos.dane.gov.co/index.php/catalog/859) |

---

## 5. Plataformas de Información Geográfica y Planificación (SIPRA - UPRA)

Herramientas territoriales para zonificación, aptitud productiva y fronteras agrícolas.

| Sistema | Tipo | Cobertura | Descripción | Enlace Directo |
|---|---|---|---|---|
| **SIPRA** | Geoportal Interactivo | Nacional | Sistema de Información para la Planificación Rural Agropecuaria (Aptitud de cultivos, mapas de uso y capas geográficas) | [Geoportal SIPRA Nacional](https://sipra.upra.gov.co/nacional) |

---

## 6. Matriz de Mapeo a Módulos del Sistema AgroStatsApp

| Fuente / Recurso | Módulo del Sistema | Uso en Pipeline (`src/imputer/...`) | Documento Relacionado |
|---|---|---|---|
| **Socrata API GAIC-B8AW** | `src/imputer/ingestion/socrata_client.py` | Ingesta automática de volúmenes y valores de exportaciones / agroinsumos | `2-diccionariofuentes.md` (Fuente #5/6) |
| **Socrata API 57SV-P2FU** | `src/imputer/ingestion/socrata_client.py` | Ingesta de observaciones telemétricas en tiempo real (sensores IDEAM) | `5-bateria_fuentes_enlaces.md` (Sección 1) |
| **Boletines Agroinsumos UPRA** | `src/notebook_code/eda_analyzer.py` | Benchmark de precios e índices de fertilizantes/bioinsumos | `1-Bateria_preguntas.md` (Preguntas E1, E2) |
| **Informes PIB UPRA (PDFs)** | `src/notebook_code/feature_engineer.py` | Extracción de covariables macroeconómicas y VAB | `4-quecomo.md` (Sección Agroeconomía) |
| **DANE Catalog 859** | `src/imputer/ingestion/dane_scraper.py` | Archivo de microdatos anonimizados para modelos imputadores de Rubin | `3-granularidad.md` (Nivel Microdatos) |
| **SIPRA Geoportal** | `src/notebook_code/mdm_manager.py` | Cruces de aptitud territorial y fronteras productivas por municipio | `3-granularidad.md` (Nivel Municipio x Capa) |

---

> ℹ️ **Nota de mantenimiento**: Todos los enlaces han sido verificados contra la estructura oficial de dominios de `datos.gov.co`, `upra.gov.co` y `dane.gov.co`.
