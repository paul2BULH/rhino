\
from __future__ import annotations
import json
from typing import Dict, Any, Optional

# Try both modern and legacy SDK names to maximize deploy compatibility.
def _get_gemini_client(api_key: str):
    try:
        import google.genai as genai  # modern SDK
        client = genai.Client(api_key=api_key)
        return client, "genai"
    except Exception:
        try:
            import google.generativeai as genai_old  # legacy SDK
            genai_old.configure(api_key=api_key)
            return genai_old, "generativeai"
        except Exception as e:
            raise RuntimeError("Unable to import Gemini SDK. Install google-genai or google-generativeai.") from e

def call_gemini_json(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    schema: Dict[str, Any],
    timeout: int = 60
) -> Dict[str, Any]:
    client, flavor = _get_gemini_client(api_key)

    # Force deterministic settings
    generation_config = {
        "temperature": 0.0,
        "top_p": 1.0,
        "top_k": 1,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
        "response_schema": schema
    }

    if flavor == "genai":
        # New SDK
        resp = client.models.generate_content(
            model=model,
            contents=[
                {"role": "system", "parts": [{"text": system_prompt}]},
                {"role": "user", "parts": [{"text": user_prompt}]},
            ],
            config=generation_config,
        )
        # The SDK returns a dict-like object with .text possibly empty since mime is JSON.
        text = getattr(resp, "text", None)
        if not text:
            # Try candidates
            cands = getattr(resp, "candidates", None)
            if cands and len(cands) and hasattr(cands[0], "content"):
                parts = getattr(cands[0].content, "parts", []) or []
                text = "".join([getattr(p, "text", "") or "" for p in parts])
        if not text:
            raise RuntimeError("Gemini returned empty response.")
        return json.loads(text)

    else:
        # Legacy SDK
        model_obj = client.GenerativeModel(model_name=model,
                                           generation_config={
                                               "temperature": 0.0,
                                               "top_p": 1.0,
                                               "top_k": 1,
                                               "max_output_tokens": 2048,
                                               "response_mime_type": "application/json"
                                           })
        # system instruction supported via 'system_instruction' in some versions; fallback to prepend
        prompt = f"{system_prompt}\n\n{user_prompt}"
        resp = model_obj.generate_content(prompt, request_options={"timeout": timeout})
        text = resp.text
        if not text:
            # Try candidate parts
            if hasattr(resp, "candidates") and resp.candidates:
                parts = getattr(resp.candidates[0].content, "parts", []) or []
                text = "".join([getattr(p, "text", "") or "" for p in parts])
        if not text:
            raise RuntimeError("Gemini returned empty response.")
        return json.loads(text)
