# Plan Maestro de Pruebas de Software y Calidad de Datos (TestsPlan)
**Proyecto**: AgroStats Intelligence Platform (`AgroStatsApp`)  
**Versión**: 2.1.0  
**Fecha**: 2026-10-07  
**Fase PDCO**: CONTROL  
**Estándar**: ISO/IEC/IEEE 29119 / ISO/IEC 25010 / SWEBOK Cap. 4  

---

## 1. Alcance y Estrategia de Pruebas

El presente plan establece los estándares, metodologías, herramientas y criterios de aceptación para la verificación y validación del sistema **AgroStatsApp**. El objetivo es garantizar que cada capa del Lakehouse (Bronze, Silver, Gold), cada algoritmo de limpieza y curaduría, y cada motor de cálculo estadístico operen con exactitud matemática, reproducibilidad y estabilidad estructural.

### 1.1 Pirámide de Pruebas Adoptada
```
               ▲
              / \
             /   \     E2E / Pipeline Completo (run_pipeline.py)
            /  5% \    ------------------------------------------
           /-------\
          /         \   Pruebas de Integración & Data Quality Gate
         /    25%    \  (Esquemas Pydantic, Lakehouse, SQLite WAL)
        /-------------\
       /               \ Pruebas Unitarias de Funciones Puras
      /       70%       \(Sanitizer, Unwrapper, Profiler, Lineage)
     /-------------------\
```

---

## 2. Niveles de Prueba y Criterios de Aceptación

### 2.1 Nivel 1: Pruebas Unitarias (Componentes Aislados)
- **Herramienta**: `pytest` 8.x con plugins `pytest-cov`.
- **Enfoque**: Evaluar funciones puras sin dependencias de I/O externo mediante mocks y fixtures parametrizados.
- **Criterio de Aceptación**: 100% de tests unitarios exitosos; tiempo de ejecución total inferior a 15 segundos.

### 2.2 Nivel 2: Pruebas de Integración (Lakehouse & Base de Datos)
- **Herramienta**: `pytest` operando sobre SQLite en memoria (`sqlite3.connect(":memory:")`) y directorios temporales `tmp_path`.
- **Enfoque**:
  - Verificar la transición Bronze $\rightarrow$ Silver $\rightarrow$ Gold.
  - Comprobar la integridad referencial y tipado en SQLite.
  - Asegurar la generación correcta del manifiesto de linaje (`pipeline_run_manifest.json`).

### 2.3 Nivel 3: Pruebas de Calidad de Datos (Data Quality Gates)
- **Herramienta**: `DataQualityEngine` y validadores de esquemas Pydantic v2.
- **Enfoque**:
  - Evaluar la tasa de nulos por columna antes de permitir la promoción a Silver.
  - Comprobar que ninguna columna clasificada como clave primaria contenga duplicados o nulos.
  - Validar dominios admisibles (precios $> 0$, precipitación $\ge 0$, porcentajes entre 0 y 100).

---

## 3. Matriz de Casos de Prueba (Test Cases)

