"""Lightweight rule-based healthcare assistant.

Intentionally conservative: provides general wellness guidance and awareness,
and NEVER diagnoses. Designed to be swappable for an LLM backend later.
"""
from __future__ import annotations

DISCLAIMER = (
    "I'm an AI assistant for general health awareness — not a doctor. "
    "For diagnosis, treatment, or emergencies, contact a qualified professional "
    "or your local emergency number."
)

EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cant breathe", "unconscious", "stroke",
    "severe bleeding", "suicide", "heart attack",
]

KNOWLEDGE = {
    ("diabetes", "sugar", "glucose"): (
        "Type 2 diabetes is strongly linked to lifestyle. Maintaining a healthy weight, "
        "exercising regularly, limiting refined sugar, and eating fibre-rich foods help "
        "keep blood sugar in check. Regular fasting-glucose checks are wise if you have "
        "risk factors."
    ),
    ("blood pressure", "hypertension", "bp"): (
        "To support healthy blood pressure: reduce salt, stay active, manage stress, "
        "limit alcohol, and monitor your readings. Persistently high readings should be "
        "discussed with a physician."
    ),
    ("heart", "cardiac", "cholesterol"): (
        "Heart health benefits from regular activity, a diet low in saturated/trans fats, "
        "not smoking, and managing blood pressure, sugar, and cholesterol."
    ),
    ("kidney", "renal"): (
        "Protect kidney health by controlling blood pressure and blood sugar, staying "
        "hydrated, and avoiding excessive painkillers. Regular screening helps catch issues early."
    ),
    ("sleep", "insomnia"): (
        "Aim for 7–8 hours nightly. Keep a consistent schedule, limit screens before bed, "
        "and avoid caffeine late in the day."
    ),
    ("stress", "anxiety"): (
        "Chronic stress affects your heart and metabolism. Try breathing exercises, regular "
        "movement, social connection, and breaks. Seek support if it feels overwhelming."
    ),
    ("diet", "food", "nutrition", "eat"): (
        "A balanced plate — half vegetables/fruit, a quarter whole grains, a quarter lean "
        "protein — supports overall health. Limit ultra-processed foods and sugary drinks."
    ),
    ("exercise", "workout", "activity"): (
        "Target at least 150 minutes of moderate activity weekly, plus strength work twice "
        "a week. Even short daily walks make a difference."
    ),
    ("smoking", "smoke", "cigarette"): (
        "Quitting smoking is one of the most impactful things you can do — cardiovascular "
        "risk starts dropping within weeks. Support lines and nicotine-replacement options can help."
    ),
    ("medicine reminder", "reminder", "medication"): (
        "For medication reminders, set phone alarms or use a pill organizer, and tie doses "
        "to daily routines (e.g. brushing teeth). Always follow your prescriber's instructions."
    ),
}

SUGGESTIONS = [
    "How can I lower my diabetes risk?",
    "What foods are good for heart health?",
    "How much exercise do I need weekly?",
    "Tips to manage stress",
]


def get_reply(message: str) -> dict:
    text = message.lower().strip()

    if any(kw in text for kw in EMERGENCY_KEYWORDS):
        return {
            "reply": (
                "⚠️ This may be a medical emergency. Please call your local emergency number "
                "or go to the nearest emergency department immediately. I cannot provide "
                "emergency medical care."
            ),
            "disclaimer": DISCLAIMER,
            "suggestions": [],
        }

    for keywords, answer in KNOWLEDGE.items():
        if any(kw in text for kw in keywords):
            return {"reply": answer, "disclaimer": DISCLAIMER, "suggestions": SUGGESTIONS}

    return {
        "reply": (
            "I can share general guidance on lifestyle, nutrition, exercise, sleep, stress, "
            "and NCD awareness (diabetes, hypertension, heart and kidney health). What would "
            "you like to know? Remember, I never diagnose conditions."
        ),
        "disclaimer": DISCLAIMER,
        "suggestions": SUGGESTIONS,
    }
