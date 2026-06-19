from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Prediction, User
from app.services.pdf_report import build_report

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/{prediction_id}")
def download_report(
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

    prediction_dict = {
        "inputs": pred.inputs,
        "risk_level": pred.risk_level,
        "risk_class": pred.risk_class,
        "risk_score": pred.risk_score,
        "health_score": pred.health_score,
        "bmi": pred.bmi,
        "recommendations": pred.recommendations,
        "disclaimer": "NCD Shield AI is an early-screening tool, NOT a medical diagnosis. "
        "Consult a qualified physician for medical advice.",
    }
    pdf_bytes = build_report(
        {"full_name": user.full_name, "email": user.email}, prediction_dict
    )
    headers = {
        "Content-Disposition": f'attachment; filename="ncd_report_{prediction_id}.pdf"'
    }
    import io

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
