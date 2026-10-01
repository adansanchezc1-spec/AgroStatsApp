"""
Interfaz de Línea de Comandos (CLI) para Ingesta e Imputación de AgroStats
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: POSIX CLI, Argparse, PEP 8
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd
import numpy as np

from .config import DEFAULT_RAW_DIR, SAMPLE_BATCH_LIMIT
from .ingestion.dataset_registry import DATASET_REGISTRY
from .pipeline import AgroDataIngestionPipeline
from .imputation.imputation_engine import IntelligentImputer

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("imputer_cli")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AgroStats Automated Data Ingestion & Intelligent Imputer CLI"
    )
    parser.add_argument(
        "--download-all",
        action="store_true",
        help="Descargar e ingerir las 10 fuentes oficiales hacia data/RAW.",
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=list(DATASET_REGISTRY.keys()),
        help="Descargar una fuente individual específica.",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="Listar el catálogo maestro de fuentes disponibles.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=SAMPLE_BATCH_LIMIT,
        help=f"Límite de registros para consultas Socrata (default: {SAMPLE_BATCH_LIMIT}).",
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(DEFAULT_RAW_DIR),
        help="Ruta personalizada para data/RAW.",
    )
    parser.add_argument(
        "--impute-sample",
        action="store_true",
        help="Ejecuta una demostración de diagnóstico e imputación sobre datos con nulos.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Activar modo detallado de depuración (DEBUG).",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list_sources:
        print("\n=== CATÁLOGO MAESTRO DE FUENTES AGROPECUARIAS (DAMA-DMBOK 2) ===")
        for sid, meta in DATASET_REGISTRY.items():
            print(f"- ID: {sid:25} | Custodio: {meta.custodian:6} | Estrategia: {meta.extraction_type}")
            print(f"  Nombre: {meta.official_name}")
            print(f"  Granularidad: {meta.temporal_granularity} | {meta.spatial_granularity}")
            print(f"  Indicadores: {', '.join(meta.indicators)}")
            print("-" * 75)
        return 0

    if args.impute_sample:
        logger.info("Iniciando prueba del motor de imputación inteligente...")
        # Generar dataset de prueba representativo con clima y mercado
        np.random.seed(42)
        n = 100
        sample_data = {
            "fecha": pd.date_range("2026-01-01", periods=n, freq="D"),
            "cod_municipio": np.random.choice(["25001", "15001", "05001"], size=n),
            "precio_medio_kg": np.random.normal(3500, 400, size=n),
            "precipitacion_mm": np.random.exponential(12.0, size=n),
            "temp_media_c": np.random.normal(18.5, 3.0, size=n),
            "volumen_abasto_ton": np.random.lognormal(4.0, 0.5, size=n),
        }
        test_df = pd.DataFrame(sample_data)

        # Inyectar ausencias (15%)
        for col in ["precio_medio_kg", "precipitacion_mm", "temp_media_c"]:
            mask = np.random.random(size=n) < 0.15
            test_df.loc[mask, col] = np.nan

        imputer = IntelligentImputer()
        result = imputer.fit_impute(test_df, inject_audit_flags=True)

        print("\n=== REPORTE DE DIAGNÓSTICO DE AUSENCIAS (RUBIN) ===")
        print(f"Filas: {result.diagnostics.total_rows}, Columnas: {result.diagnostics.total_cols}")
        print(f"Mecanismo diagnosticado: {result.diagnostics.diagnosed_mechanism}")
        print(f"P-value proxy Little: {result.diagnostics.littles_test_p_value:.4f}")
        print(f"Estrategia sugerida: {result.diagnostics.recommended_strategy}")
        print("\n=== RESULTADOS DEL BENCHMARK COMPETITIVO ===")
        for algo, score in result.scores_by_algorithm.items():
            print(f"  - {algo:30}: Score = {score:.4f}")
        print(f"\nAlgoritmo ganador: {result.winning_algorithm_name} (Score: {result.winning_score:.4f})")
        print(f"Banderas de auditoría creadas: {result.audit_flags_injected}")
        print(f"Nulos remanentes en dataset imputado: {result.imputed_dataframe.isna().sum().to_dict()}")
        return 0

    if args.download_all:
        logger.info("Iniciando descarga automatizada de todas las 10 fuentes hacia %s", args.raw_dir)
        pipeline = AgroDataIngestionPipeline(raw_dir=Path(args.raw_dir))
        manifest = pipeline.ingest_all_sources(limit_per_socrata=args.limit)
        print("\n=== RESUMEN DE LA INGESTA AUTOMATIZADA ===")
        print(f"Fuentes intentadas: {manifest['sources_attempted']}")
        print(f"Fuentes exitosas:   {manifest['sources_successful']}")
        print(f"Fuentes con error:  {manifest['sources_failed']}")
        for d in manifest["datasets"]:
            print(f"  [OK] {d['dataset_id']:25} | Filas: {d['row_count']:5} | Archivos: {', '.join(d['files'])}")
        if manifest["errors"]:
            print("\nErrores registrados:")
            for sid, err in manifest["errors"].items():
                print(f"  [ERR] {sid:25} -> {err}")
        return 0

    if args.source:
        logger.info("Iniciando ingesta individual para: %s", args.source)
        pipeline = AgroDataIngestionPipeline(raw_dir=Path(args.raw_dir))
        entry = pipeline.ingest_dataset(dataset_id=args.source, limit=args.limit)
        print(f"\nIngesta exitosa para {args.source}:")
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
