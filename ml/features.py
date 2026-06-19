"""Shared feature configuration used by both the training pipeline and the
backend inference service so the two never drift apart."""

NUMERIC_FEATURES = [
    "age",
    "height_cm",
    "weight_kg",
    "bmi",
    "systolic_bp",
    "blood_sugar",
    "cholesterol",
    "exercise_freq",
    "sleep_hours",
]

BINARY_FEATURES = ["smoking", "alcohol", "family_history"]

CATEGORICAL_FEATURES = ["gender", "stress_level"]

# Order of all engineered columns AFTER encoding (filled in at fit time and
# persisted alongside the model so inference can rebuild the exact column order).
TARGET = "risk"

RISK_LABELS = {0: "Low Risk", 1: "Moderate Risk", 2: "High Risk"}
