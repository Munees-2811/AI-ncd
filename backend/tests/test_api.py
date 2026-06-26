SAMPLE = {
    "age": 52,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 92,
    "systolic_bp": 145,
    "blood_sugar": 130,
    "cholesterol": 230,
    "smoking": True,
    "alcohol": True,
    "exercise_freq": 1,
    "sleep_hours": 5.5,
    "stress_level": "high",
    "family_history": True,
    "existing_diseases": [],
}


def test_root(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json()["status"] == "healthy"


def test_register_and_login(client):
    r = client.post(
        "/api/auth/register",
        json={"full_name": "Jane Doe", "email": "jane@example.com", "password": "Password123"},
    )
    assert r.status_code == 201
    assert "access_token" in r.json()

    r2 = client.post(
        "/api/auth/login",
        data={"username": "jane@example.com", "password": "Password123"},
    )
    assert r2.status_code == 200


def test_predict_requires_auth(client):
    assert client.post("/api/predict", json=SAMPLE).status_code == 401


def test_predict_and_history(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/api/predict", json=SAMPLE, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["risk_level"] in {"Low Risk", "Moderate Risk", "High Risk"}
    assert 0 <= body["risk_score"] <= 100
    assert body["bmi"] > 0
    assert len(body["recommendations"]) > 0

    hist = client.get("/api/history", headers=headers)
    assert hist.status_code == 200
    assert len(hist.json()) >= 1

    pid = body["id"]
    report = client.get(f"/api/report/{pid}", headers=headers)
    assert report.status_code == 200
    assert report.headers["content-type"] == "application/pdf"


def test_chatbot(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/api/chatbot", json={"message": "How can I lower my diabetes risk?"}, headers=headers)
    assert r.status_code == 200
    assert "diabetes" in r.json()["reply"].lower() or len(r.json()["reply"]) > 0


def test_admin_requires_admin(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    assert client.get("/api/admin/stats", headers=headers).status_code == 403


def test_report_comparison(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # With <2 assessments, compare is unavailable (not an error).
    first = client.get("/api/history/compare", headers=headers)
    assert first.status_code == 200
    assert "available" in first.json()

    # Create two distinct assessments — second is healthier.
    worse = {**SAMPLE, "blood_sugar": 180, "systolic_bp": 160, "cholesterol": 260}
    better = {**SAMPLE, "blood_sugar": 95, "systolic_bp": 118, "cholesterol": 175,
              "smoking": False, "exercise_freq": 5}
    client.post("/api/predict", json=worse, headers=headers)
    client.post("/api/predict", json=better, headers=headers)

    cmp = client.get("/api/history/compare", headers=headers)
    assert cmp.status_code == 200
    data = cmp.json()
    assert data["available"] is True
    assert data["verdict"] in {"improved", "declined", "unchanged"}
    assert any(m["key"] == "health_score" for m in data["metrics"])
    # Each metric carries a direction-aware improvement flag.
    assert all("better" in m for m in data["metrics"])
