# AgroStatsApp 🌾📊

> **Plataforma Analítica y Arquitectura Lakehouse para Inteligencia Agropecuaria y Telemetría Climática**  
> Diseñada bajo estándares internacionales **SWEBOK**, **DAMA-DMBOK 2**, **ISO/IEC 25010** y principios **SOLID**.

---

## 📌 Visión General

**AgroStatsApp** es una solución integral de ingeniería de datos, ciencia de datos y visualización analítica enfocada en la convergencia de datos agropecuarios (SIPSA Mayoristas, Insumos, Abastecimientos DANE), variables macroeconómicas (IPC, IPP Alimentos) y series climáticas/telemetría en tiempo real (IDEAM Socrata API `57sv-p2fu`).

El sistema responde rigurosamente a una **batería de 25 preguntas de negocio (A1 - J1)** mediante metodologías paramétricas y no paramétricas, garantizando armonización temporal y espacial (cruce Lat/Lon estación $\rightarrow$ DIVIPOLA DANE).

---

## 🏛️ Arquitectura del Sistema

```
                             FUENTES HETEROGÉNEAS
       ┌───────────────────────────────┬───────────────────────────────┐
       │ • SIPSA Abastecimientos       │ • DANE CSAA Satélite          │
       │ • SIPSA Precios Mayoristas    │ • IDEAM Telemetría (API Socrata)
       │ • SIPSA Insumos y Fertiliz.   │ • IDEAM Climatología Histórica│
       │ • DANE IPC / IPP Alimentos    │ • Boletines Técnicos DANE PDF │
       └───────────────────────────────┴───────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │                CAPA DE INGESTIÓN & HARMONIZACIÓN              │
       │  - SocrataClient (Paginación tokenizada + Backoff)            │
       │  - GranularityHarmonizer (Station Lat/Lon -> DIVIPOLA DANE)   │
       │  - FileLoader (.csv, .xlsx, .parquet, .dta, .sav)             │
       └───────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │              CAPA DE GOBERNANZA & DATA QUALITY (ISO 25010)    │
       │  - DataSanitizer & PIIHandler (Hashing SHA-256)               │
       │  - SchemaValidator (Pydantic / Great Expectations Quality Gate│
       └───────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │                   MEDALLION DATA LAKEHOUSE                    │
       │  - Bronze: Datos crudos indexados con metadatos de linaje     │
       │  - Silver: Limpieza, imputación MICE/Rubin y tipos validados  │
       │  - Gold: SQLite (`agrostats_lakehouse.db`) + Parquet curados   │
       └───────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │            MOTOR ANALÍTICO & MODELADO ESTADÍSTICO             │
       │  - BusinessQuestionsEngine (25 Preguntas A1-J1)               │
       │  - Enfoque Dual: Paramétrico (ANOVA, OLS) vs No Paramétrico   │
       │    (Mann-Whitney, Kruskal-Wallis, Spearman, Regresión Robusta)│
       │  - Control Estadístico de Procesos (Regla 1 de Nelson - 3σ)   │
       │  - SARIMAX & Múltiples Imputaciones (FCS MICE)                │
       └───────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │                    CONSUMO & VISUALIZACIÓN                    │
       │  - 72 Notebooks Jupyter interactivos (Pip headers listos)     │
       │  - Dashboard HTML5/CSS3/Vanilla JS Ejecutivo (`app/dash/`)    │
       └───────────────────────────────────────────────────────────────┘
```

---

## 📂 Estructura del Repositorio

