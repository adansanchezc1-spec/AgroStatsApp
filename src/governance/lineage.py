"""
Sistema de Trazabilidad, Linaje de Datos y DAG (Data Lineage & Provenance)
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2 (Data Governance, Metadata & Data Lineage)
"""

import os
import json
import hashlib
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import pandas as pd

logger = logging = __import__("logging").getLogger(__name__)


@dataclass
class LineageNode:
    node_id: str
    layer: str  # SOURCE, BRONZE, SILVER, GOLD
    dataset_name: str
    target_path_or_table: str
    input_records: int
    output_records: int
    checksum_sha256: str
    execution_time_sec: float
    timestamp: str
    quality_score: Optional[float] = None
    quality_status: Optional[str] = None
    transformations_applied: List[str] = field(default_factory=list)
    upstream_nodes: List[str] = field(default_factory=list)


class DataLineageTracker:
    """
    Rastrea el linaje completo de datos desde la fuente hasta las tablas analíticas Gold.
    Construye el grafo acíclico dirigido (DAG) y produce reportes Mermaid y JSON.
    """

    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S")
        self.start_time = time.time()

    @staticmethod
    def calculate_checksum(df: pd.DataFrame) -> str:
        """Calcula hash criptográfico SHA-256 del contenido muestreado para integridad."""
        if df.empty:
            return "empty_dataframe_sha256"
        sample_bytes = df.head(1000).to_csv(index=False).encode("utf-8")
        return hashlib.sha256(sample_bytes).hexdigest()

    def record_stage(
        self,
        node_id: str,
        layer: str,
        dataset_name: str,
        target_path_or_table: str,
        input_records: int,
        output_records: int,
        checksum: str,
        execution_time_sec: float,
        quality_score: Optional[float] = None,
        quality_status: Optional[str] = None,
        transformations: Optional[List[str]] = None,
        upstream_nodes: Optional[List[str]] = None
    ) -> LineageNode:
        node = LineageNode(
            node_id=node_id,
            layer=layer.upper(),
            dataset_name=dataset_name,
            target_path_or_table=target_path_or_table,
            input_records=input_records,
            output_records=output_records,
            checksum_sha256=checksum,
            execution_time_sec=round(execution_time_sec, 3),
            timestamp=datetime.now().isoformat(),
            quality_score=round(quality_score, 4) if quality_score is not None else None,
            quality_status=quality_status,
            transformations_applied=transformations or [],
            upstream_nodes=upstream_nodes or []
        )
        self.nodes[node_id] = node
        logger.info(f"[Lineage] Registrado nodo '{node_id}' ({layer}) para dataset '{dataset_name}'.")
        return node

    def to_manifest(self) -> Dict[str, Any]:
        """Genera el manifiesto completo de gobernanza y trazabilidad."""
        total_time = round(time.time() - self.start_time, 2)
        total_records_processed = sum(n.output_records for n in self.nodes.values() if n.layer == "SILVER")
        return {
            "run_id": self.run_id,
            "completed_at": datetime.now().isoformat(),
            "total_execution_time_seconds": total_time,
            "total_silver_records": total_records_processed,
            "total_nodes": len(self.nodes),
            "layers_summary": {
                "bronze_count": sum(1 for n in self.nodes.values() if n.layer == "BRONZE"),
                "silver_count": sum(1 for n in self.nodes.values() if n.layer == "SILVER"),
                "gold_count": sum(1 for n in self.nodes.values() if n.layer == "GOLD")
            },
            "nodes": {nid: asdict(node) for nid, node in self.nodes.items()}
        }

    def generate_mermaid_dag(self) -> str:
        """Genera diagrama Mermaid del flujo de datos de extremo a extremo."""
        lines = [
            "```mermaid",
            "flowchart LR",
            "    classDef bronze fill:#f9d5e5,stroke:#333,stroke-width:1px;",
            "    classDef silver fill:#eeeeee,stroke:#333,stroke-width:1px;",
            "    classDef gold fill:#d4edda,stroke:#28a745,stroke-width:2px;"
        ]

        for nid, node in self.nodes.items():
            label = f"{node.dataset_name}<br/>({node.output_records:,} filas)"
            cls_name = node.layer.lower()
            lines.append(f'    {nid}["{label}"]:::{cls_name}')
            for up in node.upstream_nodes:
                if up in self.nodes:
                    lines.append(f"    {up} --> {nid}")

        lines.append("```")
        return "\n".join(lines)

    def save_artifacts(self, manifest_path: Path, mermaid_path: Path) -> None:
        """Guarda el manifiesto JSON y el diagrama Mermaid en disco."""
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.to_manifest(), f, indent=2)

        mermaid_path.parent.mkdir(parents=True, exist_ok=True)
        with open(mermaid_path, "w", encoding="utf-8") as f:
            f.write("# Diagrama de Linaje y Trazabilidad de Datos (DAG)\n\n")
            f.write(f"**Generado**: {datetime.now().isoformat()} | **Run ID**: `{self.run_id}`\n\n")
            f.write(self.generate_mermaid_dag())
            f.write("\n")
