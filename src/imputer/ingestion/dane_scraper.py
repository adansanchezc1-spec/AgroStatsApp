"""
Extractor y Descargador Automatizado para Publicaciones DANE
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
Estándares: DAMA-DMBOK 2, SWEBOK Cap. 1 & 2, Resiliencia ante Cambios Web
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .base_client import ResilientHttpClient
from .constants import DANE_BASE_URL

logger = logging.getLogger(__name__)

SPANISH_MONTHS = {
    1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
    7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"
}


class DaneScraper:
    """
    Extractor dinámico de series, microdatos y boletines oficiales del DANE
    (SIPSA Precios Mayoristas, Abastecimiento, Insumos, IPP e IPC).
    """

    def __init__(self, http_client: Optional[ResilientHttpClient] = None) -> None:
        self.http_client = http_client or ResilientHttpClient()
        self.base_url = DANE_BASE_URL.rstrip("/")

    def _scrape_page_links(
        self,
        page_url: str,
        match_extensions: Tuple[str, ...] = (".xlsx", ".xls", ".csv", ".zip"),
    ) -> List[Tuple[str, str]]:
        """
        Inspecciona una URL del DANE y extrae pares (texto_enlace, url_absoluta).
        """
        try:
            response = self.http_client.get(page_url)
            soup = BeautifulSoup(response.text, "html.parser")
            extracted: List[Tuple[str, str]] = []

            for tag_a in soup.find_all("a", href=True):
                href = tag_a["href"].strip()
                text = tag_a.get_text(strip=True)
                if any(href.lower().endswith(ext) or ext in href.lower() for ext in match_extensions):
                    full_url = urljoin(page_url, href)
                    extracted.append((text, full_url))

            return extracted
        except Exception as exc:
            logger.warning("Fallo al escanear enlaces en %s: %s", page_url, exc)
            return []

    def get_latest_sipsa_precios_urls(self, max_days_back: int = 5) -> List[str]:
        """
        Descubre las URLs más recientes de Precios Mayoristas Diarios SIPSA.
        Estrategia dual: escaneo del portal + generador dinámico de fechas.
        """
        page_url = (
            f"{self.base_url}/index.php/estadisticas-por-tema/agropecuario/"
            "sistema-de-informacion-de-precios-sipsa/componente-precios-mayoristas"
        )
        found_links = self._scrape_page_links(page_url, match_extensions=(".xlsx", ".zip"))
        urls = [url for _, url in found_links if "anex-sipsadiario" in url.lower()]

        if urls:
            return list(dict.fromkeys(urls))

        # Generador dinámico de respaldo si el DOM no contiene enlaces estáticos
        now = datetime.now()
        dynamic_urls = []
        for delta in range(max_days_back):
            target_date = now - timedelta(days=delta)
            if target_date.weekday() >= 6:  # Domingo no se publica
                continue
            day_str = f"{target_date.day:02d}"
            month_str = SPANISH_MONTHS[target_date.month]
            year_str = str(target_date.year)
            url = f"{self.base_url}/files/operaciones/SIPSA/anex-SIPSADiario-{day_str}{month_str}{year_str}.xlsx"
            dynamic_urls.append(url)

        return list(dict.fromkeys(dynamic_urls))

    def get_sipsa_abastecimiento_urls(self) -> List[str]:
        """
        Obtiene enlaces de abastecimiento de alimentos (microdatos y series históricas).
        """
        page_url = (
            f"{self.base_url}/index.php/estadisticas-por-tema/agropecuario/"
            "sistema-de-informacion-de-precios-sipsa/componente-abastecimientos-1"
        )
        links = self._scrape_page_links(page_url)
        urls = [url for _, url in links if "abastecimiento" in url.lower()]

        if not urls:
            # Enlaces canónicos permanentes de respaldo
            current_year = datetime.now().year
            urls = [
                f"{self.base_url}/files/operaciones/SIPSA/Series-historicas-abastecimiento-2013-{current_year}.xlsx",
                f"{self.base_url}/files/operaciones/SIPSA/anex-Microdato-abastecimiento-{current_year}.xlsx",
            ]
        return list(dict.fromkeys(urls))

    def get_sipsa_insumos_urls(self) -> List[str]:
        """
        Obtiene enlaces de precios de insumos agrícolas y factores de producción.
        """
        page_url = (
            f"{self.base_url}/index.php/estadisticas-por-tema/agropecuario/"
            "sistema-de-informacion-de-precios-sipsa/componente-insumos-1"
        )
        links = self._scrape_page_links(page_url)
        urls = [url for _, url in links if "insumo" in url.lower()]
        return list(dict.fromkeys(urls))

    def get_ipp_urls(self) -> List[str]:
        """
        Obtiene enlaces del Índice de Precios del Productor (IPP).
        """
        page_url = (
            f"{self.base_url}/index.php/estadisticas-por-tema/precios-y-costos/"
            "indice-de-precios-del-productor-ipp"
        )
        links = self._scrape_page_links(page_url)
        urls = [url for _, url in links if "ipp" in url.lower()]

        if not urls:
            now = datetime.now()
            month_str = SPANISH_MONTHS[now.month]
            year_str = str(now.year)
            urls = [
                f"{self.base_url}/files/operaciones/IPP/anex-IPP-historicos-{month_str}{year_str}.xlsx",
                f"{self.base_url}/files/operaciones/IPP/anex-IPP-{month_str}{year_str}.xlsx",
            ]
        return list(dict.fromkeys(urls))

    def get_ipc_urls(self) -> List[str]:
        """
        Obtiene enlaces del Índice de Precios del Consumidor (IPC).
        """
        page_url = (
            f"{self.base_url}/index.php/estadisticas-por-tema/precios-y-costos/"
            "indice-de-precios-al-consumidor-ipc"
        )
        links = self._scrape_page_links(page_url)
        urls = [url for _, url in links if "ipc" in url.lower()]

        if not urls:
            now = datetime.now()
            month_str = SPANISH_MONTHS[now.month]
            year_str = str(now.year)
            urls = [
                f"{self.base_url}/files/operaciones/IPC/{month_str}{year_str}/anex-IPC-Indices-{month_str}{year_str}.xlsx",
                f"{self.base_url}/files/operaciones/IPC/{month_str}{year_str}/anex-IPC-Variacion-{month_str}{year_str}.xlsx",
            ]
        return list(dict.fromkeys(urls))

    def download_to(self, url: str, target_filepath: Path) -> Path:
        """
        Descarga el archivo desde el DANE hacia la ruta local de destino.
        """
        target_filepath.parent.mkdir(parents=True, exist_ok=True)
        self.http_client.download_file(url, str(target_filepath))
        return target_filepath
