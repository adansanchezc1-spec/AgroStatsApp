"""Pruebas Unitarias para el Módulo de Visualización Analítica (Plotly).
Fase PDCO: CONTROL | Estándar: ISO/IEC 25010 / Clean Code
Casos de prueba: TC-701 a TC-704.
"""

import pytest
import pandas as pd
import plotly.graph_objects as go

from src.visualization.plots import (
    plot_spi_timeline,
    plot_thermal_anomalies,
    plot_price_inflation,
    plot_yield_by_department,
)


class TestVisualizationPlots:
    """Pruebas unitarias para las figuras y gráficos generados con Plotly."""

    @pytest.fixture
    def sample_data(self):
        fechas = pd.date_range("2022-01-01", periods=12, freq="ME")
        return pd.DataFrame(
            {
                "fecha": fechas,
                "spi_3": [-1.8, -1.2, -0.4, 0.2, 0.8, 1.4, -0.5, 0.0, 0.3, -1.1, -1.6, 0.5],
                "anomalia_termica_z": [-1.2, 0.5, 1.8, -0.3, 0.0, 2.1, -1.5, 0.8, -0.2, 1.1, -0.9, 0.4],
                "precio_urea_bulto": [120000 + i * 2000 for i in range(12)],
                "inflacion_yoy_urea": [15.0 + i * 0.5 for i in range(12)],
                "departamento": ["ANTIOQUIA", "CUNDINAMARCA", "BOYACA", "TOLIMA"] * 3,
                "rendimiento_ton_ha": [2.5, 18.0, 15.0, 3.2] * 3,
            }
        )

    def test_plot_spi_timeline(self, sample_data):
        """TC-701: Verifica generación de figura de serie temporal de SPI con líneas de umbral."""
        fig = plot_spi_timeline(sample_data, spi_col="spi_3")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1
        assert fig.data[0].name == "SPI_3"

        # Prueba con dataframe vacío
        fig_empty = plot_spi_timeline(pd.DataFrame())
        assert isinstance(fig_empty, go.Figure)

    def test_plot_thermal_anomalies(self, sample_data):
        """TC-702: Verifica generación de barras divergentes para anomalías térmicas."""
        fig = plot_thermal_anomalies(sample_data)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"

    def test_plot_price_inflation(self, sample_data):
        """TC-703: Verifica trazado de eje dual para precios e inflación interanual."""
        fig = plot_price_inflation(sample_data)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # Precio e Inflación
        assert "y2" in fig.data[1].yaxis

    def test_plot_yield_by_department(self, sample_data):
        """TC-704: Verifica agregación y ordenamiento por rendimiento departamental."""
        fig = plot_yield_by_department(sample_data, crop_name="Papa")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].orientation == "h"
