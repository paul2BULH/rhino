\
from __future__ import annotations
import os, re
from typing import Dict, List, Tuple

def load_all_checklists(folder: str) -> Dict[str, str]:
    data = {}
    for fname in os.listdir(folder):
        if fname.lower().endswith(".md"):
            with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                data[os.path.splitext(fname)[0]] = f.read()
    return data

def pick_checklist(procedure_text: str, checklists: Dict[str,str]) -> Tuple[str, str, List[str]]:
    """
    Very simple heuristic: score by keyword frequency from **Trigger Terms** section.
    Returns (best_name, best_text, ties)
    """
    best, best_score, ties = None, -1, []
    for name, md in checklists.items():
        # Extract trigger terms line(s)
        m = re.search(r"\*\*Trigger Terms:\*\*(.+)", md)
        triggers = []
        if m:
            triggers = [t.strip().lower() for t in re.split(r",|;", m.group(1)) if t.strip()]
        score = 0
        lowered_note = procedure_text.lower()
        for t in triggers:
            if t and t in lowered_note:
                score += 1
        if score > best_score:
            best, best_score = name, score
            ties = [name]
        elif score == best_score:
            ties.append(name)
    if best is None:
        # fallback arbitrary
        best = list(checklists.keys())[0]
        ties = [best]
    return best, checklists[best], ties
