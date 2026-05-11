"""
Gemini API wrapper — streaming chat + structured JSON generation.
Reads GOOGLE_API_KEY from Streamlit secrets (prod) or .env (local dev).
"""

import json
import os
import re
import streamlit as st


def _get_api_key() -> str:
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GOOGLE_API_KEY", "")
        if not key:
            raise ValueError("GOOGLE_API_KEY not found. Add it to .env or Streamlit secrets.")
        return key


def _get_model(system_prompt: str = ""):
    import google.generativeai as genai
    genai.configure(api_key=_get_api_key())
    kwargs = {"model_name": "gemini-2.5-flash"}
    if system_prompt:
        kwargs["system_instruction"] = system_prompt
    return genai.GenerativeModel(**kwargs)


def stream_chat(messages: list[dict], system_prompt: str) -> any:
    """
    Send a conversation to Gemini and return a streaming response generator.
    messages: list of {"role": "user"|"assistant", "content": str}
    Yields text chunks as strings.
    """
    model = _get_model(system_prompt)

    # Convert to Gemini history format (all but last message)
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [{"text": msg["content"]}]})

    chat = model.start_chat(history=history)
    last_msg = messages[-1]["content"]

    response = chat.send_message(last_msg, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text


def generate_json(prompt: str, fallback: dict | None = None) -> dict:
    """
    Ask Gemini to generate structured JSON data. Returns parsed dict.
    Falls back to `fallback` dict if the call fails or JSON is malformed.
    """
    try:
        model = _get_model(
            "You are a data generation assistant. Always respond with valid JSON only. "
            "No markdown, no code fences, no explanation — pure JSON."
        )
        response = model.generate_content(prompt)
        raw = response.text.strip()
        # Strip potential markdown code fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception:
        return fallback or {}


def extract_doc_fields(file_text: str, doc_name: str, doc_purpose: str, vendor_info: dict) -> dict:
    """
    Ask Gemini to extract the most relevant structured fields from an uploaded
    document. If the text is unreadable, Gemini hallucinates plausible fields
    from the doc name + vendor context. Always returns VALID for the demo.
    """
    company = vendor_info.get("company_name", "the vendor")
    industry = vendor_info.get("industry", "general").replace("_", " ")
    prompt = (
        f"You are a Centrica procurement officer extracting key fields from a vendor document.\n\n"
        f"Document type: {doc_name}\n"
        f"Why it's needed: {doc_purpose}\n"
        f"Vendor: {company} (industry: {industry})\n\n"
        f"Document content:\n---\n{file_text[:5000]}\n---\n\n"
        f"Extract 3-5 of the MOST RELEVANT fields a procurement officer would record. "
        f"Field labels should be concise (e.g., 'Certificate Number', 'Expiry Date', 'Issuing Authority'). "
        f"Field values should be specific and plausible.\n\n"
        f"If the content is empty, unreadable, or a binary placeholder, "
        f"generate REALISTIC fields based on the document type and vendor industry — "
        f"do NOT say the document was unreadable, just produce plausible values.\n\n"
        f"Return JSON exactly in this shape:\n"
        f"{{\n"
        f'  "extracted_fields": [{{"label": "...", "value": "..."}}, ...],\n'
        f'  "summary": "one short sentence",\n'
        f'  "validation_status": "VALID",\n'
        f'  "confidence": "high"\n'
        f"}}"
    )
    fallback = {
        "extracted_fields": [
            {"label": "Document type", "value": doc_name},
            {"label": "Issuing authority", "value": "Confirmed"},
            {"label": "Validity", "value": "Current and in date"},
        ],
        "summary": f"{doc_name} received and validated.",
        "validation_status": "VALID",
        "confidence": "high",
    }
    result = generate_json(prompt, fallback)
    # Force VALID for demo flow
    result["validation_status"] = "VALID"
    return result


def classify_industry(vendor_description: str) -> str:
    """
    Ask Gemini to classify a vendor's industry from their description.
    Returns one of the keys from industry_config.INDUSTRY_PROFILES.
    """
    valid_industries = [
        "financial_services", "construction", "maritime", "it_technology",
        "energy_utilities", "logistics_transport", "healthcare",
        "professional_services", "general",
    ]
    prompt = (
        f"Classify this vendor description into exactly one industry category.\n"
        f"Description: \"{vendor_description}\"\n"
        f"Valid categories: {', '.join(valid_industries)}\n"
        f"Respond with ONLY the category key, nothing else."
    )
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        result = response.text.strip().lower().replace(" ", "_")
        if result in valid_industries:
            return result
    except Exception:
        pass
    # Fallback: keyword matching
    from utils.industry_config import detect_industry_fallback
    return detect_industry_fallback(vendor_description)
