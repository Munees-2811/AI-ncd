"""Healthcare assistant for the Health Assistant feature.

Tries the optional Claude backend first (when ANTHROPIC_API_KEY is set), then
falls back to a robust rule-based responder. The responder handles greetings,
thanks, capability questions, a broad set of health topics, English + Tamil,
and — importantly — distinguishes a real emergency from a *prevention/awareness*
question about an emergency topic (so "how do I prevent a heart attack?" is
answered helpfully instead of triggering the emergency notice).

It NEVER diagnoses.
"""
from __future__ import annotations

from app.services.llm import health_chat

DISCLAIMER = {
    "en": (
        "I'm an AI assistant for general health awareness — not a doctor. "
        "For diagnosis, treatment, or emergencies, contact a qualified professional "
        "or your local emergency number."
    ),
    "ta": (
        "நான் பொது சுகாதார விழிப்புணர்வுக்கான AI உதவியாளர் — மருத்துவர் அல்ல. "
        "நோயறிதல், சிகிச்சை அல்லது அவசரநிலைகளுக்கு தகுதியான மருத்துவரை அல்லது "
        "உங்கள் அவசர எண்ணை தொடர்பு கொள்ளவும்."
    ),
}

SUGGESTIONS = {
    "en": [
        "How can I lower my diabetes risk?",
        "What foods are good for heart health?",
        "How much exercise do I need weekly?",
        "Tips to manage stress",
    ],
    "ta": [
        "நீரிழிவு ஆபத்தை எப்படி குறைப்பது?",
        "இதய ஆரோக்கியத்திற்கு நல்ல உணவுகள் எவை?",
        "வாரத்திற்கு எவ்வளவு உடற்பயிற்சி தேவை?",
        "மன அழுத்தத்தை நிர்வகிக்க உதவிக்குறிப்புகள்",
    ],
}

# Phrases that indicate an ACTIVE emergency.
EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cant breathe", "can not breathe", "unconscious",
    "severe bleeding", "bleeding heavily", "suicide", "kill myself", "want to die",
    "overdose", "heart attack", "stroke", "seizure", "choking",
]

# If any of these appear, the message is about awareness/prevention, NOT an
# active emergency — so we should answer the question rather than alarm.
NON_EMERGENCY_CONTEXT = [
    "prevent", "prevention", "avoid", "reduce", "lower", "risk", "symptom", "sign",
    "what is", "what are", "what causes", "cause", "how to", "how do", "how can",
    "tips", "manage", "diet", "exercise", "about", "info", "learn", "understand",
    "difference", "vs", "recover", "after",
]

GREETINGS = {
    "hi", "hii", "hiii", "hello", "helo", "hey", "heya", "hiya", "yo", "howdy",
    "good morning", "good afternoon", "good evening", "vanakkam", "வணக்கம்", "ஹலோ",
}
THANKS = ["thank", "thanks", "thx", "நன்றி"]
CAPABILITY = ["who are you", "what can you do", "what do you do", "help me", "how do you work",
              "what are you", "நீ யார்", "என்ன செய்வாய்"]


def _bilingual(en: str, ta: str) -> dict[str, str]:
    return {"en": en, "ta": ta}


