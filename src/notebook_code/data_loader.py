"""
Cargador Inteligente de Datasets Agropecuarios para Notebooks
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2, SWEBOK, PEP 8, Pandas I/O
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd

logger = logging.getLogger(__name__)


def find_raw_data_dir() -> Path:
    """
    Localiza de forma resiliente el directorio data/RAW buscando en jerarquías relativas
    desde la carpeta actual de ejecución, notebooks o src.
    """
    candidate_paths = [
        # Desde notebooks/ (CRISPDM/notebooks/ -> CRISPDM/data/RAW)
        Path.cwd().parent / "data" / "RAW",
        # Desde la raíz del proyecto AgroStatsApp/
        Path.cwd() / "CRISPDM" / "data" / "RAW",
        Path.cwd() / "data" / "RAW",
        # Relativo a este archivo fuente (src/notebook_code/ -> CRISPDM/data/RAW)
        Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "RAW",
        Path(__file__).resolve().parent.parent.parent / "data" / "RAW",
    ]

    for p in candidate_paths:
        if p.exists() and p.is_dir():
            return p.resolve()

    # Si no existe, crear la ruta canónica en CRISPDM/data/RAW
    default_dir = Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "RAW"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir.resolve()


class RawDataLoader:
    """
    Lector y estandarizador de conjuntos de datos crudos (CSV, JSON, XLSX)
    almacenados en data/RAW para su uso en notebooks de investigación.
    """

    def __init__(self, raw_dir: Optional[Union[str, Path]] = None) -> None:
        self.raw_dir = Path(raw_dir) if raw_dir else find_raw_data_dir()
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Carga el manifiesto de auditoría SHA-256 generado durante la ingesta."""
        manifest_file = self.raw_dir / "raw_manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("No se pudo parsear raw_manifest.json: %s", e)
        return {}

    def list_available_datasets(self) -> List[str]:
        """Lista los IDs de datasets encontrados en data/RAW."""
        files = list(self.raw_dir.glob("*.*"))
        dataset_ids = set()
        for f in files:
            if f.name == "raw_manifest.json" or f.name.startswith("temp_") or f.suffix.lower() in [".md", ".txt", ".gitignore"]:
                continue
            # El nombre típicamente sigue el patrón {dataset_id}_{timestamp}.ext
            parts = f.stem.split("_")
            if len(parts) >= 2:
                # Tomar los tokens previos a la fecha numérica
                prefix = []
                for p in parts:
                    if p.isdigit() and len(p) >= 8:
                        break
                    prefix.append(p)
                if prefix:
                    dataset_ids.add("_".join(prefix))
            else:
                dataset_ids.add(f.stem)
        return sorted(list(dataset_ids))

    def _find_latest_file(self, dataset_id: str, preferred_exts: Tuple[str, ...] = (".csv", ".json", ".xlsx")) -> Optional[Path]:
        """Encuentra el archivo más reciente para un dataset_id dado según la extensión preferida."""
        for ext in preferred_exts:
            candidates = list(self.raw_dir.glob(f"{dataset_id}_*{ext}")) + list(self.raw_dir.glob(f"{dataset_id}{ext}"))
            if candidates:
                # Ordenar por fecha de modificación descendente
                candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                return candidates[0]
        return None

    def load_dataset(self, dataset_id: str, clean_column_names: bool = True) -> pd.DataFrame:
        """
        Carga el dataset especificado en un DataFrame de pandas.
        Aplica autodetección de encabezados y conversión de tipos inicial.
        """
        filepath = self._find_latest_file(dataset_id)
        if not filepath:
            raise FileNotFoundError(
                f"No se encontró ningún archivo para el dataset '{dataset_id}' en {self.raw_dir}."
            )

        suffix = filepath.suffix.lower()
        logger.info("Cargando dataset [%s] desde %s", dataset_id, filepath.name)

        if suffix == ".csv":
            try:
                # Intentar lectura estándar con codificación UTF-8
                df = pd.read_csv(filepath, encoding="utf-8")
            except UnicodeDecodeError:
                # Fallback a latin-1 para compatibilidad DANE
                df = pd.read_csv(filepath, encoding="latin-1")
        elif suffix == ".json":
            df = pd.read_json(filepath)
        elif suffix in [".xlsx", ".xls"]:
            # Autodetección de filas de encabezado en formatos DANE
            df_raw = pd.read_excel(filepath, header=None)
            header_row = 0
            # Buscar la primera fila con suficiente número de strings no nulos
            for idx in range(min(15, len(df_raw))):
                row_vals = df_raw.iloc[idx].dropna()
                if len(row_vals) >= 3 and any(isinstance(v, str) and len(v) > 2 for v in row_vals):
                    header_row = idx
                    break
            df = pd.read_excel(filepath, header=header_row)
        else:
            raise ValueError(f"Formato no soportado: {suffix}")

        # Limpieza estándar de nombres de columnas
        if clean_column_names:
            df.columns = [
                str(c).strip().replace(" ", "_").replace(".", "_").replace("/", "_").lower()
                for c in df.columns
            ]

        # Inyectar atributo con metadatos de linaje
        df.attrs["dataset_id"] = dataset_id
        df.attrs["source_path"] = str(filepath)
        df.attrs["file_name"] = filepath.name

        return df

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Carga todos los conjuntos de datos presentes en data/RAW en un diccionario.
        """
        available = self.list_available_datasets()
        loaded: Dict[str, pd.DataFrame] = {}

        for ds_id in available:
            try:
                loaded[ds_id] = self.load_dataset(ds_id)
                logger.info("Dataset [%s] cargado con éxito: %d filas, %d columnas", ds_id, len(loaded[ds_id]), len(loaded[ds_id].columns))
            except Exception as e:
                logger.warning("No se pudo cargar el dataset %s: %s", ds_id, e)

        return loaded


def find_cleaned_data_dir() -> Path:
    """
    Localiza de forma resiliente el directorio data/CLEANED buscando en jerarquías relativas
    desde la carpeta actual de ejecución, notebooks o src.
    """
    candidate_paths = [
        # Desde notebooks/ (CRISPDM/notebooks/ -> CRISPDM/data/CLEANED)
        Path.cwd().parent / "data" / "CLEANED",
        # Desde la raíz del proyecto AgroStatsApp/
        Path.cwd() / "CRISPDM" / "data" / "CLEANED",
        Path.cwd() / "data" / "CLEANED",
        # Relativo a este archivo fuente
        Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "CLEANED",
        Path(__file__).resolve().parent.parent.parent / "data" / "CLEANED",
    ]

    for p in candidate_paths:
        if p.exists() and p.is_dir():
            return p.resolve()

    default_dir = Path(__file__).resolve().parent.parent.parent / "CRISPDM" / "data" / "CLEANED"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir.resolve()


class CleanDataLoader:
    """
    Lector oficial de conjuntos de datos depurados, imputados y estandarizados
    ubicados en data/CLEANED para las fases analíticas de CRISP-DM (EDA, MDM, Features, ML).
    """

    def __init__(self, cleaned_dir: Optional[Union[str, Path]] = None) -> None:
        self.cleaned_dir = Path(cleaned_dir) if cleaned_dir else find_cleaned_data_dir()

    def list_available_datasets(self) -> List[str]:
        """Lista los IDs de datasets limpios encontrados en data/CLEANED."""
        files = list(self.cleaned_dir.glob("*.csv")) + list(self.cleaned_dir.glob("*.json"))
        dataset_ids = set()
        for f in files:
            if f.name.startswith("cleaned_manifest") or f.suffix.lower() in [".md", ".txt"]:
                continue
            dataset_ids.add(f.stem)
        return sorted(list(dataset_ids))

    def generate_all_clean_datasets(self) -> None:
        """Genera y persiste automáticamente las 10 fuentes limpias desde data/RAW."""
        from pathlib import Path
        import numpy as np
        raw_loader = RawDataLoader()
        raw_dir = raw_loader.raw_dir
        self.cleaned_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. ideam_pluvio
        try:
            df_p = raw_loader.load_dataset("ideam_pluvio")
            cl_p = pd.DataFrame({
                "codigo_estacion": df_p.get("codigoestacion", "").astype(str),
                "fecha_observacion": pd.to_datetime(df_p.get("fechaobservacion"), errors="coerce"),
                "valor_observado": pd.to_numeric(df_p.get("valorobservado"), errors="coerce").clip(lower=0.0),
                "nombre_estacion": df_p.get("nombreestacion", ""),
                "departamento": df_p.get("departamento", "").astype(str).str.strip().str.upper(),
                "municipio": df_p.get("municipio", "").astype(str).str.strip().str.upper(),
                "latitud": pd.to_numeric(df_p.get("latitud"), errors="coerce"),
                "longitud": pd.to_numeric(df_p.get("longitud"), errors="coerce"),
                "unidad_medida": "mm",
            }).dropna(subset=["fecha_observacion", "valor_observado"]).sort_values("fecha_observacion").reset_index(drop=True)
            cl_p.to_csv(self.cleaned_dir / "ideam_pluvio.csv", index=False)
            cl_p.to_json(self.cleaned_dir / "ideam_pluvio.json", orient="records", indent=2, date_format="iso")
        except Exception as e:
            logger.debug("Error auto-limpiando ideam_pluvio: %s", e)

        # 2. ideam_temperatura
        try:
            df_t = raw_loader.load_dataset("ideam_temperatura")
            cl_t = pd.DataFrame({
                "codigo_estacion": df_t.get("codigoestacion", "").astype(str),
                "fecha_observacion": pd.to_datetime(df_t.get("fechaobservacion"), errors="coerce"),
                "valor_observado": pd.to_numeric(df_t.get("valorobservado"), errors="coerce"),
                "nombre_estacion": df_t.get("nombreestacion", ""),
                "departamento": df_t.get("departamento", "").astype(str).str.strip().str.upper(),
                "municipio": df_t.get("municipio", "").astype(str).str.strip().str.upper(),
                "latitud": pd.to_numeric(df_t.get("latitud"), errors="coerce"),
                "longitud": pd.to_numeric(df_t.get("longitud"), errors="coerce"),
                "unidad_medida": "°C",
            }).dropna(subset=["fecha_observacion", "valor_observado"]).sort_values("fecha_observacion").reset_index(drop=True)
            cl_t.to_csv(self.cleaned_dir / "ideam_temperatura.csv", index=False)
            cl_t.to_json(self.cleaned_dir / "ideam_temperatura.json", orient="records", indent=2, date_format="iso")
        except Exception as e:
            logger.debug("Error auto-limpiando ideam_temperatura: %s", e)

        # 3. ideam_evapotranspiracion
        try:
            df_e = raw_loader.load_dataset("ideam_evapotranspiracion")
            months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic", "anual"]
            for m in months:
                if m in df_e.columns:
                    df_e[m] = pd.to_numeric(df_e[m], errors="coerce")
            df_e["indicador"] = "ET0_mm"
            df_e.to_csv(self.cleaned_dir / "ideam_evapotranspiracion.csv", index=False)
            df_e.to_json(self.cleaned_dir / "ideam_evapotranspiracion.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando ideam_evapotranspiracion: %s", e)

        # 4. ideam_radiacion
        try:
            df_r = raw_loader.load_dataset("ideam_radiacion")
            months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic", "anual"]
            for m in months:
                if m in df_r.columns:
                    df_r[m] = pd.to_numeric(df_r[m], errors="coerce")
            df_r["indicador"] = "Radiacion_Solar_Global"
            df_r.to_csv(self.cleaned_dir / "ideam_radiacion.csv", index=False)
            df_r.to_json(self.cleaned_dir / "ideam_radiacion.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando ideam_radiacion: %s", e)

        # 5. ideam_sequia
        try:
            df_s = raw_loader.load_dataset("ideam_sequia")
            months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic", "anual"]
            for m in months:
                if m in df_s.columns:
                    df_s[m] = pd.to_numeric(df_s[m], errors="coerce")
            df_s["indicador"] = "Precipitacion_Normal_mm"
            df_s.to_csv(self.cleaned_dir / "ideam_sequia.csv", index=False)
            df_s.to_json(self.cleaned_dir / "ideam_sequia.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando ideam_sequia: %s", e)

        # 6. sipsa_insumos
        try:
            df_i = raw_loader.load_dataset("sipsa_insumos")
            df_i["fecha"] = pd.to_datetime(df_i["fecha"], errors="coerce")
            num_cols = [c for c in df_i.columns if c != "fecha"]
            for col in num_cols:
                df_i[col] = pd.to_numeric(df_i[col], errors="coerce")
            df_i = df_i.dropna(subset=["fecha"]).sort_values("fecha").reset_index(drop=True)
            df_i.to_csv(self.cleaned_dir / "sipsa_insumos.csv", index=False)
            df_i.to_json(self.cleaned_dir / "sipsa_insumos.json", orient="records", indent=2, date_format="iso")
        except Exception as e:
            logger.debug("Error auto-limpiando sipsa_insumos: %s", e)

        # 7. sipsa_precios
        try:
            xlsx_files = sorted(raw_dir.glob("sipsa_precios_*temp_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
            csv_files = sorted(raw_dir.glob("sipsa_precios_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
            raw_p = pd.read_excel(xlsx_files[0], header=None) if xlsx_files else pd.read_csv(csv_files[0], header=None)
            m_names = {}
            for col_idx in range(1, raw_p.shape[1], 2):
                val = raw_p.iloc[2, col_idx]
                if pd.notna(val):
                    m_names[col_idx] = str(val).strip().replace("\n", " ").replace("", "o")
            recs_p = []
            cur_cat = "General"
            for row_idx in range(4, len(raw_p)):
                first_v = raw_p.iloc[row_idx, 0]
                if pd.isna(first_v):
                    continue
                first_s = str(first_v).strip()
                has_pr = False
                for c in m_names.keys():
                    v = raw_p.iloc[row_idx, c]
                    if pd.notna(v) and str(v).replace("$", "").replace(".", "").replace(",", "").strip().isdigit():
                        has_pr = True
                        break
                if not has_pr:
                    cur_cat = first_s
                    continue
                p_name = first_s.replace("*", "").strip()
                for col_idx, mkt in m_names.items():
                    p_val = raw_p.iloc[row_idx, col_idx]
                    var_val = raw_p.iloc[row_idx, col_idx + 1] if col_idx + 1 < raw_p.shape[1] else np.nan
                    p_num = pd.to_numeric(str(p_val).replace("$", "").replace(".", "").replace(",", "").strip(), errors="coerce")
                    var_num = pd.to_numeric(str(var_val).replace("%", "").strip(), errors="coerce")
                    if pd.notna(p_num) and p_num > 0:
                        recs_p.append({
                            "producto": p_name,
                            "categoria": cur_cat,
                            "mercado": mkt,
                            "precio_kg": float(p_num),
                            "variacion_pct": float(var_num) if pd.notna(var_num) else 0.0,
                        })
            cl_pr = pd.DataFrame(recs_p)
            cl_pr.to_csv(self.cleaned_dir / "sipsa_precios.csv", index=False)
            cl_pr.to_json(self.cleaned_dir / "sipsa_precios.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando sipsa_precios: %s", e)

        # 8. sipsa_abastecimientos
        try:
            xlsx_files = sorted(raw_dir.glob("sipsa_abastecimientos_*temp_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
            if xlsx_files:
                df_sheet = pd.read_excel(xlsx_files[0], sheet_name="1")
                start_idx = 0
                for idx in range(len(df_sheet)):
                    row_str = " ".join([str(v) for v in df_sheet.iloc[idx].values])
                    if "Ciudad" in row_str and "Central" in row_str:
                        start_idx = idx
                        break
                clean_a = pd.read_excel(xlsx_files[0], sheet_name="1", header=start_idx).dropna(how="all")
                clean_a.columns = [str(c).strip().replace("\n", " ").replace(" ", "_").lower() for c in clean_a.columns]
                clean_a = clean_a[clean_a.iloc[:, 0].notna() & ~clean_a.iloc[:, 0].astype(str).str.contains("Regresar|Nota|Fuente", case=False)]
                clean_a.to_csv(self.cleaned_dir / "sipsa_abastecimientos.csv", index=False)
                clean_a.to_json(self.cleaned_dir / "sipsa_abastecimientos.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando sipsa_abastecimientos: %s", e)

        # 9. dane_ipc
        try:
            xlsx_files = sorted(raw_dir.glob("dane_ipc_*temp_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
            if xlsx_files:
                df_ipc_raw = pd.read_excel(xlsx_files[0], sheet_name="IndicesIPC")
                s_row = 7
                h_row = df_ipc_raw.iloc[s_row].values
                yrs = [int(float(y)) for y in h_row[1:] if pd.notna(y) and str(y).replace(".0", "").isdigit()]
                m_map = {
                    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
                    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
                }
                recs_ipc = []
                for r in range(s_row + 1, len(df_ipc_raw)):
                    m_str = str(df_ipc_raw.iloc[r, 0]).strip()
                    if m_str not in m_map:
                        continue
                    m_n = m_map[m_str]
                    for c_idx, y in enumerate(yrs, start=1):
                        val = pd.to_numeric(df_ipc_raw.iloc[r, c_idx], errors="coerce")
                        if pd.notna(val) and val > 0:
                            recs_ipc.append({
                                "fecha": f"{y:04d}-{m_n:02d}-01",
                                "anio": y,
                                "mes": m_str,
                                "mes_num": m_n,
                                "ipc_alimentos": round(float(val), 2),
                            })
                cl_ipc = pd.DataFrame(recs_ipc).sort_values("fecha").reset_index(drop=True)
                cl_ipc.to_csv(self.cleaned_dir / "dane_ipc.csv", index=False)
                cl_ipc.to_json(self.cleaned_dir / "dane_ipc.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando dane_ipc: %s", e)

        # 10. dane_ipp
        try:
            xlsx_files = sorted(raw_dir.glob("dane_ipp_*temp_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
            if xlsx_files:
                df_ipp_raw = pd.read_excel(xlsx_files[0], sheet_name="1.1")
                h_ipp = [str(c).strip() for c in df_ipp_raw.iloc[4].values]
                cl_ipp = df_ipp_raw.iloc[5:25].copy()
                cl_ipp.columns = [f"col_{i}_{str(h)}" for i, h in enumerate(h_ipp)]
                cl_ipp = cl_ipp.dropna(how="all").reset_index(drop=True)
                cl_ipp.to_csv(self.cleaned_dir / "dane_ipp.csv", index=False)
                cl_ipp.to_json(self.cleaned_dir / "dane_ipp.json", orient="records", indent=2)
        except Exception as e:
            logger.debug("Error auto-limpiando dane_ipp: %s", e)

    def load_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Carga un dataset limpio específico desde data/CLEANED."""
        csv_file = self.cleaned_dir / f"{dataset_id}.csv"
        json_file = self.cleaned_dir / f"{dataset_id}.json"

        if not csv_file.exists() and not json_file.exists():
            self.generate_all_clean_datasets()

        if csv_file.exists():
            df = pd.read_csv(csv_file)
        elif json_file.exists():
            df = pd.read_json(json_file)
        else:
            raise FileNotFoundError(
                f"No se encontró el dataset limpio '{dataset_id}' en {self.cleaned_dir}."
            )

        df.attrs["dataset_id"] = dataset_id
        df.attrs["status"] = "CLEANED"
        return df

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Carga todos los datasets limpios disponibles en un diccionario."""
        available = self.list_available_datasets()
        if not available:
            self.generate_all_clean_datasets()
            available = self.list_available_datasets()

        loaded: Dict[str, pd.DataFrame] = {}
        for ds_id in available:
            try:
                loaded[ds_id] = self.load_dataset(ds_id)
                logger.info("Dataset limpio [%s] cargado con éxito: %d filas x %d columnas", ds_id, len(loaded[ds_id]), len(loaded[ds_id].columns))
            except Exception as e:
                logger.warning("No se pudo cargar el dataset limpio %s: %s", ds_id, e)
        return loaded


def load_cleaned_dataset(dataset_id: str) -> pd.DataFrame:
    """Función de una sola línea para cargar una fuente limpia de data/CLEANED por su ID."""
    loader = CleanDataLoader()
    return loader.load_dataset(dataset_id)


def load_all_cleaned_datasets() -> Dict[str, pd.DataFrame]:
    """Carga todas las fuentes limpias disponibles en data/CLEANED en un diccionario."""
    loader = CleanDataLoader()
    return loader.load_all_datasets()
