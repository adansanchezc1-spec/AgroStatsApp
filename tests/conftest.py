"""Fixtures y Configuración Global para la Suite de Pruebas Pytest.
Fase PDCO: CONTROL | Estándar: ISO/IEC/IEEE 29119
"""

from __future__ import annotations
import sqlite3
import pytest
from pathlib import Path
from typing import Generator, Dict, Any


@pytest.fixture
def temp_lakehouse_dirs(tmp_path: Path) -> Dict[str, Path]:
    """Genera una estructura efímera y aislada de directorios para pruebas."""
    dirs = {
        "raw": tmp_path / "RAW",
        "raw_ica": tmp_path / "RAW" / "ica",
        "raw_ideam": tmp_path / "RAW" / "ideam",
        "raw_dane": tmp_path / "RAW" / "dane",
        "raw_upra": tmp_path / "RAW" / "upra",
        "cleaned": tmp_path / "CLEANED",
        "indicators": tmp_path / "INDICATORS",
        "database": tmp_path / "DATABASE",
        "logs": tmp_path / "logs",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs


@pytest.fixture
def in_memory_sqlite() -> Generator[sqlite3.Connection, None, None]:
    """Conexión SQLite en memoria aislada para pruebas transaccionales."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
