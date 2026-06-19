import os

# Use an isolated in-memory-ish SQLite DB for tests before importing the app.
os.environ["DATABASE_URL"] = "sqlite:///./test_ncd.db"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app, seed_admin


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_admin()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_ncd.db"):
        os.remove("./test_ncd.db")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
        },
    )
    resp = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "Password123"},
    )
    return resp.json()["access_token"]
