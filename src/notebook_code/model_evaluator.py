"""
Evaluador de Modelos, Diagnóstico de Residuos y Servicio de Inferencia
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: SWEBOK, Explicabilidad de Modelos (Feature Importance), Validación de Residuos
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import max_error, mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluador integral de desempeño, bondad de ajuste, análisis de residuos
    y explicabilidad de variables para modelos predictivos agropecuarios.
    """

    @staticmethod
    def load_model(
        model_path: Union[str, Path],
    ) -> Tuple[Pipeline, Dict[str, Any]]:
        """Carga el pipeline serializado y su manifiesto de metadatos."""
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {model_path}")

        pipeline = joblib.load(model_path)

        meta_path = model_path.parent / f"{model_path.stem}_metadata.json"
        metadata = {}
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        return pipeline, metadata

    @staticmethod
    def evaluate_comprehensive_metrics(
        y_true: Union[pd.Series, np.ndarray],
        y_pred: Union[pd.Series, np.ndarray],
    ) -> Dict[str, float]:
        """
        Calcula un conjunto exhaustivo de métricas de precisión y sesgo:
        MAE, RMSE, MAPE, WAPE, R² y Máximo Error Absoluto.
        """
        y_t = np.asarray(y_true, dtype=float)
        y_p = np.asarray(y_pred, dtype=float)

        mae = float(mean_absolute_error(y_t, y_p))
        rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
        r2 = float(r2_score(y_t, y_p))
        max_err = float(max_error(y_t, y_p))

        # WAPE (Weighted Absolute Percentage Error) = sum(|y - y_hat|) / sum(y)
        sum_actual = float(np.sum(np.abs(y_t)))
        wape = float((np.sum(np.abs(y_t - y_p)) / sum_actual) * 100.0) if sum_actual > 0 else 0.0

        # MAPE
        non_zero_mask = y_t != 0
        mape = float(np.mean(np.abs((y_t[non_zero_mask] - y_p[non_zero_mask]) / y_t[non_zero_mask])) * 100.0) if np.any(non_zero_mask) else 0.0

        return {
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "MAPE_%": round(mape, 2),
            "WAPE_%": round(wape, 2),
            "R2_Score": round(r2, 4),
            "Max_Error": round(max_err, 4),
        }

    @staticmethod
    def residual_diagnostics(
        y_true: Union[pd.Series, np.ndarray],
        y_pred: Union[pd.Series, np.ndarray],
    ) -> Dict[str, float]:
        """
        Evalúa las propiedades estadísticas de los residuos (e = y - y_hat):
        media, desviación, asimetría y coeficiente Durbin-Watson aproximado.
        """
        y_t = np.asarray(y_true, dtype=float)
        y_p = np.asarray(y_pred, dtype=float)
        residuals = y_t - y_p

        # Estadístico Durbin-Watson (detecta autocorrelación en residuos)
        diff_res = np.diff(residuals)
        dw = float(np.sum(diff_res ** 2) / (np.sum(residuals ** 2) + 1e-8))

        skewness = float(pd.Series(residuals).skew()) if len(residuals) > 2 else 0.0
        kurt = float(pd.Series(residuals).kurtosis()) if len(residuals) > 3 else 0.0

        return {
            "Media_Residuos": round(float(np.mean(residuals)), 4),
            "Std_Residuos": round(float(np.std(residuals)), 4),
            "Asimetria_Residuos": round(skewness, 4),
            "Curtosis_Residuos": round(kurt, 4),
            "Durbin_Watson": round(dw, 4),
            "Diagnostico_DW": "Sin Autocorrelación Severa" if 1.5 <= dw <= 2.5 else "Posible Autocorrelación",
        }

    @staticmethod
    def plot_forecast_vs_actual(
        dates: pd.Series,
        y_true: Union[pd.Series, np.ndarray],
        y_pred: Union[pd.Series, np.ndarray],
        target_name: str = "Valor",
        figsize: Tuple[int, int] = (14, 6),
    ) -> Optional[plt.Figure]:
        """Genera visualización comparativa de serie observada vs pronosticada con panel de error."""
        y_t = np.asarray(y_true, dtype=float)
        y_p = np.asarray(y_pred, dtype=float)
        errors = np.abs(y_t - y_p)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True, gridspec_kw={"height_ratios": [3, 1]})

        ax1.plot(dates, y_t, label="Real (Observado)", color="#1565c0", linewidth=1.8, marker="o", markersize=3)
        ax1.plot(dates, y_p, label="Pronóstico Modelo", color="#e65100", linewidth=1.8, linestyle="--")
        ax1.set_title(f"Evaluación de Pronóstico: {target_name} (Real vs Predicho)", fontsize=13)
        ax1.set_ylabel(target_name)
        ax1.grid(True, linestyle="--", alpha=0.4)
        ax1.legend()

        ax2.bar(dates, errors, color="#d32f2f", alpha=0.5, label="Error Absoluto (|Real - Pred|)")
        ax2.set_ylabel("Error Abs")
        ax2.set_xlabel("Fecha / Tiempo")
        ax2.grid(True, linestyle="--", alpha=0.4)
        ax2.legend()

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_feature_importance(
        pipeline: Pipeline,
        feature_names: List[str],
        top_n: int = 15,
        figsize: Tuple[int, int] = (10, 6),
    ) -> Optional[plt.Figure]:
        """Extrae y grafica la importancia relativa de variables (MDI o coeficientes lineales)."""
        estimator = pipeline.named_steps.get("model")
        if not estimator:
            return None

        importances = None
        if hasattr(estimator, "feature_importances_"):
            importances = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            importances = np.abs(estimator.coef_)

        if importances is None or len(importances) != len(feature_names):
            return None

        imp_df = pd.DataFrame({
            "Variable": feature_names,
            "Importancia": importances,
        }).sort_values("Importancia", ascending=False).head(top_n)

        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(data=imp_df, x="Importancia", y="Variable", palette="viridis", ax=ax)
        ax.set_title(f"Top {top_n} Variables de Mayor Importancia Predictiva", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_residual_distribution(
        y_true: Union[pd.Series, np.ndarray],
        y_pred: Union[pd.Series, np.ndarray],
        figsize: Tuple[int, int] = (10, 4),
    ) -> Optional[plt.Figure]:
        """Grafica la distribución empírica de residuos frente a una normal ideal centrada en 0."""
        residuals = np.asarray(y_true) - np.asarray(y_pred)

        fig, ax = plt.subplots(figsize=figsize)
        sns.histplot(residuals, kde=True, color="#00897b", bins=25, ax=ax)
        ax.axvline(0, color="red", linestyle="--", linewidth=1.5, label="Residuo Cero (Ideal)")
        ax.set_title("Distribución de Frecuencia de los Residuos del Modelo", fontsize=12)
        ax.set_xlabel("Residuo (e = y - y_pred)")
        ax.set_ylabel("Frecuencia")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()
        return fig


class InferenceService:
    """
    Servicio de inferencia y scoring en tiempo real o en lotes (batch).
    Valida contratos de entrada y genera predicciones estructuradas con metadatos.
    """

    def __init__(self, model_path: Union[str, Path]) -> None:
        self.pipeline, self.metadata = ModelEvaluator.load_model(model_path)
        self.features: List[str] = self.metadata.get("features", [])

    def predict(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta la inferencia sobre nuevos registros.
        Valida que existan las características esperadas o las imputa con 0.
        """
        X = new_data.copy()

        # Completar features faltantes si se omitieron en el payload
        for f in self.features:
            if f not in X.columns:
                X[f] = 0.0

        X_aligned = X[self.features]
        predictions = self.pipeline.predict(X_aligned)

        output_df = new_data.copy()
        output_df["prediccion_modelo"] = np.round(predictions, 4)
        output_df["modelo_version"] = self.metadata.get("model_name", "v1.0")

        return output_df
