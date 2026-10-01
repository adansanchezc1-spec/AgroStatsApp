# Módulo de Exploración y Carga para Notebooks (`src/notebook_code`)

**Plataforma**: AgroData Intelligence Platform (AgroStatsApp)  
**Fase PDCO**: **DEVELOPMENT** | **Active Skill**: `03-development`  
**Destinado a**: [`CRISPDM/notebooks/imputer.ipynb`](file:///c:/Users/ADAN/OneDrive/Documentos/Statsfirm/AgroStats%20AndTech/AgroStatsApp/CRISPDM/notebooks/imputer.ipynb)

---

## 1. Propósito

Este paquete proporciona las utilidades necesarias para que el notebook `imputer.ipynb` (o cualquier notebook de investigación CRISP-DM) pueda:
1. **Cargar automáticamente los DataFrames** desde `data/RAW` (formatos CSV, JSON, XLSX) sin lidiar con rutas absolutas ni codificaciones complejas.
2. **Explorar informáticamente cada dataset**:
   - **Metadatos y Contexto**: Filas, columnas, uso de memoria, tipos de datos.
   - **Granularidad Temporal**: Rango de fechas, frecuencia, días cubiertos, fechas únicas.
   - **Granularidad Espacial**: Detección de municipios, departamentos, estaciones meteorológicas y coordenadas.
   - **Valores Nulos**: Conteo, porcentaje, filas completas vs incompletas, columnas afectadas.
   - **Duplicados**: Conteo y porcentaje de duplicados exactos.
   - **Claves Candidatas**: Detección de columnas con unicidad del 100%.
   - **Visualizaciones**: Mapas de calor matriciales de ausencias e histogramas de distribución.
3. **Conectar con el Motor de Imputación Inteligente (`IntelligentImputer`)**:
   - Diagnóstico del mecanismo de pérdida (MCAR, MAR, MNAR según Rubin y prueba de Little).
   - Torneo competitivo entre algoritmos (Interpolación temporal, KNN, MICE, Mediana Condicional).
   - Banderas de auditoría (`_is_imputed`, `_impute_method`).
   - Comparación de varianza antes y después de la imputación.

---

## 2. Código Listo para Usar en `imputer.ipynb`

Copia y pega las siguientes celdas en tu notebook:

### Celda 1: Importación e Inicialización Universal del Entorno (Local y Google Colab)
```python
import sys
import os
from pathlib import Path

# Configuración universal de rutas (compatible con Windows, VS Code, Linux y Google Colab)
def setup_environment():
    # 1. Soporte automático para Google Colab
    if "google.colab" in sys.modules:
        print("[INFO] Entorno detectado: Google Colab")
        repo_path = Path("/content/Statsfirm")
        if not repo_path.exists():
            print("[INFO] Clonando repositorio AgroStats en Colab...")
            os.system("git clone https://github.com/adansanchezc1-spec/Statsfirm.git /content/Statsfirm")
        colab_src = Path("/content/Statsfirm/AgroStats AndTech/AgroStatsApp/src")
        if colab_src.exists() and str(colab_src) not in sys.path:
            sys.path.insert(0, str(colab_src))
            print(f"[OK] Ruta agregada en Colab: {colab_src}")
            return str(colab_src)

    # 2. Soporte para Entorno Local (Windows / Linux / VS Code / Jupyter)
    candidates = [
        Path(r"c:\Users\ADAN\OneDrive\Documentos\Statsfirm\AgroStats AndTech\AgroStatsApp\src"),
        Path("/mnt/c/Users/ADAN/OneDrive/Documentos/Statsfirm/AgroStats AndTech/AgroStatsApp/src"),
        Path.cwd() / "src",
        Path.cwd() / "AgroStats AndTech" / "AgroStatsApp" / "src",
        Path.cwd().parent / "src",
        Path.cwd().parent.parent / "src",
        Path.cwd().parent.parent / "AgroStats AndTech" / "AgroStatsApp" / "src",
    ]
    for c in candidates:
        if c.exists() and (c / "notebook_code").is_dir():
            resolved = str(c.resolve())
            if resolved not in sys.path:
                sys.path.insert(0, resolved)
            print(f"[OK] Ruta detectada: {resolved}")
            return resolved

    # 3. Búsqueda hacia arriba en el árbol de directorios
    curr = Path.cwd().resolve()
    for _ in range(6):
        target = curr / "AgroStats AndTech" / "AgroStatsApp" / "src"
        if target.exists() and (target / "notebook_code").is_dir():
            resolved = str(target.resolve())
            if resolved not in sys.path:
                sys.path.insert(0, resolved)
            print(f"[OK] Ruta encontrada en ancestro: {resolved}")
            return resolved
        curr = curr.parent

    print(f"[ALERTA] No se detectó la carpeta src. Directorio actual: {Path.cwd()}")
    return None

setup_environment()

# Importar herramientas especializadas de notebook_code
from notebook_code import (
    RawDataLoader,
    DatasetProfiler,
    NotebookImputerBridge,
    load_all_raw_datasets,
    load_raw_dataset,
    explore_dataset,
)

print("[OK] Módulos de notebook_code importados exitosamente.")
```

### Celda 2: Carga de Todos los DataFrames desde `data/RAW`
```python
# Cargar automáticamente los 10 datasets oficiales presentes en data/RAW
datasets = load_all_raw_datasets()

print(f"Total de datasets cargados: {len(datasets)}\n")
for name, df in datasets.items():
    print(f"• {name:25} -> {df.shape[0]:5} filas x {df.shape[1]:2} columnas")
```

### Celda 3: Exploración Informática Completa de un Dataset (ej. Pluviometría IDEAM)
```python
# Seleccionar un dataset para exploración a profundidad
df_pluvio = datasets["ideam_pluvio"]

# Diagnóstico informático en formato estructurado
perfil = explore_dataset(df_pluvio, dataset_name="IDEAM Pluviometría")

print("=== METADATOS Y CONTEXTO ===")
for k, v in perfil["metadata"].items():
    print(f"  {k}: {v}")

print("\n=== ANÁLISIS DE DATOS NULOS Y AUSENCIAS ===")
print(f"  Tasa global de nulos: {perfil['missingness']['global_missing_rate_pct']}%")
print(f"  Filas completas: {perfil['missingness']['complete_rows_count']} ({perfil['missingness']['complete_rows_pct']}%)")
print(f"  Columnas con nulos: {perfil['missingness']['columns_with_missing']}")

print("\n=== DUPLICADOS Y CLAVES CANDIDATAS ===")
print(f"  Filas duplicadas: {perfil['duplication']['exact_duplicate_rows']} ({perfil['duplication']['duplicate_rate_pct']}%)")
print(f"  Claves candidatas (100% únicas): {perfil['duplication']['unique_key_candidates']}")

print("\n=== GRANULARIDAD TEMPORAL Y ESPACIAL ===")
print("  Temporal:", perfil["granularity"]["temporal_features"])
print("  Espacial:", list(perfil["granularity"]["spatial_features"].keys()))
```

### Celda 4: Tabla Resumen Columna por Columna (Lista para Jupyter)
```python
# Generar tabla de perfilamiento detallada lista para visualizar
tabla_resumen = DatasetProfiler.profile_table(df_pluvio)
display(tabla_resumen)
```

### Celda 5: Visualización de Matriz de Ausencias e Histogramas
```python
# 1. Mapa de calor matricial de datos faltantes
fig_missing = DatasetProfiler.plot_missingness_heatmap(df_pluvio)
fig_missing.show()

# 2. Histogramas y densidades de variables numéricas
fig_dist = DatasetProfiler.plot_distributions(df_pluvio, max_features=4)
if fig_dist:
    fig_dist.show()
```

### Celda 6: Diagnóstico Estadístico de Rubin y Torneo de Imputación
```python
# Instanciar el puente de imputación
bridge = NotebookImputerBridge(variance_penalty_weight=1.5)

# 1. Diagnóstico del mecanismo de pérdida (MCAR vs MAR)
diagnostico = bridge.diagnose(df_pluvio)
print(f"Mecanismo diagnosticado: {diagnostico.diagnosed_mechanism}")
print(f"Estrategia sugerida:     {diagnostico.recommended_strategy}")

# 2. Torneo competitivo de algoritmos con penalización de varianza
df_imputado, tabla_benchmark, resultado = bridge.run_benchmark(df_pluvio)

print("\n=== RESULTADOS DEL BENCHMARK COMPETITIVO ===")
display(tabla_benchmark)
print(f"\nAlgoritmo ganador: {resultado.winning_algorithm_name} (Score: {resultado.winning_score:.4f})")
```

### Celda 7: Auditoría Visual de Preservación de Varianza
```python
# Comparar distribución antes vs después para auditar que la variabilidad natural se conserve
if "valorobservado" in df_pluvio.columns:
    fig_comp = NotebookImputerBridge.plot_imputation_comparison(
        original_df=df_pluvio,
        imputed_df=df_imputado,
        feature_col="valorobservado"
    )
    if fig_comp:
        fig_comp.show()
```
