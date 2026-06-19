from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Prediction, User
from app.schemas.auth import UserOut

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    locale: str | None = None


class ProfileSummary(BaseModel):
    user: UserOut
    total_predictions: int
    latest_health_score: float | None
    latest_risk_level: str | None


@router.get("", response_model=ProfileSummary)
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preds = (
        db.query(Prediction)
        .filter(Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    latest = preds[0] if preds else None
    return ProfileSummary(
        user=UserOut.model_validate(user),
        total_predictions=len(preds),
        latest_health_score=latest.health_score if latest else None,
        latest_risk_level=latest.risk_level if latest else None,
    )


@router.put("", response_model=UserOut)
def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name:
        user.full_name = payload.full_name
    if payload.locale in {"en", "ta"}:
        user.locale = payload.locale
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
