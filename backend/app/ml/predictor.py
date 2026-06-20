"""
Model inference service.

Loads the best trained pipeline + metadata produced by `ml/train.py`. If no model
artifact is found (e.g. fresh checkout before training), it transparently falls back
to a deterministic heuristic so the API remains fully functional for demos.
"""
from __future__ import annotations

import json
import os

import joblib
import numpy as np
import pandas as pd

from app.config import settings

RISK_LABELS = {0: "Low Risk", 1: "Moderate Risk", 2: "High Risk"}

# Human-friendly labels for raw + one-hot encoded feature names.
FEATURE_LABELS = {
    "num__age": "Age",
    "num__height_cm": "Height",
    "num__weight_kg": "Weight",
    "num__bmi": "Body Mass Index",
    "num__systolic_bp": "Blood Pressure",
    "num__blood_sugar": "Blood Sugar",
    "num__cholesterol": "Cholesterol",
    "num__exercise_freq": "Exercise Frequency",
    "num__sleep_hours": "Sleep Hours",
    "num__smoking": "Smoking",
    "num__alcohol": "Alcohol",
    "num__family_history": "Family History",
    "cat__gender_male": "Gender (Male)",
    "cat__gender_female": "Gender (Female)",
    "cat__stress_level_high": "High Stress",
    "cat__stress_level_moderate": "Moderate Stress",
    "cat__stress_level_low": "Low Stress",
}

DISCLAIMER = (
    "NCD Shield AI is an early-screening and risk-prediction tool, NOT a medical "
    "diagnosis. Results are estimates based on the information you provided. Please "
    "consult a qualified healthcare professional for any medical concerns."
)


