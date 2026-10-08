"""Pruebas Unitarias para el Motor de Indicadores Agroclimáticos y de Mercado (Capa Gold).
Fase PDCO: CONTROL | Estándar: ISO/IEC 25010 / Clean Code
Casos de prueba: TC-501 a TC-506.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.indicators.climate_indices import calculate_spi, calculate_thermal_anomaly
from src.indicators.market_indices import (
    calculate_yoy_inflation,
    calculate_terms_of_trade,
    calculate_price_index,
)
from src.indicators.temporal_features import add_lag_features, add_rolling_features
from src.indicators.indicator_store import IndicatorStore


class TestClimateIndices:
    """TC-501 & TC-502: Pruebas unitarias para cálculo de SPI y Anomalías Térmicas."""

    def test_calculate_spi_synthetic_series(self):
        """Verifica que el cálculo de SPI retorne valores numéricos acotados en escala representativa."""
        np.random.seed(42)
        # Generar 36 meses de lluvia sintética siguiendo distribución gamma
        precip_vals = np.random.gamma(shape=2.0, scale=40.0, size=36)
        # Añadir algunos ceros para probar probabilidad de sequía q
        precip_vals[5] = 0.0
        precip_vals[15] = 0.0
        series = pd.Series(precip_vals)

        spi_3 = calculate_spi(series, scale=3, min_periods=12)

        # Los primeros 2 valores son NaN por la ventana móvil de 3 meses
        assert pd.isna(spi_3.iloc[0])
        assert pd.isna(spi_3.iloc[1])
        # A partir del índice 2, debe haber valores válidos acotados [-3.5, 3.5]
        valid_spi = spi_3.dropna()
        assert len(valid_spi) > 0
        assert (valid_spi >= -3.5).all()
        assert (valid_spi <= 3.5).all()

    def test_calculate_spi_insufficient_samples(self):
        """Garantiza que una serie con menos muestras que min_periods retorne NaNs sin excepción."""
        series_short = pd.Series([10.0, 20.0, 15.0])
        res = calculate_spi(series_short, scale=3, min_periods=12)
        assert res.isna().all()

    def test_calculate_thermal_anomaly(self):
        """Verifica la anomalía Z-score agrupada por mes."""
        fechas = pd.date_range(start="2020-01-01", periods=24, freq="ME")
        # Serie donde enero tiene media 20 y varianza
        temps = [20.0 if d.month == 1 else 25.0 for d in fechas]
        temps[0] = 22.0  # Anomaly positiva en el primer enero
        temps[12] = 18.0  # Anomaly negativa en el segundo enero

        s_temp = pd.Series(temps)
        s_dates = pd.Series(fechas)

        anomalies = calculate_thermal_anomaly(s_temp, s_dates)
        assert len(anomalies) == 24
        # Enero 2020 debe tener z-score positivo y Enero 2021 z-score negativo
        assert anomalies.iloc[0] > 0
        assert anomalies.iloc[12] < 0


class TestMarketIndices:
    """TC-503 & TC-504: Pruebas unitarias para indicadores económicos y de mercado."""

    def test_calculate_yoy_inflation(self):
        """Verifica cálculo de variación interanual con lag=12."""
        # 12 meses a 100, y el mes 13 a 120 (inflación del 20%)
        prices = [100.0] * 12 + [120.0]
        s_price = pd.Series(prices)

        yoy = calculate_yoy_inflation(s_price, lag_periods=12)
        assert len(yoy) == 13
        assert pd.isna(yoy.iloc[0])
        assert pytest.approx(yoy.iloc[12], 0.01) == 20.0

    def test_calculate_terms_of_trade(self):
        """Verifica el ratio insumo/producto y manejo de división por cero."""
        p_insumo = pd.Series([1000.0, 2000.0, 3000.0])
        p_producto = pd.Series([500.0, 0.0, 1500.0])

        tot = calculate_terms_of_trade(p_insumo, p_producto)
        assert tot.iloc[0] == 2.0
        assert pd.isna(tot.iloc[1])  # Denominador cero produce NaN seguro
        assert tot.iloc[2] == 2.0

    def test_calculate_price_index(self):
        """Verifica normalización a base 100."""
        prices = pd.Series([50.0, 100.0, 75.0])
        idx = calculate_price_index(prices, base_idx=0)
        assert idx.iloc[0] == 100.0
        assert idx.iloc[1] == 200.0
        assert idx.iloc[2] == 150.0


class TestTemporalFeatures:
    """TC-505: Pruebas unitarias para rezagos (lags) y medias móviles sin lookahead bias."""

    def test_add_lag_features_grouped(self):
        """Verifica causalidad estricta en lags agrupados por municipio."""
        df = pd.DataFrame(
            {
                "cod_municipio": ["05001", "05001", "05001", "11001", "11001"],
                "periodo": [1, 2, 3, 1, 2],
                "rendimiento": [2.0, 2.5, 3.0, 1.0, 1.2],
            }
        )
        df_lagged = add_lag_features(df, target_col="rendimiento", lags=[1], group_col="cod_municipio", order_by="periodo")

        assert "rendimiento_lag_1" in df_lagged.columns
        # Primer registro de cada grupo no tiene historia previa
        assert pd.isna(df_lagged.loc[df_lagged["periodo"] == 1, "rendimiento_lag_1"]).all()
        # Segundo registro de 05001 debe tener 2.0
        val = df_lagged[(df_lagged["cod_municipio"] == "05001") & (df_lagged["periodo"] == 2)]["rendimiento_lag_1"].iloc[0]
        assert val == 2.0

    def test_add_rolling_features_no_lookahead_bias(self):
        """Verifica que el valor actual t no esté incluido en la media móvil de t."""
        df = pd.DataFrame(
            {
                "tiempo": [1, 2, 3, 4],
                "precio": [10.0, 20.0, 30.0, 100.0],
            }
        )
        df_roll = add_rolling_features(df, target_col="precio", windows=[2], order_by="tiempo")

        # En t=3 (precio=30), la media de ventana 2 debe ser sobre t=1 (10) y t=2 (20), es decir (10+20)/2 = 15.0
        # No debe incluir 30.0!
        assert df_roll["precio_roll_mean_2"].iloc[2] == 15.0


class TestIndicatorStore:
    """TC-506: Pruebas unitarias para persistencia y consolidación en IndicatorStore."""

    @pytest.fixture
    def store(self, tmp_path: Path):
        return IndicatorStore(indicators_dir=tmp_path)

    def test_save_and_load_indicator_dataset(self, store):
        """Verifica guardado en Parquet, cálculo de SHA-256 y lectura posterior."""
        df_indicators = pd.DataFrame(
            {
                "anio": [2022, 2022],
                "mes": [1, 2],
                "cod_municipio": ["05001", "05001"],
                "spi_3": [-0.5, 1.2],
                "inflacion_yoy": [12.5, 14.1],
            }
        )
        meta = store.save_indicator_dataset(df_indicators, "test_gold_indicators")

        assert meta["rows"] == 2
        assert len(meta["sha256"]) == 64
        assert Path(meta["target_path"]).exists()

        loaded_df = store.load_indicator_dataset("test_gold_indicators")
        assert len(loaded_df) == 2
        assert "spi_3" in loaded_df.columns

    def test_consolidate_features(self, store):
        """Verifica unión horizontal segura de múltiples datasets de indicadores."""
        df_base = pd.DataFrame({"anio": [2022], "mes": [1], "cod_mun": ["05001"], "prod": [100]})
        df_clima = pd.DataFrame({"anio": [2022], "mes": [1], "cod_mun": ["05001"], "spi_3": [0.8]})
        df_precios = pd.DataFrame({"anio": [2022], "mes": [1], "cod_mun": ["05001"], "tot": [1.5]})

        consolidated = store.consolidate_features(
            df_base=df_base,
            df_indicators=[df_clima, df_precios],
            join_keys=["anio", "mes", "cod_mun"],
        )

        assert len(consolidated) == 1
        assert "spi_3" in consolidated.columns
        assert "tot" in consolidated.columns
