"""Módulo de Visualización Analítica y Gráficos Interactivos (Plotly).
Fase PDCO: DEVELOPMENT | Estándar: Tufte Principles / SWEBOK v4 / Clean Code
Visualización de índices climáticos (SPI), anomalías térmicas, inflación y rendimientos agrícolas.
"""

from __future__ import annotations
from typing import Optional, List
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from src.utils.logger import get_logger

logger = get_logger("visualization.plots")


def plot_spi_timeline(
    df: pd.DataFrame,
    date_col: str = "fecha",
    spi_col: str = "spi_3",
    title: str = "Evolución Temporal del Índice de Precipitación Estandarizado (SPI)",
) -> go.Figure:
    """
    Genera gráfico interactivo de la serie de tiempo de SPI con bandas de sequía y humedad.
    """
    fig = go.Figure()

    if df.empty or spi_col not in df.columns:
        logger.warning("plot_spi_timeline invocado con DataFrame vacío o sin columna %s", spi_col)
        fig.update_layout(title=title)
        return fig

    # Línea principal de SPI
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[spi_col],
            mode="lines+markers",
            name=spi_col.upper(),
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=4),
        )
    )

    # Líneas de referencia WMO
    fig.add_hline(y=0.0, line_dash="solid", line_color="#7f7f7f", line_width=1)
    fig.add_hline(y=1.0, line_dash="dash", line_color="#2ca02c", annotation_text="Húmedo (+1.0)")
    fig.add_hline(y=-1.0, line_dash="dash", line_color="#ff7f0e", annotation_text="Sequía Moderada (-1.0)")
    fig.add_hline(y=-1.5, line_dash="dash", line_color="#d62728", annotation_text="Sequía Severa (-1.5)")

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title="Fecha",
        yaxis_title="Índice SPI (Desviaciones Estándar)",
        yaxis=dict(range=[-3.5, 3.5]),
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def plot_thermal_anomalies(
    df: pd.DataFrame,
    date_col: str = "fecha",
    anomaly_col: str = "anomalia_termica_z",
    title: str = "Anomalías Térmicas Climatológicas Estandarizadas (Z-Score)",
) -> go.Figure:
    """
    Genera gráfico de barras divergente para anomalías de temperatura.
    Valores positivos en rojo (calor anómalo) y negativos en azul (enfriamiento anómalo).
    """
    fig = go.Figure()

    if df.empty or anomaly_col not in df.columns:
        logger.warning("plot_thermal_anomalies invocado con DataFrame vacío o sin columna %s", anomaly_col)
        fig.update_layout(title=title)
        return fig

    colors = ["#d62728" if v >= 0 else "#1f77b4" for v in df[anomaly_col].fillna(0)]

    fig.add_trace(
        go.Bar(
            x=df[date_col],
            y=df[anomaly_col],
            marker_color=colors,
            name="Anomalía Z-Score",
        )
    )

    fig.add_hline(y=0.0, line_color="#333333", line_width=1.5)

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title="Fecha",
        yaxis_title="Anomalía Térmica (Z)",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def plot_price_inflation(
    df: pd.DataFrame,
    date_col: str = "fecha",
    price_col: str = "precio_urea_bulto",
    inflation_col: Optional[str] = "inflacion_yoy_urea",
    title: str = "Dinámica de Precios e Inflación Interanual (YoY)",
) -> go.Figure:
    """
    Genera gráfico con eje dual: precios nominales y tasa de inflación interanual.
    """
    fig = go.Figure()

    if df.empty or price_col not in df.columns:
        fig.update_layout(title=title)
        return fig

    # Eje Y1: Precio nominal
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[price_col],
            name=f"Precio ({price_col})",
            line=dict(color="#2ca02c", width=2.5),
            yaxis="y1",
        )
    )

    # Eje Y2: Inflación YoY
    if inflation_col and inflation_col in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[inflation_col],
                name="Inflación YoY (%)",
                line=dict(color="#d62728", width=2, dash="dot"),
                yaxis="y2",
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(title="Fecha"),
        yaxis=dict(title="Precio Nominal (COP)", side="left"),
        yaxis2=dict(
            title="Inflación YoY (%)",
            side="right",
            overlaying="y",
            showgrid=False,
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_yield_by_department(
    df: pd.DataFrame,
    dept_col: str = "departamento",
    yield_col: str = "rendimiento_ton_ha",
    crop_name: str = "Cultivo",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Genera gráfico de barras ordenado para comparar rendimientos agrícolas promedio por departamento.
    """
    fig = go.Figure()

    if df.empty or yield_col not in df.columns or dept_col not in df.columns:
        fig.update_layout(title=title or "Rendimiento Agrícola")
        return fig

    # Agrupar y ordenar por rendimiento promedio
    agg_df = (
        df.groupby(dept_col)[yield_col]
        .mean()
        .reset_index()
        .sort_values(by=yield_col, ascending=True)
    )

    fig.add_trace(
        go.Bar(
            x=agg_df[yield_col],
            y=agg_df[dept_col],
            orientation="h",
            marker=dict(color=agg_df[yield_col], colorscale="Viridis"),
            name="Rendimiento Promedio",
        )
    )

    chart_title = title or f"Rendimiento Promedio por Departamento: {crop_name} (Ton/Ha)"
    fig.update_layout(
        title=dict(text=chart_title, font=dict(size=16)),
        xaxis_title="Rendimiento (Ton/Ha)",
        yaxis_title="Departamento",
        template="plotly_white",
    )
    return fig
