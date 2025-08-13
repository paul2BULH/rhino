Procedure Note (verbatim):
---
{procedure_text}
---

Checklist summary (selected = "{checklist_name}"):
---
{checklist_rules}
---

TASK:
1) Analyze the note using ICD-10-PCS rules.
2) Use ONLY the facts present or clearly implied by the note.
3) Apply the checklist strictly: inclusion/exclusion/edge cases.
4) If ANY required character (body part/device/approach/qualifier) is uncertain, DO NOT GUESS. 
   Add a "query_opportunities" item describing exactly what clarification is needed.
5) If a code is fully supported, output it with a short explanation and confidence.
6) Output JSON that validates against the provided schema. No extra keys.

Remember: you must be deterministic; do not vary outputs for the same inputs.