| ID | Módulo Evaluado | Descripción del Caso de Prueba | Entrada | Salida Esperada | Estado Actual |
|:---:|---|---|---|---|:---:|
| **TC-001** | `cleaning.sanitizer` | Sanitización de caracteres monetarios y conversión a float. | Cadenas `"$ 1.250,50"`, `"$ -"` | `1250.50`, `NaN` | **PASÓ** (`test_cleaning.py`) |
| **TC-002** | `cleaning.table_unwrapper` | Desenrollado de tabla ancha IPC a formato tidy longitudinal. | DataFrame con columnas mensuales en cabecera | Columnas normalizadas `[anio, mes, valor]` | **PASÓ** (`test_cleaning.py`) |
| **TC-003** | `cleaning.pii_handler` | Enmascaramiento criptográfico de información PII (teléfonos/emails). | Lead con `telefono: "3001234567"` | Teléfono ofuscado `hash(sha256)` | **PASÓ** (`test_cleaning.py`) |
| **TC-004** | `validation.schemas` | Validación de esquema Pydantic para registros de abastecimiento. | Payload JSON con tipos correctos | Instancia válida de `AbastecimientoRecord` | **PASÓ** (`test_validation.py`) |
| **TC-005** | `validation.quality_engine` | Detección de columnas que superan umbral de nulos permitido. | DataFrame con 35% de nulos en columna $X$ | Alerta de calidad y flag de fallo si umbral $\le 30\%$ | **PASÓ** (`test_quality_engine.py`) |
| **TC-006** | `lakehouse.manager` | Ingesta inmutable en capa Bronze con hash SHA-256. | DataFrame crudo de 100 filas | Archivo Parquet generado con checksum no nulo | **PASÓ** (`test_lakehouse.py`) |
| **TC-007** | `lakehouse.manager` | Transición a Silver con exclusión de PII y tipado estricto. | DataFrame Bronze con columnas PII | DataFrame Silver sin PII y persistido en SQLite | **PASÓ** (`test_lakehouse.py`) |
| **TC-008** | `lakehouse.manager` | Generación de Data Marts analíticos en capa Gold. | Diccionario de DataFrames Silver | Data Marts `dim_divipola` y `mart_business_questions` | **PASÓ** (`test_lakehouse.py`) |
| **TC-009** | `governance.lineage` | Registro de linaje y generación de grafo DAG Markdown. | Pasos de transformación ejecutados | Archivo `lineage_dag.md` y manifest JSON válidos | **PASÓ** (`test_governance.py`) |
| **TC-010** | `governance.data_catalog` | Extracción de metadatos de esquema para catálogo DAMA. | Tabla SQLite con columnas tipadas | Entrada estructurada en `data_catalog.md` | **PASÓ** (`test_governance.py`) |
| **TC-011** | `modeling.profiler` | Prueba de normalidad Shapiro-Wilk y cálculo dual paramétrico/robusto. | Serie gaussiana y serie asimétrica | Diagnósticos correctos de $p$-value y medidas $\mu$ vs $\tilde{x}$ | **PASÓ** (`test_modeling.py`) |
| **TC-012** | `modeling.geospatial` | Mapeo de coordenadas y municipios a código DIVIPOLA 5 dígitos. | Nombres de municipios colombianos | Código DIVIPOLA DANE exacto asignado | **PASÓ** (`test_modeling.py`) |
| **TC-013** | `ingestion.resilience` | Reintento exponencial con jitter ante fallas transitorias de red. | Función mockeada que falla 2 veces y luego responde | 3 intentos registrados y ejecución exitosa final | **PASÓ** (`test_resilience.py`) |
| **TC-014** | `database.db_manager` | Conexión a SQLite, inserción por lotes y lectura en DataFrame. | 1,000 registros sintéticos | Transacción atómica completada en $<50$ ms | **PASÓ** (`test_lakehouse.py`) |
| **TC-015** | `imputer.algorithms` | Imputación KNN y MICE preservando la covarianza de la muestra. | Matriz con 20% de valores faltantes MAR | Matriz completa sin NaNs y $\Delta \sigma^2 < 10\%$ | **NUEVO** (A integrar en Sprint 1) |

---

## 4. Batería de Fixtures y Configuración de Pruebas

Los tests implementan el archivo `tests/conftest.py` con fixtures estándar:
- `sample_raw_dataframe`: DataFrame sintético con tipos mixtos, strings monetarios, valores nulos controlados y PII.
- `temp_lakehouse_dirs`: Fixture que genera directorios efímeros para `bronze/`, `silver/`, `gold/` y `quality_reports/`.
- `in_memory_db`: Instancia aislada de `DatabaseManager` sobre `:memory:` para pruebas transaccionales sin ensuciar disco.

---

## 5. Criterios de Suspensión y Reanudación

- **Suspensión**: Las pruebas se suspenden si más de 2 tests unitarios fallan, o si la verificación criptográfica SHA-256 detecta divergencias en los Parquets de Bronze.
- **Reanudación**: El código modificado debe compilar limpiamente bajo `pytest tests/` con cero fallos antes de permitir un commit o merge a la rama principal.

---

## 6. Métricas de Cobertura y Quality Gates

| Métrica | Meta Mínima | Estado Actual | Estado de Cumplimiento |
|---|:---:|:---:|:---:|
| **Cobertura de Líneas (`pytest-cov`)** | 80% | 84.6% | **CUMPLIDO** |
| **Tasa de Éxito de Pruebas Unitarias** | 100% | 100% (23/23) | **CUMPLIDO** |
| **Linter PEP 8 / Flake8 / Ruff** | 0 Errores Críticos | 0 Errores Críticos | **CUMPLIDO** |
| **Tiempo de Ejecución Suite de Tests** | $< 15$ segundos | 6.38 segundos | **CUMPLIDO** |
