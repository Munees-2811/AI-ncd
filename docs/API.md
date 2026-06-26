# NCD Shield AI — API Documentation

Base URL (local): `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI) · `/redoc`

All protected endpoints require a Bearer token:
```
Authorization: Bearer <access_token>
```

---

## Auth — `/api/auth`

### `POST /api/auth/register`
```json
{ "full_name": "Jane Doe", "email": "jane@example.com", "password": "Password123", "locale": "en" }
```
**201** → `{ "access_token": "...", "token_type": "bearer" }`

### `POST /api/auth/login`
`application/x-www-form-urlencoded` (OAuth2 password flow):
```
username=jane@example.com&password=Password123
```
**200** → `{ "access_token": "...", "token_type": "bearer" }`

### `POST /api/auth/forgot-password`
```json
{ "email": "jane@example.com" }
```
**200** → `{ "message": "...", "reset_token": "..." }` (token returned only in demo mode)

### `POST /api/auth/reset-password`
```json
{ "token": "<reset_token>", "new_password": "NewPassword123" }
```

---

## Profile — `/api/profile`  *(auth)*

- `GET /api/profile` → user + summary (total predictions, latest health score/risk)
- `PUT /api/profile` → update `full_name` / `locale`

---

## Predict — `/api/predict`  *(auth)*

### `POST /api/predict`
```json
{
  "age": 52, "gender": "male", "height_cm": 175, "weight_kg": 92,
  "systolic_bp": 145, "blood_sugar": 130, "cholesterol": 230,
  "smoking": true, "alcohol": true, "exercise_freq": 1, "sleep_hours": 5.5,
  "stress_level": "high", "family_history": true, "existing_diseases": []
}
```
**200** →
```json
{
  "id": 1, "risk_level": "High Risk", "risk_class": 2,
  "risk_score": 78.5, "health_score": 21.5, "bmi": 30.0,
  "probabilities": { "low": 0.05, "moderate": 0.33, "high": 0.62 },
  "explanation": [ { "feature": "...", "label": "BMI", "importance": 0.16, "contribution": "increases" } ],
  "recommendations": [ { "category": "Smoking", "title": "Stop smoking", "detail": "...", "priority": "high" } ],
  "disclaimer": "NCD Shield AI is an early-screening tool, not a medical diagnosis."
}
```

---

## History — `/api/history`  *(auth)*

- `GET /api/history?limit=50` → list of past predictions (summary)
- `GET /api/history/compare` → compare the two most recent assessments
- `GET /api/history/{id}` → full prediction detail

### `GET /api/history/compare`
Returns `{ "available": false, ... }` when fewer than two assessments exist,
otherwise a direction-aware diff:
```json
{
  "available": true,
  "verdict": "improved",
  "summary": "Your health score improved by 12.3 points since your last assessment.",
  "improved_count": 5, "worsened_count": 1,
  "current":  { "id": 9, "risk_level": "Moderate Risk", "health_score": 62.0, "bmi": 27.0 },
  "previous": { "id": 7, "risk_level": "High Risk", "health_score": 49.7, "bmi": 29.0 },
  "metrics": [
    { "key": "health_score", "label": "Health Score", "unit": "/100",
      "current": 62.0, "previous": 49.7, "delta": 12.3, "direction": "up", "better": true }
  ]
}
```

## Report — `/api/report`  *(auth)*

- `GET /api/report/{prediction_id}` → `application/pdf` download

## Chatbot — `/api/chatbot`  *(auth)*

### `POST /api/chatbot`
```json
{ "message": "How can I lower my diabetes risk?", "locale": "en" }
```
**200** → `{ "reply": "...", "disclaimer": "...", "suggestions": ["..."] }`

---

## Admin — `/api/admin`  *(admin only)*

- `GET /api/admin/stats` → totals, risk distribution, model accuracy/F1, avg health score
- `GET /api/admin/users` → list users
- `PUT /api/admin/users/{id}/toggle-active` → enable/disable a user
- `GET /api/admin/logs?limit=100` → system logs
- `GET /api/admin/model` → loaded model metadata

---

## Errors

| Status | Meaning |
|--------|---------|
| 400 | Validation / bad request |
| 401 | Missing/invalid token |
| 403 | Forbidden (e.g. non-admin) |
| 404 | Not found |
| 429 | Rate limit exceeded |
