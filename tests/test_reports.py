"""Pruebas Unitarias para el Módulo de Reportes Ejecutivos (Fase Operations).
Fase PDCO: CONTROL | Estándar: ISO/IEC 25010 / Clean Code
Casos de prueba: TC-801 a TC-803.
"""

from pathlib import Path
import pytest

from src.reports.generator import AgroRiskAssessment, ReportGenerator


class TestAgroRiskAssessment:
    """TC-801: Pruebas unitarias para reglas de clasificación de riesgo agroclimático."""

    def test_classify_spi(self):
        """Verifica categorización de estrés hídrico y sequía."""
        assert AgroRiskAssessment.classify_spi(-2.5) == "SEQUIA_EXTREMA"
        assert AgroRiskAssessment.classify_spi(-1.6) == "SEQUIA_SEVERA"
        assert AgroRiskAssessment.classify_spi(-1.2) == "SEQUIA_MODERADA"
        assert AgroRiskAssessment.classify_spi(0.2) == "NORMAL_CLIMATICO"
        assert AgroRiskAssessment.classify_spi(1.8) == "HUMEDAD_SEVERA"
        assert AgroRiskAssessment.classify_spi(None) == "DATOS_INSUFICIENTES"

    def test_classify_thermal_anomaly(self):
        """Verifica umbrales de anomalía térmica estandarizada."""
        assert AgroRiskAssessment.classify_thermal_anomaly(2.3) == "ALERTA_CALOR_CRITICA"
        assert AgroRiskAssessment.classify_thermal_anomaly(1.2) == "ANOMALIA_CALIDA_MODERADA"
        assert AgroRiskAssessment.classify_thermal_anomaly(0.1) == "TEMPERATURA_ESTABLE"
        assert AgroRiskAssessment.classify_thermal_anomaly(-2.1) == "ALERTA_FRIO_CRITICA"

    def test_classify_inflation_risk(self):
        """Verifica umbrales de riesgo económico por encarecimiento de insumos."""
        assert AgroRiskAssessment.classify_inflation_risk(30.0) == "ESTRES_COSTOS_CRITICO"
        assert AgroRiskAssessment.classify_inflation_risk(15.0) == "ESTRES_COSTOS_MODERADO"
        assert AgroRiskAssessment.classify_inflation_risk(4.5) == "ESTRUCTURA_COSTOS_ESTABLE"
        assert AgroRiskAssessment.classify_inflation_risk(-2.0) == "DEFLACION_INSUMOS"


class TestReportGenerator:
    """TC-802 & TC-803: Pruebas unitarias para generación de reportes Markdown y HTML."""

    @pytest.fixture
    def generator(self, tmp_path: Path):
        return ReportGenerator(output_dir=tmp_path)

    def test_generate_executive_report_creates_files(self, generator):
        """TC-802 & TC-803: Verifica renderizado y persistencia de reportes .md y .html."""
        sample_stats = {
            "bronze_datasets_count": 11,
            "silver_rows_count": 55000,
            "data_quality_pass_rate": "98.5%",
            "sha256_audit_status": "CONFORME",
            "latest_spi": "-1.4",
            "spi_risk_label": "SEQUIA_MODERADA",
            "latest_temp_z": "1.8",
            "temp_risk_label": "ANOMALIA_CALIDA_MODERADA",
            "latest_inflation": "18.2%",
            "inflation_risk_label": "ESTRES_COSTOS_MODERADO",
            "db_engine": "SQLite Relational Star Schema",
            "mdm_municipios_count": 1122,
            "star_schema_rows": 55000,
        }

        output_paths = generator.generate_executive_report(
            summary_stats=sample_stats,
            output_filename="test_informe_ejecutivo",
        )

        md_file = Path(output_paths["markdown_path"])
        html_file = Path(output_paths["html_path"])

        assert md_file.exists()
        assert html_file.exists()

        # Verificar contenido de los archivos
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
            assert "Informe Ejecutivo de Inteligencia Agroclimática" in md_content
            assert "SEQUIA_MODERADA" in md_content
            assert "98.5%" in md_content

        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
            assert "<!DOCTYPE html>" in html_content
            assert "Informe Ejecutivo AgroStats" in html_content