```
AgroStatsApp/
├── app/
│   └── dash/
│       └── index.html               # Dashboard analítico interactivo
├── config/
│   └── datasets_config.yaml         # Metadatos y contratos de fuentes
├── data/
│   └── processed/
│       ├── agrostats_lakehouse.db   # Lakehouse SQLite Gold
│       └── *.parquet                # Particiones analíticas columnares
├── docs/
│   ├── 1-Bateria_preguntas.md       # Batería completa A1-J1
│   ├── 2-diccionariofuentes.md      # Diccionario de datos y tipos
│   ├── 3-granularidad.md            # Matriz de dimensionalidad y resoluciones
│   ├── 4-quecomo.md                 # Arquitectura metodológica detallada
│   ├── 5-bateria_fuentes_enlaces.md # Endpoints y recursos oficiales
│   ├── lineage/                     # Manifiestos de linaje DAMA-DMBOK
│   └── quality_reports/             # Reportes gráficos de control de calidad
├── notebooks/                       # 72 Notebooks (9 fuentes x 8 fases)
│   ├── 01_sipsa_abastecimientos/
│   ├── 02_sipsa_precios/
│   ├── 03_sipsa_insumos/
│   ├── 04_dane_ipc_ipp/
│   ├── 05_ideam_climatologia/
│   ├── 06_ideam_telemetria_57sv/
│   ├── 07_dane_satelite_csaa/
│   ├── 08_boletin_pdf_webservice/
│   └── 09_landing_leads_store/
├── src/
│   ├── cleaning/                    # Sanitización, tipos y PII Hashing
│   ├── database/                    # Abstracción Lakehouse DBManager
│   ├── ingestion/                   # Clientes Socrata, PDF y multi-formato
│   ├── modeling/                    # Motor de preguntas A1-J1 y armonizador
│   ├── validation/                  # Quality Gates y esquemas Pydantic
│   └── visualization/               # Gráficos estandarizados con intervalos
├── tests/                           # Suite de pruebas unitarias automatizadas
├── build_full_notebooks.py          # Generador y compilador de los 72 notebooks
├── run_pipeline.py                  # Orquestador del pipeline end-to-end
├── requirements.txt                 # Dependencias fijadas y reproducibles
└── metadata.json                    # Trazabilidad PDCO y gobernanza
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/adansanchezc1-spec/AgroStatsApp.git
cd AgroStatsApp
```

### 2. Configurar el entorno virtual
```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Variables de entorno (Opcional)
Copiar `.env.example` a `.env` y configurar credenciales personalizadas si se requiere acceso autenticado de alta tasa a datos abiertos:
```bash
cp .env.example .env
```

---

## ⚡ Ejecución del Pipeline y Pruebas

### Ejecutar el Pipeline Lakehouse Completo
```bash
python run_pipeline.py
```
*Genera y actualiza automáticamente `data/processed/agrostats_lakehouse.db` y todos los archivos `.parquet` curados.*

### Ejecutar la Suite de Pruebas Unitarias
```bash
python -m unittest discover tests
```
*Valida sanitización, calidad de datos, extracción Socrata simulada y el motor de preguntas de negocio.*

### Abrir el Dashboard Analítico
Abrir en cualquier navegador moderno:
```bash
start app/dash/index.html
```

---

## 📓 Los 72 Notebooks de Análisis

Cada uno de los 9 datasets cuenta con 8 notebooks estructurados según el ciclo de vida de la ingeniería de datos:

1. `01_entendimiento_documentacion.ipynb`: Dominio, fichas técnicas y normativas.
2. `02_ingestion.ipynb`: Extracción idempotente y control de tasa.
3. `03_exploracion_informatica_y_estadistica.ipynb`: EDA inicial, correlaciones y dimensionalidad.
4. `04_ingestion_como_dataframe.ipynb`: Cast tipológico estricto y parseo temporal.
5. `05_limpieza_wrangling_governance.ipynb`: Anonimización PII, imputación y validación.
6. `06_modelo_base_de_datos.ipynb`: Persistencia en capa Silver/Gold del Lakehouse.
7. `07_modeling_and_integration.ipynb`: Modelado estadístico paramétrico vs. no paramétrico.
8. `08_visualization.ipynb`: Visualizaciones ejecutivas con bandas de confianza.

> **Nota:** Todos los notebooks incluyen en su primera celda `%pip install -q ...` y resolución de rutas dinámicas para ejecución directa en Google Colab, JupyterLab o VS Code sin errores de dependencias.

---

## 🎯 Batería de Preguntas de Negocio (A1 - J1)

El motor [`src/modeling/business_questions_engine.py`](file:///src/modeling/business_questions_engine.py) provee soluciones computables para:

- **Eje A (Abastecimiento y Dinámica Territorial)**: A1, A2, A3
- **Eje B (Precios Mayoristas y Volatilidad)**: B1, B2, B3
- **Eje C (Insumos y Estructura de Costos)**: C1, C2, C3
- **Eje D (Macroeconómico e Inflación DANE IPC/IPP)**: D1, D2, D3
- **Eje E (Climatología e Impacto Hidrológico IDEAM)**: E1, E2, E3
- **Eje F (Telemetría en Tiempo Real y Alertas Tempranas)**: F1, F2
- **Eje G (Cuentas Satélite y Macro-Agro CSAA)**: G1, G2
- **Eje H (Minería Textual y Boletines Webservice)**: H1, H2
- **Eje I (Comercialización y Leads de Demanda)**: I1, I2
- **Eje J (Integración Holística y Causal)**: J1, J2, J3

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia MIT.
