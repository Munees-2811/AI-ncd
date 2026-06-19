"""Rule-based personalized recommendation engine.

Turns the user's inputs + predicted risk into prioritized, actionable guidance.
"""
from __future__ import annotations


def generate_recommendations(data: dict, risk_class: int) -> list[dict]:
    recs: list[dict] = []

    def add(category, title, detail, priority):
        recs.append(
            {"category": category, "title": title, "detail": detail, "priority": priority}
        )

    bmi = data["bmi"]
    if bmi >= 30:
        add("Weight", "Work toward a healthier weight",
            "Your BMI is in the obese range. A 5–10% weight reduction meaningfully lowers NCD risk.",
            "high")
    elif bmi >= 25:
        add("Weight", "Trim a few kilograms",
            "Your BMI is in the overweight range. Aim for gradual, sustainable weight loss.",
            "medium")
    elif bmi < 18.5:
        add("Weight", "Address being underweight",
            "Your BMI is low. Consider a balanced calorie-sufficient diet and a check-up.",
            "medium")

    if data["systolic_bp"] >= 140:
        add("Blood Pressure", "Manage high blood pressure",
            "Reduce salt intake, monitor BP regularly, and discuss management with a physician.",
            "high")
    elif data["systolic_bp"] >= 130:
        add("Blood Pressure", "Watch your blood pressure",
            "You are in the elevated range. Lifestyle changes now can prevent hypertension.",
            "medium")

    if data["blood_sugar"] >= 126:
        add("Blood Sugar", "Address elevated blood sugar",
            "Your fasting blood sugar is in the diabetic range. Please consult a physician promptly.",
            "high")
    elif data["blood_sugar"] >= 100:
        add("Blood Sugar", "Reduce sugar intake",
            "Pre-diabetic range detected. Cut refined sugar and increase fibre and activity.",
            "medium")

    if data["cholesterol"] >= 240:
        add("Cholesterol", "Lower your cholesterol",
            "High cholesterol raises heart-disease risk. Favor unsaturated fats and fibre.",
            "high")
    elif data["cholesterol"] >= 200:
        add("Cholesterol", "Improve your lipid profile",
            "Borderline-high cholesterol. Reduce fried/processed foods.",
            "medium")

    if data["smoking"]:
        add("Smoking", "Stop smoking",
            "Smoking is a leading driver of NCDs. Quitting rapidly reduces cardiovascular risk.",
            "high")
    if data["alcohol"]:
        add("Alcohol", "Limit alcohol consumption",
            "Keep alcohol within recommended limits, or abstain, to protect your liver and heart.",
            "medium")

    if data["exercise_freq"] < 3:
        add("Exercise", "Increase physical activity",
            "Aim for at least 150 minutes of moderate exercise per week (≈5 days).",
            "high" if risk_class == 2 else "medium")

    if abs(data["sleep_hours"] - 7.5) > 1.5:
        add("Sleep", "Improve your sleep",
            "Target 7–8 hours of quality sleep nightly to support metabolic health.",
            "medium")

    if data["stress_level"] == "high":
        add("Stress", "Manage stress levels",
            "Chronic stress affects blood pressure and sugar. Try mindfulness, breathing, or breaks.",
            "medium")

    add("Diet", "Eat a balanced diet",
        "Prioritize vegetables, whole grains, lean protein, and limit processed foods.",
        "low")

    if risk_class == 2:
        add("Medical", "Consult a physician soon",
            "Your screening indicates high risk. Please schedule a professional medical evaluation.",
            "high")
    elif risk_class == 1:
        add("Medical", "Consider a routine check-up",
            "A periodic health check-up is recommended to monitor your risk factors.",
            "medium")

    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order[r["priority"]])
    return recs
