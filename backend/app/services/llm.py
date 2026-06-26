"""
Optional LLM backend for the Health Assistant.

If an ANTHROPIC_API_KEY is configured (and the `anthropic` SDK is installed),
the assistant answers via Claude for natural, multilingual conversation. When
no key is present, the import fails, or the call errors, this returns None and
the caller falls back to the built-in rule-based responder — so the assistant
always works, online or offline, with or without a key.

This module is intentionally self-contained and side-effect free on import.
"""
from __future__ import annotations

import os

# Latest, most capable Claude model for healthcare conversation.
_MODEL = "claude-opus-4-8"

_SYSTEM = {
    "en": (
        "You are NCD Shield AI's Health Assistant — a friendly assistant for GENERAL "
        "health awareness and lifestyle guidance (nutrition, exercise, sleep, stress, and "
        "Non-Communicable Disease awareness: diabetes, hypertension, heart and kidney health).\n"
        "Rules you MUST follow:\n"
        "- NEVER diagnose, name a specific condition the user has, prescribe medication, or "
        "give specific dosages. You are not a doctor.\n"
        "- Keep replies concise (2-5 sentences), warm, and practical.\n"
        "- For anything urgent (chest pain, trouble breathing, stroke signs, self-harm), tell "
        "the user to contact emergency services immediately.\n"
        "- Encourage consulting a qualified healthcare professional for personal medical concerns.\n"
        "- Answer in clear English."
    ),
    "ta": (
        "நீங்கள் NCD Shield AI இன் சுகாதார உதவியாளர் — பொது சுகாதார விழிப்புணர்வு மற்றும் வாழ்க்கை "
        "முறை வழிகாட்டுதலுக்கான நட்பு உதவியாளர் (ஊட்டச்சத்து, உடற்பயிற்சி, தூக்கம், மன அழுத்தம், "
        "மற்றும் தொற்றா நோய்கள் பற்றிய விழிப்புணர்வு: நீரிழிவு, உயர் இரத்த அழுத்தம், இதயம், சிறுநீரகம்).\n"
        "நீங்கள் கடைபிடிக்க வேண்டிய விதிகள்:\n"
        "- ஒருபோதும் நோயறிதல் செய்யாதீர்கள், மருந்து பரிந்துரைக்காதீர்கள். நீங்கள் மருத்துவர் அல்ல.\n"
        "- பதில்களை சுருக்கமாகவும் (2-5 வாக்கியங்கள்) நடைமுறைக்கு ஏற்றதாகவும் வைக்கவும்.\n"
        "- அவசர அறிகுறிகளுக்கு (மார்பு வலி, மூச்சுத் திணறல்) உடனடியாக அவசர சேவையை அணுகச் சொல்லுங்கள்.\n"
        "- தனிப்பட்ட மருத்துவ கவலைகளுக்கு தகுதியான மருத்துவரை அணுகுமாறு ஊக்குவிக்கவும்.\n"
        "- தமிழில் தெளிவாக பதிலளிக்கவும்."
    ),
}


def health_chat(message: str, locale: str = "en") -> str | None:
    """Return a Claude-generated reply, or None to signal fallback."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # imported lazily so the SDK is an optional dependency
    except ImportError:
        return None

    system = _SYSTEM.get(locale, _SYSTEM["en"])
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=_MODEL,
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": message}],
        )
        # A safety refusal arrives as a 200 with stop_reason == "refusal".
        if getattr(response, "stop_reason", None) == "refusal":
            return None
        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
        return text or None
    except Exception:  # noqa: BLE001 — any failure → graceful fallback
        return None