# Each intent: (keywords incl. Tamil, {"en", "ta"} answer).
KNOWLEDGE: list[tuple[tuple[str, ...], dict[str, str]]] = [
    (("diabetes", "blood sugar", "sugar", "glucose", "நீரிழிவு", "சர்க்கரை"),
     _bilingual(
        "Type 2 diabetes is strongly linked to lifestyle. Maintaining a healthy weight, "
        "exercising regularly, limiting refined sugar, and eating fibre-rich foods help keep "
        "blood sugar in check. Regular fasting-glucose checks are wise if you have risk factors.",
        "டைப் 2 நீரிழிவு வாழ்க்கை முறையுடன் நெருங்கிய தொடர்புடையது. ஆரோக்கியமான எடை, "
        "வழக்கமான உடற்பயிற்சி, சர்க்கரையை குறைத்தல், நார்ச்சத்து நிறைந்த உணவு ஆகியவை இரத்த "
        "சர்க்கரையை கட்டுக்குள் வைக்க உதவும். ஆபத்து இருந்தால் வழக்கமான பரிசோதனை நல்லது.")),

    (("blood pressure", "hypertension", "bp", "இரத்த அழுத்தம்", "உயர் அழுத்தம்"),
     _bilingual(
        "To support healthy blood pressure: reduce salt, stay active, manage stress, limit "
        "alcohol, and monitor your readings. Persistently high readings should be discussed "
        "with a physician.",
        "ஆரோக்கியமான இரத்த அழுத்தத்திற்கு: உப்பை குறைக்கவும், சுறுசுறுப்பாக இருங்கள், மன "
        "அழுத்தத்தை நிர்வகிக்கவும், மது குறைக்கவும், அளவீடுகளை கண்காணிக்கவும். தொடர்ந்து அதிகமாக "
        "இருந்தால் மருத்துவரிடம் கலந்தாலோசிக்கவும்.")),

    (("heart", "cardiac", "cholesterol", "இதயம்", "கொலஸ்ட்ரால்"),
     _bilingual(
        "Heart health benefits from regular activity, a diet low in saturated/trans fats, not "
        "smoking, and managing blood pressure, sugar, and cholesterol. The Mediterranean-style "
        "diet (vegetables, whole grains, fish, olive oil) is heart-friendly.",
        "இதய ஆரோக்கியத்திற்கு வழக்கமான உடற்பயிற்சி, கொழுப்பு குறைந்த உணவு, புகைபிடிக்காமை, "
        "இரத்த அழுத்தம்/சர்க்கரை/கொலஸ்ட்ரால் கட்டுப்பாடு உதவும். காய்கறிகள், முழு தானியங்கள், மீன், "
        "ஆலிவ் எண்ணெய் கொண்ட உணவு இதயத்திற்கு நல்லது.")),

    (("kidney", "renal", "சிறுநீரகம்"),
     _bilingual(
        "Protect kidney health by controlling blood pressure and blood sugar, staying hydrated, "
        "and avoiding excessive painkillers. Regular screening helps catch issues early.",
        "சிறுநீரக ஆரோக்கியத்திற்கு இரத்த அழுத்தம் மற்றும் சர்க்கரையை கட்டுப்படுத்தவும், நீர்ச்சத்துடன் "
        "இருங்கள், அதிகப்படியான வலி நிவாரணிகளை தவிர்க்கவும். வழக்கமான பரிசோதனை முன்கூட்டியே "
        "பிரச்சினைகளை கண்டறிய உதவும்.")),

    (("sleep", "insomnia", "தூக்கம்"),
     _bilingual(
        "Aim for 7–8 hours nightly. Keep a consistent schedule, limit screens before bed, and "
        "avoid caffeine late in the day.",
        "இரவில் 7–8 மணி நேரம் தூங்க முயற்சிக்கவும். நிலையான நேரம், படுக்கைக்கு முன் திரைகளை "
        "குறைத்தல், மாலையில் காஃபின் தவிர்த்தல் உதவும்.")),

    (("stress", "anxiety", "மன அழுத்தம்", "கவலை"),
     _bilingual(
        "Chronic stress affects your heart and metabolism. Try breathing exercises, regular "
        "movement, social connection, and breaks. Seek support if it feels overwhelming.",
        "நீடித்த மன அழுத்தம் இதயம் மற்றும் வளர்சிதை மாற்றத்தை பாதிக்கும். மூச்சுப் பயிற்சி, "
        "வழக்கமான நடவடிக்கை, சமூக தொடர்பு, இடைவேளைகள் முயற்சிக்கவும். தேவைப்பட்டால் ஆதரவு பெறவும்.")),

    (("diet", "food", "nutrition", "eat", "fruit", "vegetable", "உணவு", "ஊட்டச்சத்து"),
     _bilingual(
        "A balanced plate — half vegetables/fruit, a quarter whole grains, a quarter lean "
        "protein — supports overall health. Limit ultra-processed foods and sugary drinks.",
        "சமச்சீர் தட்டு — பாதி காய்கறி/பழம், கால் பகுதி முழு தானியம், கால் பகுதி புரதம் — ஒட்டுமொத்த "
        "ஆரோக்கியத்திற்கு உதவும். பதப்படுத்தப்பட்ட உணவு, இனிப்பு பானங்களை குறைக்கவும்.")),

    (("exercise", "workout", "activity", "walk", "உடற்பயிற்சி", "நடைபயிற்சி"),
     _bilingual(
        "Target at least 150 minutes of moderate activity weekly, plus strength work twice a "
        "week. Even short daily walks make a difference.",
        "வாரத்திற்கு குறைந்தது 150 நிமிட மிதமான உடற்பயிற்சி, வாரம் இருமுறை வலிமை பயிற்சி "
        "செய்யுங்கள். குறுகிய தினசரி நடைபயிற்சி கூட பயன் தரும்.")),

    (("smoking", "smoke", "cigarette", "tobacco", "புகை", "புகைபிடித்தல்"),
     _bilingual(
        "Quitting smoking is one of the most impactful things you can do — cardiovascular risk "
        "starts dropping within weeks. Support lines and nicotine-replacement options can help.",
        "புகைபிடிப்பதை நிறுத்துவது மிகவும் பயனுள்ள ஒன்று — சில வாரங்களில் இதய ஆபத்து குறையத் "
        "தொடங்கும். ஆதரவு சேவைகள் மற்றும் நிகோடின் மாற்று வழிகள் உதவும்.")),

    (("alcohol", "beer", "wine", "liquor", "மது"),
     _bilingual(
        "Keep alcohol within recommended limits, or abstain. Excess alcohol raises blood "
        "pressure and harms the liver and heart over time.",
        "மதுவை பரிந்துரைக்கப்பட்ட அளவுக்குள் வைக்கவும் அல்லது தவிர்க்கவும். அதிகப்படியான மது "
        "இரத்த அழுத்தத்தை உயர்த்தி, கல்லீரல் மற்றும் இதயத்தை பாதிக்கும்.")),

    (("weight", "obesity", "bmi", "lose weight", "எடை", "உடல்பருமன்"),
     _bilingual(
        "A gradual, sustainable approach works best — combine a balanced diet with regular "
        "activity. Even a 5–10% weight reduction meaningfully lowers NCD risk.",
        "படிப்படியான, நிலையான அணுகுமுறை சிறந்தது — சமச்சீர் உணவையும் வழக்கமான உடற்பயிற்சியையும் "
        "இணைக்கவும். 5–10% எடை குறைப்பு கூட நோய் ஆபத்தை கணிசமாக குறைக்கும்.")),

    (("water", "hydration", "drink water", "தண்ணீர்", "நீர்ச்சத்து"),
     _bilingual(
        "Most adults do well with around 6–8 glasses of fluid a day, more in heat or with "
        "exercise. Water is the best default; limit sugary and energy drinks.",
        "பெரும்பாலான பெரியவர்களுக்கு ஒரு நாளைக்கு சுமார் 6–8 கிளாஸ் திரவம் போதும், வெப்பம்/"
        "உடற்பயிற்சியின் போது அதிகம். தண்ணீரே சிறந்தது; இனிப்பு பானங்களை குறைக்கவும்.")),

    (("caffeine", "coffee", "tea", "காபி", "தேநீர்"),
     _bilingual(
        "Moderate caffeine (about 1–3 cups of coffee a day) is fine for most adults. Avoid it "
        "late in the day if it affects your sleep, and cut back if it makes you jittery.",
        "மிதமான காஃபின் (நாளைக்கு சுமார் 1–3 கப் காபி) பெரும்பாலானோருக்கு பரவாயில்லை. தூக்கத்தை "
        "பாதித்தால் மாலையில் தவிர்க்கவும்.")),

    (("medicine reminder", "reminder", "medication", "pills", "மருந்து நினைவூட்டல்"),
     _bilingual(
        "For medication reminders, set phone alarms or use a pill organizer, and tie doses to "
        "daily routines (e.g. brushing teeth). Always follow your prescriber's instructions.",
        "மருந்து நினைவூட்டலுக்கு தொலைபேசி அலாரம் அல்லது மாத்திரை பெட்டியை பயன்படுத்தவும், "
        "தினசரி வழக்கங்களுடன் இணைக்கவும். எப்போதும் மருத்துவரின் அறிவுறுத்தலை பின்பற்றவும்.")),
]


