"""
Visualización de Datos y Tableros Analíticos
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
"""

import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class AgroVisualizer:
    """Genera gráficos reproducibles leyendo únicamente de datasets procesados."""
    
    @staticmethod
    def plot_time_series(df: pd.DataFrame, x_col: str, y_col: str, title: str, output_path: str):
        plt.figure(figsize=(10, 5))
        plt.plot(df[x_col], df[y_col], marker='o', linestyle='-', color='#1b5e20')
        plt.title(title, fontsize=12, fontweight='bold')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=300)
        plt.close()
        logger.info(f"Gráfico guardado en: {path}")
