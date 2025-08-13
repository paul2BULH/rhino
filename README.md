# ICD-10-PCS Code Generator (Deterministic, Streamlit)

This app analyzes an uploaded **procedure note** (PDF or .txt), selects the most appropriate **procedure checklist**, and calls **Gemini 2.0 Flash** to return **deterministic** ICD‑10‑PCS codes or CDI query opportunities in a strict JSON schema.

## Why deterministic?
- Temperature = 0.0, top_k = 1, top_p = 1.0
- System and user prompts enforce **no guessing**
- If any axis is missing (e.g., body part/approach/device/qualifier), the model must **not** output a code and instead produce a CDI **query opportunity**

---

## Project Structure

```
pcs_code_generator_streamlit/
├── streamlit_app.py
├── requirements.txt
├── prompts/
│   ├── schema.json
│   ├── system_prompt.md
│   └── user_prompt_template.md
├── utils/
│   ├── gemini_api.py
│   ├── parse_procedure_text.py
│   ├── checklist_loader.py
│   └── pcs_validator.py
├── checklists/
│   ├── Debridement.md
│   └── Cholecystectomy.md
└── .streamlit/
    └── secrets_template.toml
```

> Add more checklists as `checklists/*.md` (one file per procedure group). The app will auto‑load them.

---

## Local Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Secrets
Set your API key via Streamlit **secrets** (locally create `.streamlit/secrets.toml`):

```toml
[gemini]
api_key = "YOUR_GEMINI_API_KEY"
```

On **Streamlit Cloud**, open **Settings → Secrets** and paste the same TOML block.

### Model
Default: `gemini-2.0-flash`. You can switch to `gemini-2.0-flash-lite` in the sidebar.

---

## Deployment (Streamlit Cloud + GitHub)

1. Push this folder to a new GitHub repo (root must contain `streamlit_app.py` and `requirements.txt`).
2. In Streamlit Cloud: **New app** → point to the repo + main branch.
3. Set **Secrets**:
   ```toml
   [gemini]
   api_key = "YOUR_GEMINI_API_KEY"
   ```
4. Deploy.

---

## Extending Determinism

- Keep the **schema.json** strict and extend if needed; the app validates the JSON.
- Checklist authoring: prefer objective rules, explicit phrasing, and “query if missing” sections.
- Add more **Trigger Terms** lines to strengthen automatic checklist selection.
- Consider adding downstream validation with official ICD‑10‑PCS tables if you have the XML resources.

---

## Notes

- PDF text extraction uses **PyMuPDF**. If scanned PDFs are involved, add OCR (e.g., Tesseract) before analysis.
- The app includes a minimal code-format check (`quick_validate_code_structure`) but does not validate against official PCS tables.
