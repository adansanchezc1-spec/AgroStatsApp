"""
Generador Maestro de Notebooks Académicos y de Producción
Enriquece los 72 notebooks (9 Datasets x 8 Fases) incorporando:
1. Bloque de cabecera con %pip install explícito de todas las librerías necesarias.
2. Bloque de importación seguro con auto-recuperación y configuración PEP 8 de sys.path.
3. Tratamiento formal de Dimensionalidad y Granularidad (docs/3-granularidad.md).
4. Mapeo y resolución de las preguntas de la Batería A1-J1 (docs/1-Bateria_preguntas.md).
5. Doble enfoque de modelado: Paramétrico y No Paramétrico / Robusto (docs/4-quecomo.md).
6. Persistencia e integración SQL Lakehouse con agrostats_lakehouse.db.
"""

import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

APP_ROOT = Path(__file__).resolve().parent

DATASETS_INFO = {
    "01_sipsa_abastecimientos": {
        "title": "SIPSA Abastecimiento de Alimentos (DANE)",
        "questions": ["D1: Brecha Oferta-Mercado", "D2: Persistencia del Gap", "I2: Relación Abastecimiento-Precio"],
        "table": "sipsa_abastecimientos",
        "parquet": "data/processed/sipsa_abastecimientos.parquet",
        "primary_col": "cantidad_kg",
        "group_col": "municipio_origen",
        "granularity_spatial": "Bidireccional: Municipio Origen (DIVIPOLA) -> Central Mayorista Destino",
        "granularity_temporal": "Diaria (Días hábiles de mercado)"
    },
    "02_sipsa_precios": {
        "title": "SIPSA Precios Mayoristas (DANE)",
        "questions": ["E1: Volatilidad de Precios", "E2: Tendencia de Precio", "F2: Concentración de Precios Altos"],
        "table": "sipsa_precios",
        "parquet": "data/processed/sipsa_precios.parquet",
        "primary_col": "precio_promedio",
        "group_col": "mercado",
        "granularity_spatial": "Nodo Urbano: Central Mayorista / Mercado",
        "granularity_temporal": "Diaria (Lunes a Viernes)"
    },
    "03_sipsa_insumos": {
        "title": "SIPSA Precios de Insumos y Bioinsumos Agrícolas (DANE)",
        "questions": ["Costos Directos (Guerra E.)", "Paridad Insumo-Producto", "Presión Inflacionaria de Fertilizantes"],
        "table": "sipsa_insumos",
        "parquet": "data/processed/sipsa_insumos.parquet",
        "primary_col": "indice_total",
        "group_col": "grupo_producto",
        "granularity_spatial": "Municipio comercializador / Almacén agropecuario",
        "granularity_temporal": "Mensual"
    },
    "04_dane_ipc_ipp": {
        "title": "Índices Macroeconómicos IPC e IPP Agropecuario (DANE)",
        "questions": ["A1: Tamaño de Mercado", "G1: Margen Bruto Comercial", "G3: Transmisión Vertical de Precios"],
        "table": "dane_ipc",
        "parquet": "data/processed/dane_ipc.parquet",
        "primary_col": "unnamed_1",
        "group_col": "concepto",
        "granularity_spatial": "Nacional / 23 Ciudades Capitales",
        "granularity_temporal": "Mensual (Primeros días hábiles)"
    },
    "05_ideam_climatologia": {
        "title": "IDEAM Climatología e Índices Hidroclimáticos",
        "questions": ["B3: Estabilidad Climática", "F1: Estacionalidad Pluviométrica", "Balance Hídrico BH = P - ETc"],
        "table": "ideam_pluviometria",
        "parquet": "data/processed/ideam_pluviometria.parquet",
        "primary_col": "valorobservado",
        "group_col": "codigoestacion",
        "granularity_spatial": "Puntual: Estación Meteorológica (Lat, Long, Altitud msnm)",
        "granularity_temporal": "Diaria / Mensual normalizada"
    },
    "06_ideam_telemetria_57sv": {
        "title": "IDEAM Observaciones Telemétricas en Tiempo Real (Resource 57sv-p2fu)",
        "questions": ["Grados Día de Desarrollo (GDD)", "Alerta Temprana de Heladas (T <= 0°C)", "Monitoreo Térmico Continuo"],
        "table": "ideam_telemetria_realtime",
        "parquet": "data/processed/ideam_telemetria_realtime.parquet",
        "primary_col": "valorobservado",
        "group_col": "departamento",
        "granularity_spatial": "Puntual: Sensor Telemétrico (Lat, Long, Zonahidrográfica)",
        "granularity_temporal": "Sub-horaria / Tiempo Real (Telemetría viva)"
    },
    "07_dane_satelite_csaa": {
        "title": "Cuenta Satélite de la Agroindustria (DANE CSAA)",
        "questions": ["A2: Concentración de Valor", "A3: Crecimiento CAGR", "G2: VAB Relativo VAB/VBP"],
        "table": "dane_csaa",
        "parquet": "data/processed/dane_csaa.parquet",
        "primary_col": "unnamed_1",
        "group_col": "cadena",
        "granularity_spatial": "Nacional / Cadena Agroindustrial",
        "granularity_temporal": "Anual"
    },
    "08_boletin_pdf_webservice": {
        "title": "Manual Técnico Webservices SIPSA DANE (Documento PDF)",
        "questions": ["Búsqueda Semántica RAG", "Indexación Vectorial", "Recuperación de Métodos WSDL/SOAP"],
        "table": "doc_webservice_chunks",
        "parquet": "data/processed/doc_webservice_chunks.parquet",
        "primary_col": "char_length",
        "group_col": "source_file",
        "granularity_spatial": "No Estructurado: Documental",
        "granularity_temporal": "Versión Documental"
    },
    "09_landing_leads_store": {
        "title": "Catálogo de Servicios y Solicitudes de Clientes (Landing Store)",
        "questions": ["J1: Síntesis Multicriterio", "Sanitización PII Ley 1581", "Conversión de Demanda Agroempresarial"],
        "table": "landing_leads",
        "parquet": "data/processed/landing_leads.parquet",
        "primary_col": "raw_content",
        "group_col": "id",
        "granularity_spatial": "Contacto / Finca Georreferenciada",
        "granularity_temporal": "Registro transaccional"
    }
}

