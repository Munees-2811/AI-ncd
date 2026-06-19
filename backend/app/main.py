"""NCD Shield AI — FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import admin, auth, chatbot, history, predict, profile, report
from app.config import settings
from app.core.limiter import limiter
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import User


def seed_admin() -> None:
    """Create the default admin account on first boot if it doesn't exist."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.admin_email).first()
        if not existing:
            db.add(
                User(
                    full_name="System Admin",
                    email=settings.admin_email,
                    hashed_password=hash_password(settings.admin_password),
                    is_admin=True,
                )
            )
            db.commit()
            print(f"[startup] seeded admin user {settings.admin_email}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_admin()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Early Screening for Non-Communicable Diseases.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---- Security middleware -----------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# ---- Routers -----------------------------------------------------------------
for r in (auth, profile, predict, history, report, chatbot, admin):
    app.include_router(r.router)


@app.get("/", tags=["meta"])
def root():
    return {
        "app": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "disclaimer": "Early screening tool — not a medical diagnosis.",
    }


@app.get("/health", tags=["meta"])
def health():
    from app.ml.predictor import predictor

    return {"status": "healthy", "model_loaded": predictor.is_model_loaded}
