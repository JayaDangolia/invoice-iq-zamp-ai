import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pymupdf
from core.exceptions import ExtractionError

class PDFReaderService:
    def __init__(self, min_text_threshold: int = 50):
        self.min_text_threshold = min_text_threshold

    def calculate_file_hash(self, file_bytes: bytes) -> str:
        """Calculate SHA-256 hash of the uploaded document bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    def inspect_and_extract_text(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Inspect PDF bytes and extract text, layout metadata, and page counts.
        Returns extracted text, page count, and whether OCR is required.
        """
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise ExtractionError(f"Failed to open PDF document: {str(e)}") from e

        page_count = len(doc)
        full_text_pages: List[str] = []
        page_metadata: List[Dict[str, Any]] = []

        total_char_count = 0
        for page_idx in range(page_count):
            page = doc[page_idx]
            page_text = page.get_text("text") or ""
            full_text_pages.append(page_text)
            char_count = len(page_text.strip())
            total_char_count += char_count

            rect = page.rect
            page_metadata.append({
                "page_number": page_idx + 1,
                "width": rect.width,
                "height": rect.height,
                "char_count": char_count,
            })

        full_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text_pages).strip()
        needs_ocr = total_char_count < self.min_text_threshold

        return {
            "page_count": page_count,
            "full_text": full_text,
            "raw_pages": full_text_pages,
            "char_count": total_char_count,
            "needs_ocr": needs_ocr,
            "page_metadata": page_metadata,
        }

    def render_page_image(self, file_bytes: bytes, page_number: int = 0, dpi: int = 150) -> bytes:
        """Render a specific PDF page to PNG image bytes for preview or OCR."""
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            if page_number >= len(doc):
                page_number = 0
            page = doc[page_number]
            zoom = dpi / 72.0
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            return pix.tobytes("png")
        except Exception as e:
            raise ExtractionError(f"Failed to render PDF page {page_number}: {str(e)}") from e
