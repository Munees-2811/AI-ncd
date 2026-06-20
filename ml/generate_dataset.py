"""
Synthetic dataset generator for NCD Shield AI.

Produces a realistic, labelled dataset linking lifestyle / health features to the
risk of four Non-Communicable Diseases (NCDs). The relationships below are encoded
using clinically-inspired heuristics so that trained models learn sensible patterns.

This is SYNTHETIC data for demo / hackathon use only — it is not real patient data.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_SAMPLES = 30000
OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "ncd_dataset.csv")

GENDERS = ["male", "female"]
STRESS_LEVELS = ["low", "moderate", "high"]


def _clip(x, lo, hi):
    return np.clip(x, lo, hi)


def generate() -> pd.DataFrame:
    n = N_SAMPLES

    age = _clip(RNG.normal(45, 16, n), 18, 90).round().astype(int)
    gender = RNG.choice(GENDERS, n)
    height_cm = _clip(RNG.normal(168, 10, n), 140, 200).round(1)
    # weight correlates loosely with height + noise
    weight_kg = _clip(RNG.normal(72, 16, n) + (height_cm - 168) * 0.4, 40, 160).round(1)
    bmi = (weight_kg / (height_cm / 100) ** 2).round(1)

    systolic_bp = _clip(RNG.normal(125, 18, n) + (age - 45) * 0.3, 90, 200).round().astype(int)
    blood_sugar = _clip(RNG.normal(105, 30, n) + (bmi - 25) * 1.2, 70, 300).round().astype(int)
    cholesterol = _clip(RNG.normal(195, 40, n) + (age - 45) * 0.5, 120, 350).round().astype(int)

    smoking = RNG.choice([0, 1], n, p=[0.7, 0.3])
    alcohol = RNG.choice([0, 1], n, p=[0.65, 0.35])
    exercise_freq = RNG.integers(0, 8, n)          # days/week
    sleep_hours = _clip(RNG.normal(6.8, 1.3, n), 3, 11).round(1)
    stress_level = RNG.choice(STRESS_LEVELS, n, p=[0.4, 0.4, 0.2])
    family_history = RNG.choice([0, 1], n, p=[0.6, 0.4])

    stress_num = pd.Series(stress_level).map({"low": 0, "moderate": 1, "high": 2}).to_numpy()

    # ---- Risk scoring (latent) ----------------------------------------------
    # Normalized contributions plus clinically-inspired interaction terms,
    # summed into a logit, then thresholded into risk classes.
    z = (
        0.045 * (age - 40)
        + 0.09 * (bmi - 24)
        + 0.03 * (systolic_bp - 120)
        + 0.025 * (blood_sugar - 100)
        + 0.012 * (cholesterol - 190)
        + 0.8 * smoking
        + 0.35 * alcohol
        - 0.18 * exercise_freq
        + 0.25 * np.abs(sleep_hours - 7.5)
        + 0.45 * stress_num
        + 0.7 * family_history
        # interaction terms — combined risk factors compound the danger
        + 0.015 * np.maximum(0, age - 50) * smoking            # older smokers
        + 0.004 * np.maximum(0, bmi - 25) * (blood_sugar - 100)  # obesity × high sugar
        + 0.010 * smoking * (systolic_bp - 120)                # smoking × high BP
        + 0.20 * family_history * (bmi > 30)                   # genetics × obesity
        + RNG.normal(0, 1.1, n)
    )

    # Map latent score to 3-class risk via quantiles.
    q33, q66 = np.quantile(z, [0.45, 0.78])
    risk = np.where(z <= q33, 0, np.where(z <= q66, 1, 2))  # 0 low, 1 moderate, 2 high

    df = pd.DataFrame(
        {
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "systolic_bp": systolic_bp,
            "blood_sugar": blood_sugar,
            "cholesterol": cholesterol,
            "smoking": smoking,
            "alcohol": alcohol,
            "exercise_freq": exercise_freq,
            "sleep_hours": sleep_hours,
            "stress_level": stress_level,
            "family_history": family_history,
            "risk": risk,
        }
    )
    return df


def main() -> None:
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df = generate()
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df):,} rows -> {OUT_PATH}")
    print(df["risk"].value_counts(normalize=True).rename({0: "low", 1: "moderate", 2: "high"}))


if __name__ == "__main__":
    main()
