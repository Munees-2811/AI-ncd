from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.ml.predictor import predictor
from app.models import Prediction, SystemLog, User
from app.schemas.auth import UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


class AdminStats(BaseModel):
    total_users: int
    total_predictions: int
    risk_distribution: dict[str, int]
    model_name: str
    model_accuracy: float | None
    model_f1: float | None
    avg_health_score: float | None


@router.get("/stats", response_model=AdminStats)
def stats(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0

    dist_rows = (
        db.query(Prediction.risk_level, func.count(Prediction.id))
        .group_by(Prediction.risk_level)
        .all()
    )
    risk_distribution = {level: count for level, count in dist_rows}
    avg_health = db.query(func.avg(Prediction.health_score)).scalar()

    meta = predictor.metadata
    best_metrics = meta.get("best_metrics", {})
    return AdminStats(
        total_users=total_users,
        total_predictions=total_predictions,
        risk_distribution=risk_distribution,
        model_name=meta.get("best_model", "heuristic"),
        model_accuracy=best_metrics.get("accuracy"),
        model_f1=best_metrics.get("f1_weighted"),
        avg_health_score=round(float(avg_health), 1) if avg_health is not None else None,
    )


@router.get("/users", response_model=list[UserOut])
def list_users(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}/toggle-active")
def toggle_active(
    user_id: int, _: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.get("/logs")
def system_logs(
    limit: int = 100, _: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    logs = (
        db.query(SystemLog).order_by(SystemLog.created_at.desc()).limit(min(limit, 500)).all()
    )
    return [
        {
            "id": l.id,
            "level": l.level,
            "action": l.action,
            "detail": l.detail,
            "user_id": l.user_id,
            "created_at": l.created_at,
        }
        for l in logs
    ]


@router.get("/model")
def model_info(_: User = Depends(get_current_admin)):
    return {
        "loaded": predictor.is_model_loaded,
        "metadata": predictor.metadata,
    }
