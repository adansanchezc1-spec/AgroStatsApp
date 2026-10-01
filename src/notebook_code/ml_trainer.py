"""
Entrenador de Modelos de Machine Learning y Validación Cruzada Temporal
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: SWEBOK, Scikit-Learn Pipelines, TimeSeriesSplit, Prevención de Data Leakage
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Orquestador de entrenamiento competitivo de modelos supervisados para series de tiempo
    agropecuarias (pronóstico de precios mayoristas, volúmenes de oferta y variables climáticas).
    """

    @staticmethod
    def prepare_train_test_split(
        df: pd.DataFrame,
        target_col: str,
        date_col: Optional[str] = None,
        test_size: float = 0.2,
        feature_cols: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """
        Realiza partición cronológica estricta respetando la flecha del tiempo
        para impedir fuga de datos del futuro (Lookahead Data Leakage).
        """
        clean_df = df.copy()

        if date_col and date_col in clean_df.columns:
            clean_df[date_col] = pd.to_datetime(clean_df[date_col], errors="coerce")
            clean_df = clean_df.dropna(subset=[date_col]).sort_values(date_col)
            dates = clean_df[date_col]
        else:
            dates = pd.Series(range(len(clean_df)))

        # Filtrar target válido
        clean_df = clean_df.dropna(subset=[target_col])
        dates = dates.loc[clean_df.index]

        # Seleccionar features numéricas o especificadas
        if feature_cols:
            selected_features = [c for c in feature_cols if c in clean_df.columns and c != target_col]
        else:
            selected_features = clean_df.select_dtypes(include=[np.number]).columns.tolist()
            if target_col in selected_features:
                selected_features.remove(target_col)

        X = clean_df[selected_features]
        y = clean_df[target_col]

        split_idx = int(len(X) * (1.0 - test_size))

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        train_dates, test_dates = dates.iloc[:split_idx], dates.iloc[split_idx:]

        return X_train, y_train, X_test, y_test, train_dates, test_dates

    @staticmethod
    def build_pipeline(
        model_type: str = "hist_gbr",
        scale_numeric: bool = True,
        random_state: int = 42,
    ) -> Pipeline:
        """
        Construye un Scikit-learn Pipeline robusto con imputación de mediana,
        escalamiento robusto ante atípicos y el estimador seleccionado.
        """
        steps = [
            ("imputer", SimpleImputer(strategy="median")),
        ]

        if scale_numeric:
            steps.append(("scaler", RobustScaler()))

        if model_type == "ridge":
            estimator = Ridge(alpha=1.0, random_state=random_state)
        elif model_type == "rf":
            estimator = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=random_state,
                n_jobs=-1,
            )
        elif model_type == "hist_gbr":
            estimator = HistGradientBoostingRegressor(
                max_iter=100,
                max_depth=8,
                random_state=random_state,
            )
        else:
            raise ValueError(f"Tipo de modelo no soportado: {model_type}")

        steps.append(("model", estimator))
        return Pipeline(steps)

    @classmethod
    def cross_validate_time_series(
        cls,
        pipeline: Pipeline,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 5,
    ) -> Dict[str, Any]:
        """
        Ejecuta validación cruzada temporal (TimeSeriesSplit) para evaluar
        estabilidad predictiva a lo largo de horizontes sucesivos.
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        rmse_scores = []
        mae_scores = []
        r2_scores = []

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

            pipeline.fit(X_tr, y_tr)
            preds = pipeline.predict(X_val)

            fold_rmse = float(np.sqrt(mean_squared_error(y_val, preds)))
            fold_mae = float(mean_absolute_error(y_val, preds))
            fold_r2 = float(r2_score(y_val, preds))

            rmse_scores.append(fold_rmse)
            mae_scores.append(fold_mae)
            r2_scores.append(fold_r2)

        return {
            "mean_rmse": float(np.mean(rmse_scores)),
            "std_rmse": float(np.std(rmse_scores)),
            "mean_mae": float(np.mean(mae_scores)),
            "mean_r2": float(np.mean(r2_scores)),
            "folds_rmse": rmse_scores,
        }

    @classmethod
    def train_competitive_tournament(
        cls,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        candidate_models: Tuple[str, ...] = ("ridge", "rf", "hist_gbr"),
    ) -> Tuple[Pipeline, pd.DataFrame, Dict[str, Pipeline]]:
        """
        Torneo competitivo entre múltiples familias algorítmicas
        (Lineal regularizado, Ensamble Bagging y Gradient Boosting).
        """
        results = []
        fitted_pipelines = {}

        for m_type in candidate_models:
            pipe = cls.build_pipeline(model_type=m_type)
            pipe.fit(X_train, y_train)

            train_preds = pipe.predict(X_train)
            test_preds = pipe.predict(X_test)

            train_rmse = np.sqrt(mean_squared_error(y_train, train_preds))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
            test_mae = mean_absolute_error(y_test, test_preds)
            test_r2 = r2_score(y_test, test_preds)

            results.append({
                "Modelo": m_type.upper(),
                "RMSE_Train": round(float(train_rmse), 4),
                "RMSE_Test": round(float(test_rmse), 4),
                "MAE_Test": round(float(test_mae), 4),
                "R2_Test": round(float(test_r2), 4),
                "Ratio_Overfit": round(float(test_rmse / (train_rmse + 1e-6)), 2),
            })
            fitted_pipelines[m_type] = pipe

        summary_df = pd.DataFrame(results).sort_values("RMSE_Test", ascending=True).reset_index(drop=True)
        winner_name = summary_df.iloc[0]["Modelo"].lower()
        winner_pipeline = fitted_pipelines[winner_name]

        summary_df["Seleccionado_Ganador"] = ["✓ Ganador" if i == 0 else "" for i in range(len(summary_df))]
        return winner_pipeline, summary_df, fitted_pipelines

    @staticmethod
    def save_trained_model(
        pipeline: Pipeline,
        feature_names: List[str],
        metrics: Dict[str, Any],
        output_dir: Optional[Path] = None,
        model_name: str = "best_agro_model",
    ) -> Tuple[str, str]:
        """
        Persiste el pipeline serializado en CRISPDM/data/MODEL/ con su manifiesto de metadatos.
        """
        if output_dir is None:
            output_dir = Path.cwd() / "CRISPDM" / "data" / "MODEL"
            if not output_dir.exists():
                output_dir = Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "MODEL"
            output_dir.mkdir(parents=True, exist_ok=True)

        model_file = output_dir / f"{model_name}.joblib"
        meta_file = output_dir / f"{model_name}_metadata.json"

        joblib.dump(pipeline, model_file)

        metadata = {
            "model_name": model_name,
            "estimator_class": str(pipeline.named_steps["model"].__class__.__name__),
            "features_count": len(feature_names),
            "features": feature_names,
            "metrics": metrics,
            "pipeline_steps": list(pipeline.named_steps.keys()),
        }

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info("Modelo persistido exitosamente en %s", model_file)
        return str(model_file), str(meta_file)
