"""
Gestor de Datos Maestros (MDM) y Resolución de Entidades Agropecuarias
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Reference and Master Data), DANE DIVIPOLA, CPC Ver. 2.1 A.C.
"""

import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Catálogo Canónico DANE DIVIPOLA (Departamentos Oficiales de Colombia)
DIVIPOLA_DEPARTAMENTOS: Dict[str, str] = {
    "ANTIOQUIA": "05",
    "ATLANTICO": "08",
    "BOGOTA D.C.": "11",
    "BOGOTA": "11",
    "BOLIVAR": "13",
    "BOYACA": "15",
    "CALDAS": "17",
    "CAQUETA": "18",
    "CAUCA": "19",
    "CESAR": "20",
    "CORDOBA": "23",
    "CUNDINAMARCA": "25",
    "CHOCO": "27",
    "HUILA": "41",
    "LA GUAJIRA": "44",
    "GUAJIRA": "44",
    "MAGDALENA": "47",
    "META": "50",
    "NARINO": "52",
    "NORTE DE SANTANDER": "54",
    "QUINDIO": "63",
    "RISARALDA": "66",
    "SANTANDER": "68",
    "SUCRE": "70",
    "TOLIMA": "73",
    "VALLE DEL CAUCA": "76",
    "VALLE": "76",
    "ARAUCA": "81",
    "CASANARE": "85",
    "PUTUMAYO": "86",
    "SAN ANDRES": "88",
    "AMAZONAS": "91",
    "GUAINIA": "94",
    "GUAVIARE": "95",
    "VAUPES": "97",
    "VICHADA": "99",
}

# Catálogo Canónico CPC Ver. 2.1 A.C. para Principales Productos Agropecuarios
CPC_AGRO_PRODUCTS: Dict[str, Dict[str, str]] = {
    "PAPA": {"cpc_code": "01510", "cpc_name": "Papas", "grupo": "Tubérculos"},
    "CEBOLLA": {"cpc_code": "01252", "cpc_name": "Cebollas y ajos", "grupo": "Hortalizas"},
    "TOMATE": {"cpc_code": "01234", "cpc_name": "Tomates", "grupo": "Hortalizas"},
    "PLATANO": {"cpc_code": "01314", "cpc_name": "Plátanos", "grupo": "Frutas"},
    "BANANO": {"cpc_code": "01312", "cpc_name": "Bananos", "grupo": "Frutas"},
    "ZANAHORIA": {"cpc_code": "01251", "cpc_name": "Zanahorias y nabos", "grupo": "Hortalizas"},
    "ARROZ": {"cpc_code": "01131", "cpc_name": "Arroz con cáscara", "grupo": "Cereales"},
    "MAIZ": {"cpc_code": "01121", "cpc_name": "Maíz grano", "grupo": "Cereales"},
    "CAFE": {"cpc_code": "01610", "cpc_name": "Café en grano verde", "grupo": "Estimulantes"},
    "AGUACATE": {"cpc_code": "01344", "cpc_name": "Aguacates", "grupo": "Frutas"},
    "CITRICOS": {"cpc_code": "01322", "cpc_name": "Cítricos", "grupo": "Frutas"},
    "NARANJA": {"cpc_code": "01322", "cpc_name": "Cítricos (Naranjas)", "grupo": "Frutas"},
    "LIMON": {"cpc_code": "01322", "cpc_name": "Cítricos (Limones)", "grupo": "Frutas"},
    "LECHUGA": {"cpc_code": "01241", "cpc_name": "Lechugas y achicorias", "grupo": "Hortalizas"},
    "YUCA": {"cpc_code": "01520", "cpc_name": "Yuca (mandioca)", "grupo": "Tubérculos"},
    "FRUVER": {"cpc_code": "01000", "cpc_name": "Productos agrícolas mixtos", "grupo": "General"},
}


