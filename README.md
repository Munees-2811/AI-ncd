# 🛡️ NCD Shield AI

### AI-Powered Early Screening for Non-Communicable Diseases

NCD Shield AI is a production-grade healthcare SaaS application that estimates a user's
risk of developing **Non-Communicable Diseases (NCDs)** — Diabetes, Hypertension,
Heart Disease, and Chronic Kidney Disease — from lifestyle and health data, and returns
**personalized, explainable recommendations**.

> ⚠️ **Disclaimer:** NCD Shield AI is **NOT** a medical diagnosis tool. It is an early
> screening and risk-prediction system. Always consult a qualified physician.

---

## ✨ Features

| Area | Highlights |
|------|-----------|
| **Landing** | Modern glassmorphism UI, hero, features, stats, FAQ, dark mode |
| **Auth** | Register / Login / Forgot password, JWT, bcrypt password hashing |
| **Assessment** | 14-factor health form, automatic BMI calculation |
| **AI Engine** | Multi-model training (RF, XGBoost, LogReg, Decision Tree), best-model auto-select |
| **Explainability** | Per-prediction feature-importance explanation |
| **Recommendations** | Rule + model driven personalized lifestyle guidance |
| **Dashboard** | Health score, risk trend, history charts (Recharts) |
| **Reports** | Professional PDF report generation |
| **Chatbot** | Healthcare assistant (never diagnoses) |
| **Admin** | Users, predictions, analytics, model accuracy, system logs |
| **i18n** | English + Tamil language switcher |
| **Security** | Rate limiting, CORS, input validation, JWT, SQLi/XSS protection |

---

## 🧱 Tech Stack

**Frontend:** Next.js 15 · React · TypeScript · Tailwind CSS · shadcn/ui · Framer Motion · Recharts
**Backend:** FastAPI · Python 3.11 · Pydantic v2
**ML:** scikit-learn · pandas · NumPy · XGBoost · Joblib
**Database:** PostgreSQL · SQLAlchemy
**Auth:** JWT (python-jose) + bcrypt
**Infra:** Docker · Docker Compose

---

## 📁 Project Structure

```
AI-ncd/
├── backend/          # FastAPI app, API routes, auth, services
│   └── app/
│       ├── api/      # /auth /predict /history /profile /report /chatbot /admin
│       ├── core/     # security, settings, rate limiting
│       ├── models/   # SQLAlchemy ORM models
│       ├── schemas/  # Pydantic request/response models
│       ├── ml/       # model loading + inference
│       └── services/ # recommendations, pdf, chatbot
├── ml/               # dataset generation + training pipeline
│   ├── data/         # sample dataset (CSV)
│   └── models/       # serialized .joblib artifacts
├── frontend/         # Next.js 15 app
├── docker-compose.yml
└── .env.example
```

---

## 🖥️ Quick Demo — Desktop App (no Docker/Node needed)

For fast local testing and demos, a **Tkinter desktop edition** reuses the same
ML model and services in a single window:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cd ml && python generate_dataset.py && python train.py && cd ..   # optional (heuristic fallback otherwise)
python desktop/ncd_shield_desktop.py
```

See [`desktop/README.md`](desktop/README.md) for details.

---

## 🚀 Quick Start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend API + docs → http://localhost:8000/docs

## 🛠️ Local Development

### 1. Train the model (generates dataset + artifacts)

```bash
cd ml
pip install -r ../backend/requirements.txt
python generate_dataset.py
python train.py
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Obtain JWT |
| POST | `/api/auth/forgot-password` | Request reset token |
| GET  | `/api/profile` | Current user profile |
| POST | `/api/predict` | Run NCD risk assessment |
| GET  | `/api/history` | Past predictions |
| GET  | `/api/report/{id}` | Download PDF report |
| POST | `/api/chatbot` | Healthcare assistant |
| GET  | `/api/admin/stats` | Admin analytics |

Full interactive docs at `/docs` (Swagger) and `/redoc`.

---

## 🧪 Testing

```bash
cd backend && pytest
cd frontend && npm test
```

---

## 📜 License

MIT — built for hackathons, learning, and portfolio use.
