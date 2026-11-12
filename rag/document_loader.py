"""Read fixed PDF collections page by page, retaining document provenance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

DEFAULT_DOCUMENT_DIRS = (Path("documents/dgca"), Path("documents/airline"))
_SECTION_RE = re.compile(
    r"^\s*((?:section|chapter|article|rule|regulation)\s+[\w.()/-]+[^\n]*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def load_pdfs(
    directories: tuple[str | Path, ...] | list[str | Path] | None = None,
) -> list[dict[str, Any]]:
    """Extract non-empty PDF pages; page numbers are 1-based."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF loading requires pypdf; install requirements.txt") from exc

    roots = [Path(p) for p in directories] if directories is not None else list(DEFAULT_DOCUMENT_DIRS)
    pages: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for pdf_path in sorted(root.rglob("*.pdf")):
            reader = PdfReader(str(pdf_path))
            for page_number, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue
                headings = _SECTION_RE.findall(text)
                pages.append({
                    "text": text,
                    "source": pdf_path.name,
                    "page": page_number,
                    "section": headings[-1].strip() if headings else None,
                })
    return pages
