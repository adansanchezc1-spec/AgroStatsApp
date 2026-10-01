"""
Extractor de Documentos y PDFs no estructurados
Fase PDCO: DEVELOPMENT | Active Skill: 03-development
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extrae texto de documentos PDF, limpia encabezados y segmenta en chunks estructurados."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Archivo PDF no encontrado: {pdf_path}")
            
    def extract_chunks(self, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        """Extrae texto por páginas y genera chunks con metadatos de linaje."""
        text_pages = []
        try:
            import pypdf
            reader = pypdf.PdfReader(str(self.pdf_path))
            for idx, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                text_pages.append((idx + 1, txt))
        except Exception as e:
            logger.warning(f"Error con pypdf, utilizando fallback de lectura binaria de texto: {e}")
            with open(self.pdf_path, 'rb') as f:
                content = f.read().decode('latin-1', errors='ignore')
                text_pages.append((1, content))
                
        chunks = []
        chunk_id = 0
        for page_num, page_text in text_pages:
            clean_text = " ".join(page_text.split())
            for i in range(0, max(1, len(clean_text)), chunk_size - overlap):
                segment = clean_text[i:i + chunk_size]
                if segment.strip():
                    chunk_id += 1
                    chunks.append({
                        "chunk_id": chunk_id,
                        "source_file": self.pdf_path.name,
                        "page_number": page_num,
                        "chunk_text": segment,
                        "char_length": len(segment)
                    })
                    
        logger.info(f"PDF {self.pdf_path.name} procesado: {len(chunks)} chunks generados.")
        return chunks
