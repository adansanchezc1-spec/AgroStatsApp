# Paquete AgroStats Imputer & Ingestor (`src/imputer`)

**Plataforma**: AgroData Intelligence Platform (AgroStatsApp)  
**Fase PDCO**: **DEVELOPMENT** | **Active Skill**: `03-development`  
**Estándares**: DAMA-DMBOK 2 (Gobierno y Calidad de Metadatos), SWEBOK Cap. 1 & 2, Rubin Framework (MCAR/MAR/MNAR), ISO 25010, PEP 8.

---

## 1. Visión y Propósito

El paquete `src/imputer` es el motor desacoplado de la plataforma AgroStats encargado de:
1. **Ingesta Automatizada**: Conectarse por internet a los portales oficiales de datos abiertos del gobierno colombiano (**DANE** e **IDEAM**) para descargar, validar y almacenar de forma inmutable los **10 conjuntos de datos estratégicos** del sector agropecuario en `data/RAW`.
2. **Gobernanza y Linaje DAMA-DMBOK**: Generación automática de huellas criptográficas **SHA-256**, conteo de registros, esquemas de columnas y archivo `raw_manifest.json`.
3. **Imputación Inteligente Multivariada**: Diagnóstico estadístico de ausencias (mecanismos MCAR, MAR, MNAR según Rubin y prueba de Little), torneo competitivo de algoritmos con penalización de distorsión de varianza e inyección de banderas de trazabilidad (`_is_imputed`, `_impute_method`).

---

## 2. Catálogo Oficial de las 10 Fuentes Estratégicas

| # | Identificador (`dataset_id`) | Fuente Oficial | Custodio | Estrategia | Formato |
|---|---|---|---|---|---|
| **1** | `sipsa_abastecimientos` | SIPSA Abastecimiento de Alimentos | DANE | `dane_scrape` | XLSX / CSV |
| **2** | `sipsa_precios` | SIPSA Precios Mayoristas Diarios | DANE | `dane_scrape` | XLSX / CSV |
| **3** | `sipsa_insumos` | SIPSA Insumos Agrícolas (Fertilizantes/Plaguicidas) | DANE / MADR | Socrata API (`gwbi-fnzs`) | JSON / CSV |
| **4** | `dane_ipp` | Índice de Precios del Productor (IPP) | DANE | `dane_scrape` | XLSX / CSV |
| **5** | `dane_ipc` | Índice de Precios al Consumidor (IPC Alimentos) | DANE | `dane_scrape` | XLSX / CSV |
| **6** | `ideam_sequia` | Normales Climatológicas y Sequía | IDEAM | Socrata API (`nsz2-kzcq`) | JSON / CSV |
| **7** | `ideam_pluvio` | Pluviometría y Precipitación por Estación | IDEAM | Socrata API (`s54a-sgyg`) | JSON / CSV |
| **8** | `ideam_temperatura` | Temperatura Ambiente y Extremos | IDEAM | Socrata API (`sbwg-7ju4`) | JSON / CSV |
| **9** | `ideam_evapotranspiracion` | Evapotranspiración y Demanda Atmosférica | IDEAM | Modelo FAO-56 / Catálogo | JSON / CSV |
| **10** | `ideam_radiacion` | Radiación Solar Global Acumulada | IDEAM | Socrata API (`rv9s-8nv6`) | JSON / CSV |

---

## 3. Estructura Arquitectónica Modular

```
src/imputer/
├── __init__.py                     <- Inicializador del paquete e interfaces públicas
├── config.py                       <- Rutas a data/RAW, URLs base, timeouts y endpoints Socrata
├── pipeline.py                     <- Orquestador maestro de descarga e inmutabilidad en data/RAW
├── cli.py                          <- Interfaz de línea de comandos (POSIX CLI)
├── ingestion/                      <- Módulo de conectores de red y web scraping
│   ├── __init__.py
│   ├── base_client.py              <- Cliente HTTP con reintentos exponenciales y streaming
│   ├── socrata_client.py           <- Conector API Socrata SODA 2.0 (datos.gov.co)
│   ├── dane_scraper.py             <- Extractor dinámico de publicaciones y anexos del DANE
│   └── dataset_registry.py         <- Registro DAMA de metadatos de las 10 fuentes
├── imputation/                     <- Motor científico de imputación de datos
│   ├── __init__.py
│   ├── rubin_diagnostics.py        <- Diagnóstico de patrones de ausencia (MCAR, MAR, MNAR)
│   ├── algorithms.py               <- Algoritmos: Interpolación temporal, KNN, MICE, Mediana Condicional
│   └── imputation_engine.py        <- Benchmark competitivo con penalización de varianza
└── README.md                       <- Documentación técnica del módulo
```

---

## 4. Modo de Uso

### 4.1. Vía Línea de Comandos (CLI)

```bash
# 1. Listar las 10 fuentes oficiales y sus metadatos
python -m imputer.cli --list-sources

# 2. Descargar e ingerir todas las 10 fuentes en data/RAW
python -m imputer.cli --download-all --limit 500

# 3. Descargar una fuente específica (ej. Pluviometría IDEAM)
python -m imputer.cli --source ideam_pluvio --limit 1000

# 4. Descargar Precios Mayoristas Diarios del DANE
python -m imputer.cli --source sipsa_precios

# 5. Ejecutar demostración del motor de imputación inteligente
python -m imputer.cli --impute-sample
```

### 4.2. Uso Programático en Python o Notebooks

```python
from imputer import AgroDataIngestionPipeline, IntelligentImputer

# 1. Ingesta automatizada hacia data/RAW
pipeline = AgroDataIngestionPipeline()
manifest = pipeline.ingest_all_sources(limit_per_socrata=500)

# 2. Diagnóstico e imputación competitiva
imputer = IntelligentImputer()
result = imputer.fit_impute(df, inject_audit_flags=True)

print("Algoritmo ganador:", result.winning_algorithm_name)
print("Score:", result.winning_score)
curated_df = result.imputed_dataframe
```

---

## 5. Metodología Científica del Motor de Imputación

### Diagnóstico de Rubin (1976) & Test de Little (1988)
El motor clasifica el patrón de ausencias en tres regímenes:
- **MCAR** (*Missing Completely at Random*): Ausencias independientes de cualquier variable observada o no observada. Se recomiendan métodos de interpolación local o KNN.
- **MAR** (*Missing at Random*): La probabilidad de ausencia depende sistemáticamente de covariables registradas (ej. falta de reporte de precios en municipios lejanos explicada por lejanía o baja producción). Se seleccionan métodos multivariados como MICE o mediana condicional por jerarquía DIVIPOLA/CPC.
- **MNAR** (*Missing Not at Random*): Dependencia intrínseca con el valor no observado. Requiere banderas obligatorias de auditoría.

### Benchmark Competitivo con Penalización de Varianza
Para evitar el colapso artificial de la variabilidad natural (error típico de imputaciones simples por media), el algoritmo ganador se selecciona minimizando:

$$\text{Score} = \text{RMSE} \times \left(1.0 + \left|1.0 - \frac{\text{Var}_{imp}}{\text{Var}_{orig}}\right| \times \lambda\right)$$

Donde $\lambda = 1.5$ es el factor de penalización por distorsión de varianza.
