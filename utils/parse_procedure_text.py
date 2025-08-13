\
from __future__ import annotations
from typing import Tuple
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text.append(page.get_text("text"))
    return "\n".join(text).strip()

def extract_text_from_file(file) -> Tuple[str, str]:
    """
    Accepts a Streamlit UploadedFile or a filesystem path string.
    Returns (text, source_info).
    """
    if hasattr(file, "name"):  # Streamlit UploadedFile
        name = file.name.lower()
        if name.endswith(".pdf"):
            # Save temp then parse
            import tempfile, os
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            try:
                txt = extract_text_from_pdf(tmp_path)
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            return txt, f"PDF:{file.name}"
        else:
            raw = file.read().decode("utf-8", errors="ignore")
            return raw, f"TXT:{file.name}"
    else:
        # string path
        if str(file).lower().endswith(".pdf"):
            return extract_text_from_pdf(file), f"PDF:{file}"
        else:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), f"TXT:{file}"
