from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class AssessmentInput(BaseModel):
    """Health-assessment form payload. BMI is derived server-side."""

    age: int = Field(ge=1, le=120)
    gender: Literal["male", "female"]
    height_cm: float = Field(ge=50, le=250)
    weight_kg: float = Field(ge=10, le=400)
    systolic_bp: int = Field(ge=60, le=260, description="Systolic blood pressure (mmHg)")
    blood_sugar: int = Field(ge=40, le=600, description="Fasting blood sugar (mg/dL)")
    cholesterol: int = Field(ge=80, le=500, description="Total cholesterol (mg/dL)")
    smoking: bool = False
    alcohol: bool = False
    exercise_freq: int = Field(ge=0, le=7, description="Exercise days per week")
    sleep_hours: float = Field(ge=0, le=24)
    stress_level: Literal["low", "moderate", "high"] = "moderate"
    family_history: bool = False
    existing_diseases: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight_kg / ((self.height_cm / 100) ** 2), 1)


class ExplanationItem(BaseModel):
    feature: str
    label: str
    importance: float
    contribution: str  # "increases" | "decreases" | "neutral"


class Recommendation(BaseModel):
    category: str
    title: str
    detail: str
    priority: Literal["high", "medium", "low"]


class PredictionResult(BaseModel):
    id: int | None = None
    risk_level: str
    risk_class: int
    risk_score: float
    health_score: float
    bmi: float
    probabilities: dict[str, float]
    explanation: list[ExplanationItem]
    recommendations: list[Recommendation]
    disclaimer: str
    created_at: datetime | None = None


class PredictionHistoryItem(BaseModel):
    id: int
    risk_level: str
    risk_score: float
    health_score: float
    bmi: float
    created_at: datetime

    class Config:
        from_attributes = True
