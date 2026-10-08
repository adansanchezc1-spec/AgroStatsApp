"""Gestor de Datos Maestros (Master Data Management - MDM).
Fase PDCO: DEVELOPMENT | Estándar: DAMA-DMBOK 2 (Master & Reference Data) / Clean Code
Algoritmos de reconciliación difusa (Levenshtein y Jaro-Winkler) para Golden Records.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from src.utils.logger import get_logger
from src.cleaning.transformers import sanitize_text

logger = get_logger("database.mdm_manager")


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calcula la distancia de edición mínima de Levenshtein entre dos cadenas."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Retorna similitud normalizada en rango [0.0, 1.0] mediante distancia Levenshtein."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1.0 - (levenshtein_distance(s1, s2) / max_len)


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Calcula el coeficiente de similitud de Jaro-Winkler entre dos cadenas.
    Especialmente efectivo para nombres propios, municipios y términos agrícolas.
    """
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    max_dist = max(len1, len2) // 2 - 1

    match1 = [False] * len1
    match2 = [False] * len2
    matches = 0

    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len2)
        for j in range(start, end):
            if not match2[j] and s1[i] == s2[j]:
                match1[i] = True
                match2[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    # Contar transposiciones
    t = 0
    point2 = 0
    for i in range(len1):
        if match1[i]:
            while not match2[point2]:
                point2 += 1
            if s1[i] != s2[point2]:
                t += 1
            point2 += 1
    t = t / 2.0

    jaro = (matches / len1 + matches / len2 + (matches - t) / matches) / 3.0

    # Prefijo común hasta 4 caracteres
    l = 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]:
            l += 1
        else:
            break

    return jaro + (l * p * (1.0 - jaro))


class MDMManager:
    """Orquestador de Master Data Management para reconciliación de entidades maestras."""

    def __init__(self, match_threshold: float = 0.85) -> None:
        self.match_threshold = match_threshold
        self.golden_municipios: Dict[str, Dict[str, Any]] = {}
        self.golden_productos: Dict[str, Dict[str, Any]] = {}

    def register_canonical_municipios(self, df_divipola: pd.DataFrame) -> int:
        """
        Registra el catálogo canónico de municipios DIVIPOLA (DANE).
        Requiere columnas: ['cod_municipio', 'nombre_municipio', 'cod_departamento', 'nombre_departamento'].
        """
        registered = 0
        for _, row in df_divipola.iterrows():
            cod_mun = str(row.get("cod_municipio", "")).strip().zfill(5)
            nom_mun = sanitize_text(row.get("nombre_municipio", ""))
            cod_dep = str(row.get("cod_departamento", "")).strip().zfill(2)
            nom_dep = sanitize_text(row.get("nombre_departamento", ""))

            if cod_mun and nom_mun:
                self.golden_municipios[cod_mun] = {
                    "cod_municipio": cod_mun,
                    "nombre_municipio": nom_mun,
                    "cod_departamento": cod_dep,
                    "nombre_departamento": nom_dep,
                }
                registered += 1

        logger.info("MDM: Registrados %d municipios canónicos DIVIPOLA", registered)
        return registered

    def match_municipio(self, raw_name: str, dep_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Reconcilia un nombre de municipio crudo contra los registros canónicos.
        Retorna el Golden Record si supera el umbral de similitud.
        """
        clean_name = sanitize_text(raw_name)
        if not clean_name or not self.golden_municipios:
            return None

        best_match = None
        best_score = -1.0

        for mun in self.golden_municipios.values():
            canonical_name = mun["nombre_municipio"]

            # Coincidencia exacta
            if clean_name == canonical_name:
                return {**mun, "similarity_score": 1.0, "match_type": "EXACT"}

            # Similitud compuesta (Levenshtein y Jaro-Winkler)
            sim_jw = jaro_winkler_similarity(clean_name, canonical_name)
            sim_lev = levenshtein_similarity(clean_name, canonical_name)
            score = 0.6 * sim_jw + 0.4 * sim_lev

            # Filtro opcional por departamento para evitar homónimos
            if dep_hint and mun["nombre_departamento"]:
                clean_dep = sanitize_text(dep_hint)
                if clean_dep != mun["nombre_departamento"]:
                    score *= 0.8  # Penalización por departamento discordante

            if score > best_score:
                best_score = score
                best_match = mun

        if best_score >= self.match_threshold and best_match is not None:
            return {**best_match, "similarity_score": round(best_score, 4), "match_type": "FUZZY"}

        return None
