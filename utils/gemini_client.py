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
    kwargs = {"model_name": "gemini-2.5-flash-preview-04-17"}
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
