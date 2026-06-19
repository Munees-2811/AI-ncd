from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.ml.predictor import predictor
from app.models import Prediction, SystemLog, User
from app.schemas.prediction import AssessmentInput, PredictionResult
from app.services.recommendations import generate_recommendations

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("", response_model=PredictionResult)
def predict(
    payload: AssessmentInput,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()  # includes computed bmi
    result = predictor.predict(data)
    recommendations = generate_recommendations(data, result["risk_class"])

    record = Prediction(
        user_id=user.id,
        inputs=data,
        risk_level=result["risk_level"],
        risk_score=result["risk_score"],
        risk_class=result["risk_class"],
        health_score=result["health_score"],
        bmi=data["bmi"],
        probabilities=result["probabilities"],
        explanation=result["explanation"],
        recommendations=recommendations,
    )
    db.add(record)
    db.add(SystemLog(action="predict", detail=result["risk_level"], user_id=user.id))
    db.commit()
    db.refresh(record)

    return PredictionResult(
        id=record.id,
        risk_level=result["risk_level"],
        risk_class=result["risk_class"],
        risk_score=result["risk_score"],
        health_score=result["health_score"],
        bmi=data["bmi"],
        probabilities=result["probabilities"],
        explanation=result["explanation"],
        recommendations=recommendations,
        disclaimer=result["disclaimer"],
        created_at=record.created_at,
    )
