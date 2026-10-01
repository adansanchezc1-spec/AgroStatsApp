"""
Motor de Limpieza y Feature Engineering Agropecuario Multidominio
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: FAO-56 Irrigation and Drainage, SWEBOK, PEP 8, Time-Series Feature Store
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Ingeniería de variables agropecuarias y bioestadísticas.
    Genera rezagos temporales, ventanas móviles de volatilidad, balances hídricos FAO-56,
    codificaciones cíclicas de estacionalidad e integración de matrices para Machine Learning.
    """

    @staticmethod
    def clean_dataset(
        df: pd.DataFrame,
        date_col: Optional[str] = None,
        numeric_cols: Optional[List[str]] = None,
        clip_negative_cols: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Limpia y estandariza tipos de datos, parsea fechas ISO y restringe dominios biofísicos.
        """
        clean_df = df.copy()

        # 1. Parseo de fecha
        if date_col and date_col in clean_df.columns:
            clean_df[date_col] = pd.to_datetime(clean_df[date_col], errors="coerce")
            clean_df = clean_df.dropna(subset=[date_col]).sort_values(date_col)

        # 2. Conversión de columnas numéricas
        if numeric_cols:
            for col in numeric_cols:
                if col in clean_df.columns:
                    if clean_df[col].dtype == object:
                        clean_df[col] = (
                            clean_df[col]
                            .astype(str)
                            .str.replace("$", "", regex=False)
                            .str.replace(".", "", regex=False)  # Miles
                            .str.replace(",", ".", regex=False)  # Decimales
                            .str.strip()
                        )
                    clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")

        # 3. Truncamiento de valores negativos inadmisibles (precipitación, radiación, precios)
        if clip_negative_cols:
            for col in clip_negative_cols:
                if col in clean_df.columns:
                    clean_df[col] = clean_df[col].clip(lower=0.0)

        return clean_df.reset_index(drop=True)

    @staticmethod
    def create_lag_features(
        df: pd.DataFrame,
        target_cols: List[str],
        lags: List[int] = (1, 2, 7, 30),
        group_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Genera variables de rezago temporal (lags) para modelos autorregresivos.
        """
        result_df = df.copy()
        for col in target_cols:
            if col not in result_df.columns:
                continue

            for lag in lags:
                col_name = f"{col}_lag_{lag}"
                if group_col and group_col in result_df.columns:
                    result_df[col_name] = result_df.groupby(group_col)[col].shift(lag)
                else:
                    result_df[col_name] = result_df[col].shift(lag)

        return result_df

    @staticmethod
    def create_rolling_features(
        df: pd.DataFrame,
        target_cols: List[str],
        windows: List[int] = (7, 14, 30),
        group_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Genera estadísticas sobre ventanas móviles (media móvil, volatilidad y extremos).
        """
        result_df = df.copy()
        for col in target_cols:
            if col not in result_df.columns:
                continue

            for w in windows:
                mean_col = f"{col}_rolling_mean_{w}"
                std_col = f"{col}_rolling_std_{w}"

                if group_col and group_col in result_df.columns:
                    grouped = result_df.groupby(group_col)[col]
                    result_df[mean_col] = grouped.transform(lambda s: s.rolling(w, min_periods=1).mean())
                    result_df[std_col] = grouped.transform(lambda s: s.rolling(w, min_periods=1).std()).fillna(0)
                else:
                    result_df[mean_col] = result_df[col].rolling(w, min_periods=1).mean()
                    result_df[std_col] = result_df[col].rolling(w, min_periods=1).std().fillna(0)

        return result_df

    @staticmethod
    def create_fao_agroclimate_features(
        df: pd.DataFrame,
        precip_col: str,
        evap_col: str,
        temp_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calcula indicadores biofísicos de balance hídrico basados en FAO-56:
        - Balance Hídrico Neto = Precipitación - Evapotranspiración (P - ETP)
        - Déficit de Riego Acumulado = max(0, ETP - P)
        - Índice de Humedad Arv = P / (ETP + 1e-5)
        """
        result_df = df.copy()

        has_precip = precip_col in result_df.columns
        has_evap = evap_col in result_df.columns

        if has_precip and has_evap:
            p = result_df[precip_col].fillna(0.0)
            etp = result_df[evap_col].fillna(0.0)

            result_df["balance_hidrico_neto_fao"] = p - etp
            result_df["deficit_hidrico_riego_fao"] = (etp - p).clip(lower=0.0)
            result_df["indice_humedad_arv"] = p / (etp + 1e-3)

        if temp_col and temp_col in result_df.columns:
            temp = result_df[temp_col]
            result_df["grados_dia_desarrollo"] = (temp - 10.0).clip(lower=0.0)

        return result_df

    @staticmethod
    def create_cyclical_calendar_features(
        df: pd.DataFrame,
        date_col: str,
    ) -> pd.DataFrame:
        """
        Aplica transformaciones seno y coseno para capturar la periodicidad
        anual y semanal sin discontinuidades artificiales.
        """
        result_df = df.copy()
        if date_col not in result_df.columns:
            return result_df

        dt = pd.to_datetime(result_df[date_col], errors="coerce")

        # Mes del año (1 a 12)
        month = dt.dt.month.fillna(1)
        result_df["sin_mes"] = np.sin(2 * np.pi * month / 12.0)
        result_df["cos_mes"] = np.cos(2 * np.pi * month / 12.0)

        # Día del año (1 a 365)
        doy = dt.dt.dayofyear.fillna(1)
        result_df["sin_dia_ano"] = np.sin(2 * np.pi * doy / 365.25)
        result_df["cos_dia_ano"] = np.cos(2 * np.pi * doy / 365.25)

        # Día de la semana (0 a 6)
        dow = dt.dt.dayofweek.fillna(0)
        result_df["sin_dia_semana"] = np.sin(2 * np.pi * dow / 7.0)
        result_df["cos_dia_semana"] = np.cos(2 * np.pi * dow / 7.0)

        return result_df

    @staticmethod
    def integrate_feature_matrix(
        primary_df: pd.DataFrame,
        secondary_dfs: List[Tuple[pd.DataFrame, str]],
        how: str = "left",
    ) -> pd.DataFrame:
        """
        Fusiona múltiples fuentes agregadas sobre una clave común (ej. llave geo-temporal o fecha).
        """
        master = primary_df.copy()
        for df_sec, key in secondary_dfs:
            if key in master.columns and key in df_sec.columns:
                # Evitar columnas duplicadas
                cols_to_use = [c for c in df_sec.columns if c == key or c not in master.columns]
                master = master.merge(df_sec[cols_to_use], on=key, how=how)

        return master

    @staticmethod
    def save_feature_matrix(
        df: pd.DataFrame,
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Persiste la matriz de características integrada en CRISPDM/data/FEATURES/.
        """
        if output_file is None:
            output_dir = Path.cwd() / "CRISPDM" / "data" / "FEATURES"
            if not output_dir.exists():
                output_dir = Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "FEATURES"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "master_feature_matrix.csv"

        df.to_csv(output_file, index=False, encoding="utf-8")
        logger.info("Matriz de características guardada: %s (%d filas x %d cols)", output_file, len(df), len(df.columns))
        return str(output_file)