class Predictor:
    def __init__(self) -> None:
        self.model = None
        self.metadata: dict = {}
        self._load()

    def _load(self) -> None:
        model_path = os.path.join(settings.model_dir, "ncd_model.joblib")
        meta_path = os.path.join(settings.model_dir, "metadata.json")
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                if os.path.exists(meta_path):
                    with open(meta_path) as f:
                        self.metadata = json.load(f)
            except Exception as exc:  # pragma: no cover
                print(f"[predictor] failed to load model: {exc}; using heuristic")
                self.model = None
        else:
            print(f"[predictor] no model at {model_path}; using heuristic fallback")

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    # ---- core inference -----------------------------------------------------
    def _to_frame(self, data: dict) -> pd.DataFrame:
        row = {
            "age": data["age"],
            "gender": data["gender"],
            "height_cm": data["height_cm"],
            "weight_kg": data["weight_kg"],
            "bmi": data["bmi"],
            "systolic_bp": data["systolic_bp"],
            "blood_sugar": data["blood_sugar"],
            "cholesterol": data["cholesterol"],
            "smoking": int(data["smoking"]),
            "alcohol": int(data["alcohol"]),
            "exercise_freq": data["exercise_freq"],
            "sleep_hours": data["sleep_hours"],
            "stress_level": data["stress_level"],
            "family_history": int(data["family_history"]),
        }
        return pd.DataFrame([row])

    def _heuristic(self, data: dict) -> np.ndarray:
        """Fallback probability estimate mirroring the dataset generator logic."""
        stress_num = {"low": 0, "moderate": 1, "high": 2}[data["stress_level"]]
        z = (
            0.045 * (data["age"] - 40)
            + 0.09 * (data["bmi"] - 24)
            + 0.03 * (data["systolic_bp"] - 120)
            + 0.025 * (data["blood_sugar"] - 100)
            + 0.012 * (data["cholesterol"] - 190)
            + 0.8 * int(data["smoking"])
            + 0.35 * int(data["alcohol"])
            - 0.18 * data["exercise_freq"]
            + 0.25 * abs(data["sleep_hours"] - 7.5)
            + 0.45 * stress_num
            + 0.7 * int(data["family_history"])
        )
        # squash into pseudo-probabilities across 3 classes
        low = 1 / (1 + np.exp(0.5 * (z - 1)))
        high = 1 / (1 + np.exp(-0.5 * (z - 4)))
        mod = max(0.05, 1 - low - high)
        probs = np.array([low, mod, high])
        return probs / probs.sum()

    def predict(self, data: dict) -> dict:
        if self.model is not None:
            frame = self._to_frame(data)
            probs = self.model.predict_proba(frame)[0]
        else:
            probs = self._heuristic(data)

        risk_class = int(np.argmax(probs))
        # Weighted risk score (0..100): probability mass shifted toward higher risk.
        risk_score = round(float(probs[1] * 50 + probs[2] * 100), 1)
        health_score = round(100 - risk_score, 1)

        return {
            "risk_class": risk_class,
            "risk_level": RISK_LABELS[risk_class],
            "risk_score": risk_score,
            "health_score": health_score,
            "probabilities": {
                "low": round(float(probs[0]), 4),
                "moderate": round(float(probs[1]), 4),
                "high": round(float(probs[2]), 4),
            },
            "explanation": self._explain(data),
            "disclaimer": DISCLAIMER,
        }

    # ---- explainability -----------------------------------------------------
    def _explain(self, data: dict) -> list[dict]:
        """Combine global feature importance with the direction each input pushes risk."""
        importances = self.metadata.get("feature_importance", {})
        if not importances:
            # Heuristic importances when no trained model present.
            importances = {
                "num__bmi": 0.16, "num__age": 0.14, "num__smoking": 0.12,
                "num__family_history": 0.11, "num__blood_sugar": 0.10,
                "num__systolic_bp": 0.09, "cat__stress_level_high": 0.08,
                "num__exercise_freq": 0.08, "num__cholesterol": 0.07,
                "num__sleep_hours": 0.05,
            }

        directions = self._directions(data)
        items: list[dict] = []
        for feat, imp in list(importances.items())[:8]:
            contribution = directions.get(self._root_feature(feat), "neutral")
            items.append(
                {
                    "feature": feat,
                    "label": self._pretty_label(feat),
                    "importance": round(float(imp), 4),
                    "contribution": contribution,
                }
            )
        return items

    @staticmethod
    def _pretty_label(feat: str) -> str:
        """Human-friendly label, including interaction features like 'BMI × Age'."""
        if feat in FEATURE_LABELS:
            return FEATURE_LABELS[feat]
        # Strip the ColumnTransformer prefix (num__ / cat__).
        name = feat.split("__", 1)[-1]
        # PolynomialFeatures joins interacting features with a space.
        parts = name.split(" ")
        pretty = [FEATURE_LABELS.get(f"num__{p}", p.replace("_", " ").title()) for p in parts]
        return " × ".join(pretty)

    @staticmethod
    def _root_feature(encoded: str) -> str:
        name = encoded.split("__")[-1] if "__" in encoded else encoded
        for root in [
            "stress_level", "family_history", "blood_sugar", "systolic_bp",
            "exercise_freq", "sleep_hours", "height_cm", "weight_kg",
        ]:
            if name.startswith(root):
                return root
        return name.split("_")[0]

    @staticmethod
    def _directions(data: dict) -> dict[str, str]:
        def d(cond: bool) -> str:
            return "increases" if cond else "decreases"

        return {
            "age": d(data["age"] > 45),
            "bmi": d(data["bmi"] > 25),
            "systolic": d(data["systolic_bp"] > 130),
            "blood": d(data["blood_sugar"] > 110),
            "cholesterol": d(data["cholesterol"] > 200),
            "smoking": d(bool(data["smoking"])),
            "alcohol": d(bool(data["alcohol"])),
            "exercise": "decreases" if data["exercise_freq"] >= 3 else "increases",
            "sleep": d(abs(data["sleep_hours"] - 7.5) > 1.5),
            "stress": d(data["stress_level"] == "high"),
            "family": d(bool(data["family_history"])),
            "gender": "neutral",
        }


# Singleton instance reused across requests.
predictor = Predictor()
