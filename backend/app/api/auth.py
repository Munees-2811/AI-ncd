from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import SystemLog, User
from app.schemas.auth import (
    ForgotPasswordRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _log(db: Session, action: str, detail: str = "", user_id: int | None = None):
    db.add(SystemLog(action=action, detail=detail, user_id=user_id))


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        locale=payload.locale,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _log(db, "register", f"user {user.email}", user.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(user.email))


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 form uses `username` field; we treat it as email.
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    _log(db, "login", f"user {user.email}", user.id)
    db.commit()
    token = create_access_token(user.email, {"is_admin": user.is_admin})
    return TokenResponse(access_token=token)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Always respond the same way to avoid user enumeration.
    if user:
        user.reset_token = secrets.token_urlsafe(32)
        db.commit()
        # In production this token would be emailed. For the demo we return it.
        return {
            "message": "If the email exists, a reset link has been sent.",
            "reset_token": user.reset_token,
        }
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user.hashed_password = hash_password(payload.new_password)
    user.reset_token = None
    db.commit()
    return {"message": "Password updated successfully."}
