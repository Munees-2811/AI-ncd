from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Snapshot of the inputs that produced this prediction.
    inputs: Mapped[dict] = mapped_column(JSON, nullable=False)

    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # Low/Moderate/High
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)      # 0..100 (%)
    risk_class: Mapped[int] = mapped_column(Integer, nullable=False)      # 0/1/2
    health_score: Mapped[float] = mapped_column(Float, nullable=False)    # 0..100
    bmi: Mapped[float] = mapped_column(Float, nullable=False)

    probabilities: Mapped[dict] = mapped_column(JSON, nullable=False)
    explanation: Mapped[list] = mapped_column(JSON, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="predictions")
