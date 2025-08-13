\
from __future__ import annotations
import re
from typing import Dict, Any

PCS_CODE_RE = re.compile(r"^[0-9A-HJ-NP-Z]{7}$")

def quick_validate_code_structure(code: str) -> bool:
    """
    Minimal syntactic validation for a 7-character ICD-10-PCS code.
    Excludes I and O letters per PCS convention.
    """
    return bool(PCS_CODE_RE.match(code or ""))

def normalize_components(c: Dict[str,Any]) -> Dict[str,Any]:
    return {
        "section": (c.get("section") or "").strip(),
        "body_system": (c.get("body_system") or "").strip(),
        "root_operation": (c.get("root_operation") or "").strip(),
        "body_part": (c.get("body_part") or "").strip(),
        "approach": (c.get("approach") or "").strip(),
        "device": (c.get("device") or "").strip(),
        "qualifier": (c.get("qualifier") or "").strip(),
    }
