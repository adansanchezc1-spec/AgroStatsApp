"""Módulo de Logging Estructurado.
Fase PDCO: DEVELOPMENT | Estándar: Clean Code / SWEBOK
Centralización de bitácora sin uso de print().
"""

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from src.config.settings import settings


_LOGGERS: dict[str, logging.Logger] = {}


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    force: bool = False,
) -> None:
    """Configura el handler raíz del sistema."""
    resolved_log_dir = log_dir or settings.LOGS_DIR
    resolved_log_dir.mkdir(parents=True, exist_ok=True)
    
    resolved_level = getattr(logging, (log_level or settings.LOG_LEVEL).upper(), logging.INFO)
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%dT%H:%M:%S%z"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    root_logger = logging.getLogger("agrostats")
    root_logger.setLevel(resolved_level)

    # Si se pide forzar o no hay handlers configurados
    if force or not root_logger.handlers:
        for handler in list(root_logger.handlers):
            handler.close()
            root_logger.removeHandler(handler)

        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(resolved_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Handler de archivo rotativo
        log_file = resolved_log_dir / "agrostats.log"
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(resolved_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger con el namespace jerárquico 'agrostats.<name>'."""
    if not logging.getLogger("agrostats").handlers:
        setup_logging()

    logger_name = f"agrostats.{name}" if not name.startswith("agrostats") else name
    if logger_name not in _LOGGERS:
        _LOGGERS[logger_name] = logging.getLogger(logger_name)
    return _LOGGERS[logger_name]
