"""Generador Automatizado de Reportes Ejecutivos e Inteligencia Agroclimática.
Fase PDCO: OPERATIONS | Estándar: DAMA-DMBOK 2 / ISO/IEC 25010 / Clean Code
Consolidación de auditorías de calidad, alertas de riesgo climático e índices de mercado.
"""

from __future__ import annotations
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from jinja2 import Template

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("reports.generator")


class AgroRiskAssessment:
    """Motor de clasificación de riesgo agroclimático y económico."""

    @staticmethod
    def classify_spi(spi_val: float) -> str:
        """Clasifica el nivel de estrés hídrico según normas de la OMM (WMO)."""
        if pd.isna(spi_val):
            return "DATOS_INSUFICIENTES"
        if spi_val <= -2.0:
            return "SEQUIA_EXTREMA"
        if spi_val <= -1.5:
            return "SEQUIA_SEVERA"
        if spi_val <= -1.0:
            return "SEQUIA_MODERADA"
        if spi_val >= 2.0:
            return "HUMEDAD_EXTREMA"
        if spi_val >= 1.5:
            return "HUMEDAD_SEVERA"
        if spi_val >= 1.0:
            return "HUMEDAD_MODERADA"
        return "NORMAL_CLIMATICO"

    @staticmethod
    def classify_thermal_anomaly(z_val: float) -> str:
        """Clasifica la severidad de anomalía térmica mensual."""
        if pd.isna(z_val):
            return "DATOS_INSUFICIENTES"
        if z_val >= 2.0:
            return "ALERTA_CALOR_CRITICA"
        if z_val >= 1.0:
            return "ANOMALIA_CALIDA_MODERADA"
        if z_val <= -2.0:
            return "ALERTA_FRIO_CRITICA"
        if z_val <= -1.0:
            return "ANOMALIA_FRIA_MODERADA"
        return "TEMPERATURA_ESTABLE"

    @staticmethod
    def classify_inflation_risk(inflation_pct: float) -> str:
        """Clasifica el riesgo de sobrecosto por inflación de insumos agrícolas."""
        if pd.isna(inflation_pct):
            return "DATOS_INSUFICIENTES"
        if inflation_pct >= 25.0:
            return "ESTRES_COSTOS_CRITICO"
        if inflation_pct >= 12.0:
            return "ESTRES_COSTOS_MODERADO"
        if inflation_pct < 0.0:
            return "DEFLACION_INSUMOS"
        return "ESTRUCTURA_COSTOS_ESTABLE"


class ReportGenerator:
    """Generador de reportes ejecutivos en formatos Markdown y HTML."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or (settings.BASE_DIR / "reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_executive_report(
        self,
        summary_stats: Dict[str, Any],
        output_filename: str = "informe_ejecutivo_agrostats",
    ) -> Dict[str, str]:
        """
        Compila el informe ejecutivo consolidando calidad de datos, métricas y riesgos.
        Exporta tanto archivo Markdown (.md) como HTML enriquecido (.html).
        """
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md_template_str = """# Informe Ejecutivo de Inteligencia Agroclimática
**Plataforma**: AgroStats Intelligence Platform (`AgroStatsApp`)  
**Fecha de Emisión**: {{ generated_at }}  
**Marco de Trabajo**: PDCO (Plan-Development-Control-Operations) / SWEBOK v4 / DAMA-DMBOK 2  

---

## 1. Resumen Ejecutivo del Pipeline
- **Datasets Procesados en Bronze**: {{ stats.get('bronze_datasets_count', 0) }}
- **Registros Sanitizados en Silver**: {{ stats.get('silver_rows_count', 0) }}
- **Tasa de Conformidad de Calidad**: {{ stats.get('data_quality_pass_rate', '100%') }}
- **Estado de Integridad Criptográfica**: {{ stats.get('sha256_audit_status', 'CONFORME') }}

---

## 2. Diagnóstico de Riesgo Agroclimático (Gold)
| Dimensión Analítica | Valor Reciente | Clasificación de Riesgo |
|---------------------|----------------|-------------------------|
| **Índice de Sequía (SPI-3)** | {{ stats.get('latest_spi', '0.0') }} | **{{ stats.get('spi_risk_label', 'NORMAL') }}** |
| **Anomalía Térmica ($Z_T$)** | {{ stats.get('latest_temp_z', '0.0') }} | **{{ stats.get('temp_risk_label', 'ESTABLE') }}** |
| **Inflación Fertilizantes (YoY)** | {{ stats.get('latest_inflation', '0.0%') }} | **{{ stats.get('inflation_risk_label', 'ESTABLE') }}** |

---

## 3. Estado del Repositorio de Datos (Relational Star Schema)
- **Base de Datos**: {{ stats.get('db_engine', 'SQLite / DuckDB') }}
- **Municipios DIVIPOLA Reconciliados**: {{ stats.get('mdm_municipios_count', 0) }}
- **Observaciones en Modelo Estrella**: {{ stats.get('star_schema_rows', 0) }}

---

*Generado automáticamente por el motor de reportes de AgroStatsApp bajo lineamientos ISO/IEC 25010.*
"""

        template = Template(md_template_str)
        rendered_md = template.render(generated_at=now_str, stats=summary_stats)

        md_path = self.output_dir / f"{output_filename}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(rendered_md)

        # Generar también versión HTML
        html_template_str = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe Ejecutivo AgroStats</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 40px auto; padding: 20px; background-color: #f8f9fa; }
        .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #1e4620; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; }
        h2 { color: #2e7d32; margin-top: 25px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #e8f5e9; color: #1b5e20; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; background: #c8e6c9; color: #1b5e20; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Informe Ejecutivo AgroStats</h1>
        <p><strong>Fecha:</strong> {{ generated_at }} | <strong>Fase:</strong> OPERATIONS</p>
        <h2>Diagnóstico de Riesgo Agroclimático</h2>
        <table>
            <tr><th>Indicador</th><th>Valor</th><th>Estado de Riesgo</th></tr>
            <tr><td>Índice de Sequía (SPI-3)</td><td>{{ stats.get('latest_spi', '0.0') }}</td><td><span class="badge">{{ stats.get('spi_risk_label', 'NORMAL') }}</span></td></tr>
            <tr><td>Anomalía Térmica (Z)</td><td>{{ stats.get('latest_temp_z', '0.0') }}</td><td><span class="badge">{{ stats.get('temp_risk_label', 'ESTABLE') }}</span></td></tr>
            <tr><td>Inflación Fertilizantes YoY</td><td>{{ stats.get('latest_inflation', '0.0%') }}</td><td><span class="badge">{{ stats.get('inflation_risk_label', 'ESTABLE') }}</span></td></tr>
        </table>
    </div>
</body>
</html>"""
        html_template = Template(html_template_str)
        rendered_html = html_template.render(generated_at=now_str, stats=summary_stats)

        html_path = self.output_dir / f"{output_filename}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        logger.info("Reporte ejecutivo emitido: %s (.md y .html)", output_filename)
        return {
            "markdown_path": str(md_path),
            "html_path": str(html_path),
        }