class MasterDataManager:
    """
    Controlador de Gobierno y Armonización de Entidades Maestras (MDM).
    Asegura unicidad semántica, asignación de identificadores canónicos (DIVIPOLA, CPC)
    y generación de llaves compuestas de integración cross-domain.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """Limpia caracteres diacríticos (tildes), espacios y normaliza a mayúsculas."""
        if not isinstance(text, str):
            return ""
        text = text.strip().upper()
        # Eliminar tildes
        text = "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )
        # Limpiar caracteres especiales
        text = re.sub(r"[^A-Z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def harmonize_divipola(
        cls,
        df: pd.DataFrame,
        dept_col: str,
        output_col_name: str = "cod_dpto_divipola",
    ) -> pd.DataFrame:
        """
        Asigna el código DANE DIVIPOLA a cada registro según su departamento normalizado.
        """
        if dept_col not in df.columns:
            return df

        result_df = df.copy()
        clean_dept_series = result_df[dept_col].astype(str).apply(cls.normalize_text)

        codes = []
        for d in clean_dept_series:
            code = DIVIPOLA_DEPARTAMENTOS.get(d)
            if not code:
                # Búsqueda parcial si hay prefijos o variaciones
                for k, v in DIVIPOLA_DEPARTAMENTOS.items():
                    if k in d or d in k:
                        code = v
                        break
            codes.append(code if code else "99")

        result_df[output_col_name] = codes
        result_df["depto_normalizado"] = clean_dept_series
        return result_df

    @classmethod
    def harmonize_cpc_products(
        cls,
        df: pd.DataFrame,
        product_col: str,
    ) -> pd.DataFrame:
        """
        Clasifica productos agropecuarios hacia la codificación internacional CPC.
        """
        if product_col not in df.columns:
            return df

        result_df = df.copy()
        clean_prod_series = result_df[product_col].astype(str).apply(cls.normalize_text)

        cpc_codes = []
        cpc_names = []
        cpc_groups = []

        for p in clean_prod_series:
            matched = False
            for k, meta in CPC_AGRO_PRODUCTS.items():
                if k in p:
                    cpc_codes.append(meta["cpc_code"])
                    cpc_names.append(meta["cpc_name"])
                    cpc_groups.append(meta["grupo"])
                    matched = True
                    break
            if not matched:
                cpc_codes.append("01999")
                cpc_names.append("Otros productos agrícolas")
                cpc_groups.append("Otros")

        result_df["cpc_code"] = cpc_codes
        result_df["cpc_nombre"] = cpc_names
        result_df["cpc_grupo"] = cpc_groups
        result_df["producto_normalizado"] = clean_prod_series
        return result_df

    @classmethod
    def extract_ideam_stations_catalog(cls, df_ideam: pd.DataFrame) -> pd.DataFrame:
        """
        Construye el catálogo maestro canónico de estaciones meteorológicas del IDEAM.
        """
        col_map = {
            "codigoestacion": "codigo_estacion",
            "nombreestacion": "nombre_estacion",
            "departamento": "departamento",
            "municipio": "municipio",
            "latitud": "latitud",
            "longitud": "longitud",
            "altitud": "altitud",
            "categoria": "categoria",
        }

        # Renombrar columnas encontradas
        df = df_ideam.copy()
        df.columns = [cls.normalize_text(c).lower().replace(" ", "") for c in df.columns]

        found_cols = [c for c in col_map.keys() if c in df.columns]
        if not found_cols:
            return pd.DataFrame()

        stations = df[found_cols].drop_duplicates().rename(columns=col_map)
        if "departamento" in stations.columns:
            stations = cls.harmonize_divipola(stations, "departamento")

        return stations.reset_index(drop=True)

    @classmethod
    def extract_sipsa_markets_catalog(cls, df_sipsa: pd.DataFrame) -> pd.DataFrame:
        """
        Construye el catálogo maestro canónico de plazas mayoristas y centros de abastecimiento SIPSA.
        """
        df = df_sipsa.copy()
        df.columns = [cls.normalize_text(c).lower().replace(" ", "_") for c in df.columns]

        market_col = None
        for c in ["mercado", "fuente", "plaza", "ciudad"]:
            candidates = [col for col in df.columns if c in col]
            if candidates:
                market_col = candidates[0]
                break

        if not market_col:
            return pd.DataFrame()

        dept_col = next((c for c in df.columns if "depto" in c or "departamento" in c), None)

        subset_cols = [market_col]
        if dept_col:
            subset_cols.append(dept_col)

        markets = df[subset_cols].drop_duplicates().rename(columns={market_col: "nombre_mercado"})
        if dept_col:
            markets = cls.harmonize_divipola(markets, dept_col)

        markets["id_mercado"] = [f"MKT_{i+1:03d}" for i in range(len(markets))]
        return markets.reset_index(drop=True)

    @classmethod
    def build_cross_domain_surrogate_key(
        cls,
        df: pd.DataFrame,
        date_col: str,
        dept_col: str,
        key_name: str = "surrogate_key_geo_temporal",
    ) -> pd.DataFrame:
        """
        Genera una clave surrogada unificada (COD_DPTO_AÑO_MES) para permitir
        la integración relacional entre series climáticas de IDEAM y precios DANE.
        """
        result_df = df.copy()
        if date_col not in result_df.columns:
            return result_df

        # Asegurar columna DIVIPOLA
        if "cod_dpto_divipola" not in result_df.columns and dept_col in result_df.columns:
            result_df = cls.harmonize_divipola(result_df, dept_col)

        dt_series = pd.to_datetime(result_df[date_col], errors="coerce")
        years = dt_series.dt.year.fillna(9999).astype(int).astype(str)
        months = dt_series.dt.month.fillna(99).astype(int).apply(lambda m: f"{m:02d}")

        divipola = result_df.get("cod_dpto_divipola", pd.Series(["99"] * len(result_df)))
        result_df[key_name] = divipola.astype(str) + "_" + years + "_" + months
        return result_df

    @staticmethod
    def save_mdm_catalogs(
        catalogs: Dict[str, pd.DataFrame],
        output_dir: Optional[Path] = None,
    ) -> Dict[str, str]:
        """
        Persiste los catálogos maestros canónicos en formato CSV y JSON en CRISPDM/data/MDM/.
        """
        if output_dir is None:
            output_dir = Path.cwd() / "CRISPDM" / "data" / "MDM"
            if not output_dir.exists():
                output_dir = Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "MDM"

        output_dir.mkdir(parents=True, exist_ok=True)
        persisted_paths = {}

        for name, cdf in catalogs.items():
            if cdf.empty:
                continue
            csv_path = output_dir / f"mdm_{name}.csv"
            json_path = output_dir / f"mdm_{name}.json"

            cdf.to_csv(csv_path, index=False, encoding="utf-8")
            cdf.to_json(json_path, orient="records", indent=2, force_ascii=False)
            persisted_paths[name] = str(csv_path)
            logger.info("Catálogo maestro guardado: %s (%d registros)", name, len(cdf))

        return persisted_paths