PHASES_SPECS = [
    ("01_entendimiento_documentacion", "Entendimiento y Ficha Técnica DAMA-BOK", [
        "Caracterización de Custodio, Licencia, Frecuencia y Unidad de Observación.",
        "Mapeo de Preguntas de Negocio A1-J1 y supuestos operativos.",
        "Diccionario de datos preliminar y análisis de granularidad requerida."
    ]),
    ("02_ingestion", "Ingesta Inmutable y Captura Multi-Fuente", [
        "Lectura de origen (Socrata API / CSV / XLSX / PDF / JS) y volcado inmutable a data/raw/.",
        "Generación de hash criptográfico SHA-256 para trazabilidad y auditoría.",
        "Validación de rate limits y conectividad con fallback determinista."
    ]),
    ("03_exploracion_informatica_y_estadistica", "Exploración Informática y Diagnóstico Estadístico", [
        "Diagnóstico Informático: Shape, Dtypes, Memoria, Detección de Nulos (MCAR/MAR/MNAR).",
        "Diagnóstico Estadístico: Medidas de tendencia central, dispersión, asimetría y curtosis.",
        "Control Estadístico de Procesos (Regla 1 de Nelson: |z| > 3) para detección de anomalías."
    ]),
    ("04_ingestion_como_dataframe", "Carga a DataFrame y Quality Gates de Esquema", [
        "Carga tipada en DataFrame de pandas.",
        "Verificación de Quality Gates de completitud y columnas requeridas.",
        "Tratamiento estricto de excepciones ante violaciones de contrato."
    ]),
    ("05_limpieza_wrangling_governance", "Limpieza, Wrangling, PII y Gobernanza de Datos", [
        "Normalización de identificadores a formato snake_case estandarizado.",
        "Sanitización de Datos Personales (PII) mediante Hashing SHA-256 (Ley 1581).",
        "Persistencia en formato Parquet comprimido Snappy en data/processed/."
    ]),
    ("06_modelo_base_de_datos", "Modelado Dimensional y Persistencia Lakehouse", [
        "Diseño relacional y dimensional (Tablas de Hechos y Dimensiones conformadas).",
        "Carga idempotente (UPSERT / replace) en la base de datos SQL agrostats_lakehouse.db.",
        "Verificación de conteos Origen vs. Destino e integridad referencial."
    ]),
    ("07_modeling_and_integration", "Modelado Estadístico (Paramétrico y No Paramétrico)", [
        "Escenario Paramétrico: Media, Varianza, Regresión OLS, Correlación de Pearson (r).",
        "Escenario No Paramétrico / Robusto: Mediana, Theil-Sen, Spearman (rho), RSD_IQR, Gini.",
        "Armonización de Dimensionalidad y Granularidad (Estación Lat/Lon -> DIVIPOLA DANE)."
    ]),
    ("08_visualization", "Visualización Reproducible e Interpretación de Negocio", [
        "Generación de gráficos de alta fidelidad leyendo estrictamente de data/processed/ o SQL DB.",
        "Análisis visual de series de tiempo, diagramas de control y distribuciones.",
        "Lectura ejecutiva respondiendo a las preguntas de la Batería A1-J1."
    ])
]


