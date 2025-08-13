\
import streamlit as st
import json, os, io
from utils.parse_procedure_text import extract_text_from_file
from utils.checklist_loader import load_all_checklists, pick_checklist
from utils.gemini_api import call_gemini_json
from utils.pcs_validator import quick_validate_code_structure, normalize_components

st.set_page_config(page_title="PCS Code Generator", layout="wide")

st.title("ICD-10-PCS Code Generator (Deterministic)")
st.caption("Analyzes a procedure note, applies the best-matched checklist, and returns structured PCS codes or CDI queries.")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Gemini Model", ["gemini-2.0-flash", "gemini-2.0-flash-lite"], index=0)
    determinism_help = st.checkbox("Extra Strict Determinism", value=True, help="Adds an additional instruction to avoid guesswork.")
    show_debug = st.checkbox("Show Debug", value=False)

# Secrets
try:
    GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
except Exception:
    GEMINI_API_KEY = None

if not GEMINI_API_KEY:
    st.warning("Set your Gemini key in Streamlit secrets as:\n\n[gemini]\napi_key = \"YOUR_KEY\"\n")
    st.stop()

# Load prompts and schema
SYSTEM_PROMPT = open("prompts/system_prompt.md", "r", encoding="utf-8").read()
USER_TMPL = open("prompts/user_prompt_template.md", "r", encoding="utf-8").read()
SCHEMA = json.load(open("prompts/schema.json", "r", encoding="utf-8"))

if determinism_help:
    SYSTEM_PROMPT += "\n\nAdditional constraint: If any doubt remains for any axis (body part/device/qualifier/approach), do not output a code for that path; create a query opportunity instead.\n"

# Load checklists
CHECKLISTS = load_all_checklists("checklists")

st.subheader("1) Upload Procedure Note (PDF or .txt)")
uploaded = st.file_uploader("Upload", type=["pdf","txt"])

if uploaded:
    text, src = extract_text_from_file(uploaded)
    with st.expander("Preview extracted text"):
        st.write(src)
        st.text_area("Extracted Text", value=text, height=240)

    st.subheader("2) Checklist Selection")
    best_name, best_text, ties = pick_checklist(text, CHECKLISTS)

    if len(ties) > 1:
        st.info(f"Multiple checklists matched: {', '.join(ties)}. Please confirm.")
    chosen = st.selectbox("Checklist", options=list(CHECKLISTS.keys()), index=list(CHECKLISTS.keys()).index(best_name))

    rules_md = CHECKLISTS[chosen]

    if st.button("Analyze with Gemini", type="primary"):
        # Build user prompt
        user_prompt = USER_TMPL.format(
            procedure_text=text,
            checklist_name=chosen,
            checklist_rules=rules_md
        )

        try:
            result = call_gemini_json(
                api_key=GEMINI_API_KEY,
                model=model,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=SCHEMA
            )
        except Exception as e:
            st.error(f"Gemini error: {e}")
            st.stop()

        # Validate & display
        st.subheader("3) Results")
        # Pretty JSON
        st.json(result)

        # Render Codes table
        codes = result.get("codes") or []
        if codes:
            st.markdown("#### Suggested ICD-10-PCS Codes")
            for idx, c in enumerate(codes, start=1):
                pcs = (c.get("pcs_code") or "").strip()
                valid = quick_validate_code_structure(pcs)
                components = normalize_components(c.get("components") or {})
                with st.container(border=True):
                    st.write(f"**#{idx}** — `{pcs}` {'✅' if valid else '⚠️ invalid format'}  | confidence={c.get('confidence')}")
                    st.write(c.get("explanation") or "")
                    st.write("Components:", components)

        # Render Query Opportunities
        qops = result.get("query_opportunities") or []
        if qops:
            st.markdown("#### CDI Query Opportunities")
            for q in qops:
                with st.container(border=True):
                    st.write(f"**{q.get('title','Query')}**")
                    st.write(q.get("reason",""))
                    st.code(q.get("suggested_query_text",""), language="markdown")

        st.caption(f"Checklist used: {result.get('checklist_used')}")
        if show_debug:
            st.write("Determinism note:", result.get("determinism_note"))

else:
    st.info("Upload a PDF or TXT to begin.")
