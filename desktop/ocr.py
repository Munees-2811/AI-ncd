"""
Medical report scanner (OCR) for the NCD Shield AI desktop app.

Extracts common lab/vital values from an uploaded lab report so the assessment
form can be auto-filled. Supports image scans (PNG/JPG, via Tesseract OCR) and
PDFs (text extracted directly; OCR fallback for scanned PDFs).

All heavy dependencies are optional and imported lazily, so the desktop app
still runs if OCR libraries aren't installed — the scan button simply reports
what's missing instead of crashing.

Install extras with:  pip install -r desktop/requirements.txt
For image OCR you also need the Tesseract engine:
  • Windows: https://github.com/UB-Mannheim/tesseract/wiki
  • macOS:   brew install tesseract
  • Linux:   sudo apt install tesseract-ocr
"""
from __future__ import annotations

import re

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}


class OCRUnavailable(Exception):
    """Raised when a required OCR/extraction dependency is missing."""


# --- Text extraction --------------------------------------------------------
def _extract_text_from_image(path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise OCRUnavailable(
            "Image scanning needs 'pytesseract' and 'Pillow'.\n"
            "Run: pip install -r desktop/requirements.txt\n"
            "and install the Tesseract OCR engine (see desktop/ocr.py header)."
        ) from exc
    try:
        return pytesseract.image_to_string(Image.open(path))
    except Exception as exc:  # pragma: no cover
        raise OCRUnavailable(
            "Could not run Tesseract OCR. Is the Tesseract engine installed and on PATH?\n"
            f"Details: {exc}"
        ) from exc


def _extract_text_from_pdf(path: str) -> str:
    # Prefer pdfplumber (handles text PDFs well); fall back to pypdf.
    try:
        import pdfplumber

        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
        joined = "\n".join(text).strip()
        if joined:
            return joined
    except ImportError:
        pass
    except Exception:
        pass

    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except ImportError as exc:
        raise OCRUnavailable(
            "PDF reading needs 'pdfplumber' or 'pypdf'.\n"
            "Run: pip install -r desktop/requirements.txt"
        ) from exc


def extract_text(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".pdf"):
        return _extract_text_from_pdf(path)
    if any(lower.endswith(ext) for ext in IMAGE_EXTS):
        return _extract_text_from_image(path)
    raise OCRUnavailable("Unsupported file type. Use a PDF or an image (PNG/JPG).")


# --- Field parsing ----------------------------------------------------------
# Each pattern captures a numeric value near a known lab/vital keyword.
PATTERNS: dict[str, tuple[str, tuple[float, float]]] = {
    # field: (regex, (min_valid, max_valid)). \b word boundaries prevent
    # keywords matching inside other words (e.g. "ht" inside "weight").
    "blood_sugar": (
        r"\b(?:fasting\s+blood\s+sugar|blood\s+sugar|glucose|fbs|fasting\s+glucose|sugar)\b"
        r"[^\d]{0,18}(\d{2,3})",
        (40, 600),
    ),
    "cholesterol": (
        r"\b(?:total\s+cholesterol|cholesterol|chol|tc)\b[^\d]{0,18}(\d{2,3})",
        (80, 500),
    ),
    "systolic_bp": (
        r"\b(?:blood\s+pressure|bp|systolic)\b[^\d]{0,12}(\d{2,3})(?:\s*/\s*\d{2,3})?",
        (60, 260),
    ),
    "age": (r"\bage\b[^\d]{0,8}(\d{1,3})", (1, 120)),
    "weight_kg": (r"\b(?:weight|wt)\b[^\d]{0,8}(\d{2,3})", (10, 400)),
    "height_cm": (r"\b(?:height|ht)\b[^\d]{0,8}(\d{2,3})", (50, 250)),
}


def parse_lab_values(text: str) -> dict[str, float]:
    """Return a dict of recognised {field: value} from raw report text."""
    found: dict[str, float] = {}
    flat = re.sub(r"\s+", " ", text).lower()
    for field, (pattern, (lo, hi)) in PATTERNS.items():
        match = re.search(pattern, flat, flags=re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
            except (ValueError, IndexError):
                continue
            if lo <= value <= hi:
                found[field] = value
    return found


def scan_report(path: str) -> dict[str, float]:
    """High-level entry point: extract text then parse known fields."""
    text = extract_text(path)
    if not text.strip():
        raise OCRUnavailable(
            "No readable text found. If this is a scanned image inside a PDF, "
            "try exporting it as a PNG/JPG and scanning that instead."
        )
    return parse_lab_values(text)
