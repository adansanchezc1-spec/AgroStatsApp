"""
Catálogo de Datos y Diccionario de Metadatos (Data Catalog & Dictionary)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Metadata Management & Data Catalog)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import pandas as pd

logger = __import__("logging").getLogger(__name__)


@dataclass
class ColumnMetadata:
    name: str
    physical_type: str
    logical_type: str
    nullable: bool
    description: str
    sensitivity_tier: str  # PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL_PII
    example_value: Optional[str] = None


@dataclass
class TableCatalogEntry:
    table_name: str
    layer: str  # BRONZE, SILVER, GOLD
    domain: str
    business_description: str
    granularity: str
    primary_key: List[str]
    update_frequency: str
    columns: List[ColumnMetadata] = field(default_factory=list)
    record_count: int = 0
    size_bytes: int = 0


class DataCatalog:
    """
    Catálogo de metadatos gobernados que gestiona el inventario de entidades de datos
    de la arquitectura Medallion Lakehouse de AgroStatsApp.
    """

    def __init__(self):
        self.entries: Dict[str, TableCatalogEntry] = {}

    def register_table(
        self,
        table_name: str,
        layer: str,
        domain: str,
        description: str,
        granularity: str,
        primary_key: List[str],
        frequency: str,
        df: Optional[pd.DataFrame] = None
    ) -> TableCatalogEntry:
        entry = TableCatalogEntry(
            table_name=table_name,
            layer=layer.upper(),
            domain=domain,
            business_description=description,
            granularity=granularity,
            primary_key=primary_key,
            update_frequency=frequency
        )

        if df is not None:
            entry.record_count = len(df)
            entry.size_bytes = int(df.memory_usage(deep=True).sum())
            for col in df.columns:
                dtype_str = str(df[col].dtype)
                has_null = bool(df[col].isna().any())
                
                # Clasificación de sensibilidad (Ley 1581 Habeas Data)
                is_pii = any(k in col.lower() for k in ["email", "correo", "telefono", "phone", "nombre_persona", "cedula"])
                tier = "CONFIDENTIAL_PII" if is_pii else ("INTERNAL" if "id" in col.lower() else "PUBLIC")
                
                sample_val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else None
                if sample_val and len(sample_val) > 40:
                    sample_val = sample_val[:37] + "..."

                entry.columns.append(ColumnMetadata(
                    name=col,
                    physical_type=dtype_str,
                    logical_type="Text" if "object" in dtype_str else ("Numeric" if "int" in dtype_str or "float" in dtype_str else "DateTime"),
                    nullable=has_null,
                    description=f"Atributo {col} en dominio {domain}.",
                    sensitivity_tier=tier,
                    example_value=sample_val
                ))

        self.entries[table_name] = entry
        return entry

    def export_catalog(self, json_path: Path, md_path: Path) -> None:
        """Exporta el catálogo en formato JSON y Markdown técnico."""
        json_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "catalog_title": "AgroData Intelligence Platform Data Catalog",
            "standard": "DAMA-DMBOK 2",
            "last_updated": datetime.now().isoformat(),
            "tables_count": len(self.entries),
            "tables": {t: asdict(entry) for t, entry in self.entries.items()}
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        md_path.parent.mkdir(parents=True, exist_ok=True)
        md = [
            "# Catálogo de Datos y Diccionario de Metadatos (DAMA-DMBOK 2)",
            f"**Plataforma**: AgroStats Intelligence Platform | **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Entidades Gobernadas**: {len(self.entries)} tablas y marts\n",
            "---",
            "## 1. Inventario General de Entidades Lakehouse\n",
            "| Tabla / Entidad | Capa | Dominio | Granularidad | Registros | Frecuencia |",
            "|---|:---:|---|---|---:|:---:|"
        ]

        for t_name, entry in self.entries.items():
            md.append(f"| `{t_name}` | **{entry.layer}** | {entry.domain} | {entry.granularity} | {entry.record_count:,} | {entry.update_frequency} |")

        md.append("\n---")
        md.append("## 2. Diccionario de Datos por Entidad\n")

        for t_name, entry in self.entries.items():
            md.append(f"### Entidad: `{t_name}`")
            md.append(f"- **Capa Medallion**: {entry.layer}")
            md.append(f"- **Descripción**: {entry.business_description}")
            md.append(f"- **Granularidad**: `{entry.granularity}`")
            md.append(f"- **Clave Primaria**: `{', '.join(entry.primary_key) if entry.primary_key else 'N/A'}`\n")
            md.append("| Columna | Tipo Físico | Tipo Lógico | Nullable | Sensibilidad | Ejemplo |")
            md.append("|---|---|---|:---:|:---:|---|")
            for c in entry.columns:
                null_badge = "Sí" if c.nullable else "No"
                sens_badge = f"`{c.sensitivity_tier}`"
                ex_val = c.example_value or "null"
                md.append(f"| `{c.name}` | `{c.physical_type}` | {c.logical_type} | {null_badge} | {sens_badge} | `{ex_val}` |")
            md.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        logger.info(f"[DataCatalog] Catálogo guardado en {json_path} y {md_path}")
