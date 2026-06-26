from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Prediction, User
from app.schemas.prediction import PredictionHistoryItem, PredictionResult
from app.services.comparison import compare_reports

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[PredictionHistoryItem])
def list_history(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preds = (
        db.query(Prediction)
        .filter(Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
    return preds


def _to_dict(pred: Prediction) -> dict:
    return {
        "id": pred.id,
        "created_at": pred.created_at,
        "risk_level": pred.risk_level,
        "risk_score": pred.risk_score,
        "health_score": pred.health_score,
        "bmi": pred.bmi,
        "inputs": pred.inputs,
    }


@router.get("/compare")
def compare_latest(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare the two most recent assessments and flag improvement/downfall."""
    preds = (
        db.query(Prediction)
        .filter(Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .limit(2)
        .all()
    )
    if len(preds) < 2:
        return {
            "available": False,
            "message": "Take at least two assessments to compare your reports.",
        }
    return compare_reports(_to_dict(preds[0]), _to_dict(preds[1]))


@router.get("/{prediction_id}", response_model=PredictionResult)
def get_prediction(
    prediction_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pred = (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id, Prediction.user_id == user.id)
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return PredictionResult(
        id=pred.id,
        risk_level=pred.risk_level,
        risk_class=pred.risk_class,
        risk_score=pred.risk_score,
        health_score=pred.health_score,
        bmi=pred.bmi,
        probabilities=pred.probabilities,
        explanation=pred.explanation,
        recommendations=pred.recommendations,
        disclaimer="NCD Shield AI is an early-screening tool, not a medical diagnosis.",
        created_at=pred.created_at,
    )
