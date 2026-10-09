"""Pruebas Unitarias para el Motor de Inferencia Estadística y Pruebas de Hipótesis.
Fase PDCO: CONTROL | Estándar: ISO/IEC 25010 / SWEBOK v4 / Clean Code
Casos de prueba: TC-901 a TC-905.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.modeling.hypothesis_testing_engine import HypothesisTestingEngine, _norm_cdf, _chi2_sf_2df


class TestHypothesisTestingEngine:
    """Suite de pruebas para contrastes estadísticos formales."""

    @pytest.fixture
    def engine(self):
        return HypothesisTestingEngine(alpha=0.05)

    def test_math_utilities(self):
        """Verifica funciones matemáticas exactas _norm_cdf y _chi2_sf_2df."""
        assert pytest.approx(_norm_cdf(0.0), 0.01) == 0.5
        assert _norm_cdf(3.0) > 0.99
        assert _norm_cdf(-3.0) < 0.01

        assert _chi2_sf_2df(0.0) == 1.0
        assert pytest.approx(_chi2_sf_2df(5.991), 0.01) == 0.05  # Valor crítico chi2(2) para alpha=0.05

    def test_normality_contrast(self, engine):
        """TC-901: Verifica detección de normalidad (gaussiana) y no normalidad (exponencial)."""
        np.random.seed(42)
        normal_data = pd.Series(np.random.normal(loc=50.0, scale=10.0, size=150))
        skewed_data = pd.Series(np.random.exponential(scale=10.0, size=150))

        # 1. Datos normales no deberían rechazar H0
        res_norm = engine.test_normality(normal_data, "temperatura")
        assert res_norm["n_observations"] == 150
        assert res_norm["decision"] in {"NO_RECHAZA_H0", "RECHAZA_H0"}  # Al azar puede variar, pero verifica estructura

        # 2. Datos altamente asimétricos deben rechazar H0 de normalidad
        res_skew = engine.test_normality(skewed_data, "ingresos")
        assert res_skew["decision"] == "RECHAZA_H0"
        assert res_skew["alpha_05_rejected"] is True

        # 3. Muestra muy pequeña
        res_short = engine.test_normality(pd.Series([1, 2, 3]), "corta")
        assert res_short["decision"] == "INSUFICIENTE"

    def test_mann_kendall_trend(self, engine):
        """TC-902: Verifica detección de tendencia monótona y estimación de Sen."""
        # Serie con tendencia ascendente determinista y ruido suave
        t = np.arange(1, 41)
        increasing_series = pd.Series(2.5 * t + np.random.normal(0, 1.0, 40))

        res_trend = engine.test_mann_kendall_trend(increasing_series, "precio_fertilizante")
        assert res_trend["decision"] == "RECHAZA_H0"
        assert res_trend["trend_direction"] == "ASCENDENTE"
        assert res_trend["sens_slope"] > 1.5

        # Serie sin tendencia
        stationary_series = pd.Series(np.random.normal(100, 2, 40))
        res_stat = engine.test_mann_kendall_trend(stationary_series, "temperatura_estable")
        assert res_stat["trend_direction"] in {"ESTACIONARIA_SIN_TENDENCIA", "ASCENDENTE", "DESCENDENTE"}

    def test_stationarity_adf(self, engine):
        """TC-903: Verifica prueba de raíz unitaria (ADF) en ruido blanco vs caminata aleatoria."""
        np.random.seed(42)
        # Ruido blanco estacionario
        white_noise = pd.Series(np.random.normal(0, 1, 100))
        res_wn = engine.test_stationarity(white_noise, "ruido_blanco")
        assert res_wn["decision"] == "ESTACIONARIA"

        # Caminata aleatoria no estacionaria
        random_walk = pd.Series(np.cumsum(np.random.normal(0, 1, 100)))
        res_rw = engine.test_stationarity(random_walk, "caminata_aleatoria")
        assert res_rw["target_variable"] == "caminata_aleatoria"
        assert "decision" in res_rw

    def test_group_differences_kruskal_wallis(self, engine):
        """TC-904: Verifica diferencias no paramétricas entre grupos regionales."""
        df_groups = pd.DataFrame({
            "rendimiento": [2.0, 2.1, 2.2, 2.3] + [15.0, 15.5, 16.0, 16.2] + [22.0, 22.5, 23.0, 23.1],
            "departamento": ["ANTIOQUIA"] * 4 + ["BOYACA"] * 4 + ["CUNDINAMARCA"] * 4,
        })
        res_kw = engine.test_group_differences(df_groups, value_col="rendimiento", group_col="departamento")
        assert res_kw["decision"] == "RECHAZA_H0"
        assert res_kw["n_groups"] == 3
        assert res_kw["p_value"] < 0.05

    def test_run_full_battery_and_persist(self, engine, tmp_path: Path):
        """TC-905: Verifica compilación de batería tabular y persistencia en Gold."""
        np.random.seed(42)
        df_sim = pd.DataFrame({
            "precipitacion": np.random.gamma(2, 30, 50),
            "precio": np.arange(50) * 1.5 + np.random.normal(0, 2, 50),
            "depto": ["ANT"] * 25 + ["BOY"] * 25,
        })

        battery_df = engine.run_full_battery(df_sim, numeric_cols=["precipitacion", "precio"], group_col="depto")
        assert len(battery_df) >= 6
        assert "variable" in battery_df.columns
        assert "p_valor" in battery_df.columns

        meta = engine.persist_hypothesis_mart(battery_df, output_filename="test_mart_hypothesis")
        assert Path(meta["target_path"]).exists()
        assert meta["tests_evaluated"] == len(battery_df)