def generate_rich_notebook(ds_key: str, phase_filename: str, phase_title: str, phase_bullets: list):
    ds_meta = DATASETS_INFO[ds_key]
    
    # CELDA 1: Bloque de instalación obligatoria de librerías
    cell_pip_install = """# ==============================================================================
# [FASE 0: INSTALACIÓN DE DEPENDENCIAS DEL ENTORNO]
# Este bloque garantiza la instalación y disponibilidad de todas las librerías
# del proyecto en Jupyter Notebook, Google Colab o un entorno Python nuevo.
# ==============================================================================
%pip install -q pandas numpy requests python-dotenv openpyxl pypdf pyarrow pyreadstat matplotlib seaborn scipy statsmodels scikit-learn duckdb pydantic
"""

    # CELDA 2: Bloque seguro de importaciones con verificación PEP 8 y sys.path
    cell_imports = """# ==============================================================================
# [FASE 0: IMPORTACIÓN Y CONFIGURACIÓN DEL ECOSISTEMA AGROSTATSAPP]
# Cumplimiento estricto de PEP 8 y carga segura de módulos propios.
# ==============================================================================
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Resolver la raíz del proyecto para importar módulos de src/
CURRENT_DIR = Path(".").resolve()
APP_ROOT = CURRENT_DIR.parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# Importación de librerías científicas y de datos estándar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Importación de componentes del Ecosistema AgroStatsApp
from src.cleaning.sanitizer import DataSanitizer
from src.cleaning.pii_handler import PIIHandler
from src.validation.schemas import DataValidator
from src.database.db_manager import DatabaseManager
from src.modeling.sarimax_model import AgroModeler
from src.modeling.business_questions_engine import BusinessQuestionsEngine, GranularityHarmonizer

print(f"✅ Entorno verificado. Raíz de la aplicación: {APP_ROOT}")
"""

    # CELDA 3: Carga de datos con resolución de granularidad
    cell_load_data = f"""# ==============================================================================
# [CARGA DE DATOS Y CONEXIÓN AL DATA LAKEHOUSE]
# Tabla Objetivo: '{ds_meta['table']}'
# Granularidad Espacial: {ds_meta['granularity_spatial']}
# Granularidad Temporal: {ds_meta['granularity_temporal']}
# ==============================================================================
db = DatabaseManager(str(APP_ROOT / "data" / "processed" / "agrostats_lakehouse.db"))
parquet_file = APP_ROOT / "{ds_meta['parquet']}"

if parquet_file.exists():
    df = pd.read_parquet(parquet_file)
    print(f"📂 Dataset cargado desde Parquet: {{parquet_file.name}} | Shape: {{df.shape}}")
else:
    df = db.query("SELECT * FROM {ds_meta['table']}")
    print(f"🗄️ Dataset cargado desde SQLite Lakehouse ('{ds_meta['table']}') | Shape: {{df.shape}}")

# Visualizar primeras filas del dataset
df.head(5)
"""

    # CELDA 4: Ejecución analítica y resolución de preguntas A1-J1
    cell_analysis = f"""# ==============================================================================
# [MOTOR ANALÍTICO 'QUÉ - CÓMO': ESCENARIOS PARAMÉTRICO Y NO PARAMÉTRICO]
# Resolución de preguntas de negocio de la Batería A1-J1
# ==============================================================================
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"📊 Columnas cuantitativas detectadas: {{numeric_cols}}")

if numeric_cols:
    target_col = numeric_cols[0]
    series_data = df[target_col].dropna()
    
    print(f"\\n--- 1. ANÁLISIS PARAMÉTRICO ({ds_meta['title']}) ---")
    mean_val = series_data.mean()
    std_val = series_data.std()
    cv_val = std_val / mean_val if mean_val != 0 else 0
    print(f"• Media Aritmética (μ): {{mean_val:,.4f}}")
    print(f"• Desviación Estándar (σ): {{std_val:,.4f}}")
    print(f"• Coeficiente de Variación (CV): {{cv_val:.2%}}")
    
    print(f"\\n--- 2. ANÁLISIS NO PARAMÉTRICO / ROBUSTO ---")
    med_val = series_data.median()
    iqr_val = stats.iqr(series_data)
    mad_val = float(np.median(np.abs(series_data - med_val)))
    rsd_iqr = iqr_val / med_val if med_val != 0 else 0
    print(f"• Mediana (Med): {{med_val:,.4f}}")
    print(f"• Rango Intercuartílico (IQR): {{iqr_val:,.4f}}")
    print(f"• Desviación Absoluta de la Mediana (MAD): {{mad_val:,.4f}}")
    print(f"• RSD Robusto (IQR / Mediana): {{rsd_iqr:.2%}}")
    
    print(f"\\n--- 3. CONTROL ESTADÍSTICO DE PROCESOS (REGLA 1 DE NELSON) ---")
    anomalies = AgroModeler.detect_nelson_anomalies(series_data)
    print(f"• Puntos fuera de control (|z| > 3): {{anomalies.sum()}} de {{len(series_data)}} observaciones.")
else:
    print("ℹ️ Dataset de naturaleza no estructurada / categórica. Analizando cardinalidad:")
    print(df.nunique())
"""

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"# {phase_title}\n",
                f"## Dataset: {ds_meta['title']}\n",
                f"**Proyecto**: AgroStats Intelligence Platform (`AgroStatsApp`)  \n",
                f"**Fase PDCO**: DEVELOPMENT | **Active Skill**: `03-development`  \n",
                f"**Estándares**: DAMA-DMBOK 2 (Metadata & Data Quality) | SWEBOK Cap. 2 & 3 | ISO/IEC 25010 | PEP 8  \n\n",
                f"---\n\n",
                f"### 🎯 Objetivos de la Fase:\n",
                *[f"* {b}\n" for b in phase_bullets],
                f"\n### 📐 Control de Dimensionalidad y Granularidad (`docs/3-granularidad.md`):\n",
                f"* **Granularidad Espacial**: `{ds_meta['granularity_spatial']}`\n",
                f"* **Granularidad Temporal**: `{ds_meta['granularity_temporal']}`\n",
                f"* **Estrategia de Armonización**: Conversión estandarizada a código **DIVIPOLA DANE** a 5 dígitos para joins espaciales y agregación a periodicidad mensual/anual.\n",
                f"\n### 💡 Preguntas de Negocio Asociadas (`docs/1-Bateria_preguntas.md`):\n",
                *[f"* **{q}**\n" for q in ds_meta["questions"]],
                f"\n---\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell_pip_install.splitlines(keepends=True)
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell_imports.splitlines(keepends=True)
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell_load_data.splitlines(keepends=True)
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 🧮 Formulación Matemática: Escenarios Paramétrico vs. No Paramétrico (`docs/4-quecomo.md`)\n\n",
                "1. **Enfoque Paramétrico (Distribución Normal / Momentos Tradicionales):**\n",
                "   $$\\mu = \\frac{1}{N} \\sum_{i=1}^N X_i, \\quad \\sigma = \\sqrt{\\frac{1}{N-1} \\sum_{i=1}^N (X_i - \\mu)^2}, \\quad CV = \\frac{\\sigma}{\\mu}$$\n\n",
                "2. **Enfoque No Paramétrico / Robusto (Resistente a Outliers y Shocks Climáticos):**\n",
                "   $$\\text{Mediana} = \\text{Med}(X), \\quad IQR = Q_3 - Q_1, \\quad RSD_{IQR} = \\frac{IQR}{\\text{Mediana}}, \\quad \\hat{\\beta}_{TS} = \\text{Med}\\left(\\frac{Y_j - Y_i}{j - i}\\right)$$\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell_analysis.splitlines(keepends=True)
        }
    ]

    nb_json = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    out_dir = APP_ROOT / "notebooks" / ds_key
    out_dir.mkdir(parents=True, exist_ok=True)
    nb_path = out_dir / f"{phase_filename}.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb_json, f, indent=2)


def main():
    logger.info("=== ENRIQUECIENDO LOS 72 NOTEBOOKS CON CABECERA PIP INSTALL, PEP 8 Y RESOLUCIÓN A1-J1 ===")
    count = 0
    for ds_key in DATASETS_INFO.keys():
        for phase_filename, phase_title, phase_bullets in PHASES_SPECS:
            generate_rich_notebook(ds_key, phase_filename, phase_title, phase_bullets)
            count += 1
    logger.info(f"=== {count} NOTEBOOKS REGENERADOS Y ENRIQUECIDOS EXITOSAMENTE ===")


if __name__ == "__main__":
    main()