def _is_active_emergency(text: str) -> bool:
    if not any(kw in text for kw in EMERGENCY_KEYWORDS):
        return False
    # An emergency keyword in an awareness/prevention question is informational.
    return not any(ctx in text for ctx in NON_EMERGENCY_CONTEXT)


def _emergency_reply(locale: str) -> dict:
    reply = {
        "en": (
            "⚠️ This may be a medical emergency. Please call your local emergency number or go "
            "to the nearest emergency department immediately. I can't provide emergency care."
        ),
        "ta": (
            "⚠️ இது மருத்துவ அவசரநிலையாக இருக்கலாம். உடனடியாக உங்கள் அவசர எண்ணை அழைக்கவும் "
            "அல்லது அருகிலுள்ள அவசர சிகிச்சைப் பிரிவுக்கு செல்லவும். நான் அவசர சிகிச்சை வழங்க முடியாது."
        ),
    }
    return {"reply": reply.get(locale, reply["en"]), "disclaimer": DISCLAIMER.get(locale, DISCLAIMER["en"]),
            "suggestions": []}


def _pick(locale: str, mapping: dict[str, str]) -> str:
    return mapping.get(locale, mapping["en"])


def get_reply(message: str, locale: str = "en") -> dict:
    locale = locale if locale in ("en", "ta") else "en"
    text = message.lower().strip()
    disclaimer = DISCLAIMER[locale]
    suggestions = SUGGESTIONS[locale]

    # 1. Active emergencies always short-circuit (rules only — never an LLM).
    if _is_active_emergency(text):
        return _emergency_reply(locale)

    # 2. Greetings / thanks / capabilities — handled directly for a natural feel.
    if text in GREETINGS or any(text.startswith(g + " ") for g in GREETINGS):
        return {"reply": _pick(locale, _bilingual(
            "Hi! 👋 I'm your Health Assistant. Ask me about nutrition, exercise, sleep, stress, "
            "or NCD awareness (diabetes, blood pressure, heart and kidney health). I never diagnose.",
            "வணக்கம்! 👋 நான் உங்கள் சுகாதார உதவியாளர். ஊட்டச்சத்து, உடற்பயிற்சி, தூக்கம், மன அழுத்தம், "
            "அல்லது நோய் விழிப்புணர்வு பற்றி கேளுங்கள். நான் நோயறிதல் செய்வதில்லை.")),
            "disclaimer": disclaimer, "suggestions": suggestions}

    if any(t in text for t in THANKS):
        return {"reply": _pick(locale, _bilingual(
            "You're welcome! 😊 Is there anything else about your health and lifestyle I can help with?",
            "வரவேற்கிறேன்! 😊 உங்கள் ஆரோக்கியம் மற்றும் வாழ்க்கை முறை குறித்து வேறு ஏதேனும் உதவ முடியுமா?")),
            "disclaimer": disclaimer, "suggestions": suggestions}

    if any(c in text for c in CAPABILITY):
        return {"reply": _pick(locale, _bilingual(
            "I share general guidance on lifestyle, nutrition, exercise, sleep, stress, and NCD "
            "awareness — diabetes, hypertension, heart and kidney health. I can also suggest "
            "medication-reminder habits. I never diagnose conditions or prescribe medicine.",
            "வாழ்க்கை முறை, ஊட்டச்சத்து, உடற்பயிற்சி, தூக்கம், மன அழுத்தம், மற்றும் நோய் விழிப்புணர்வு "
            "குறித்து பொதுவான வழிகாட்டுதல் வழங்குகிறேன். நான் நோயறிதல் செய்வதில்லை.")),
            "disclaimer": disclaimer, "suggestions": suggestions}

    # 3. Optional Claude backend for natural, multilingual answers.
    llm_reply = health_chat(message, locale)
    if llm_reply:
        return {"reply": llm_reply, "disclaimer": disclaimer, "suggestions": suggestions}

    # 4. Rule-based knowledge match.
    for keywords, answer in KNOWLEDGE:
        if any(kw in text for kw in keywords):
            return {"reply": answer[locale], "disclaimer": disclaimer, "suggestions": suggestions}

    # 5. Friendly fallback.
    return {"reply": _pick(locale, _bilingual(
        "I can share general guidance on lifestyle, nutrition, exercise, sleep, stress, and NCD "
        "awareness (diabetes, hypertension, heart and kidney health). What would you like to "
        "know? Remember, I never diagnose conditions.",
        "வாழ்க்கை முறை, ஊட்டச்சத்து, உடற்பயிற்சி, தூக்கம், மன அழுத்தம், மற்றும் நோய் விழிப்புணர்வு "
        "(நீரிழிவு, உயர் இரத்த அழுத்தம், இதயம், சிறுநீரகம்) குறித்து பொதுவான வழிகாட்டுதல் வழங்க முடியும். "
        "என்ன அறிய விரும்புகிறீர்கள்? நான் நோயறிதல் செய்வதில்லை.")),
        "disclaimer": disclaimer, "suggestions": suggestions}
