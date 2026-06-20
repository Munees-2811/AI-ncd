# Deployment Guide

The app has two parts that deploy separately:

- **Frontend** (React / Next.js) → Netlify
- **Backend** (FastAPI + model) → any Python host (Render, Railway, Fly.io, etc.)

The frontend talks to the backend over an **absolute URL** set via the
`NEXT_PUBLIC_API_URL` environment variable, so the two can live anywhere.

---

## 1. Deploy the backend first

You need the backend reachable over HTTPS before the frontend is useful.

Any host that runs a Docker image or a Python process works. Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set these environment variables on the backend host:

| Variable | Example | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@host:5432/db` | or `sqlite:///./ncd.db` for a quick demo |
| `SECRET_KEY` | *(long random string)* | JWT signing |
| `FRONTEND_ORIGIN` | `https://your-site.netlify.app` | **must** match your Netlify URL for CORS |
| `MODEL_DIR` | `/app/ml/models` | where the trained model lives |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | … | seeded admin account |

> Train the model during build/deploy (`cd ml && python generate_dataset.py && python train.py`),
> or rely on the built-in heuristic fallback if no model artifact is present.

Note your backend URL, e.g. `https://ncd-shield-api.onrender.com`.

---

## 2. Deploy the frontend to Netlify

The repo already includes [`netlify.toml`](../netlify.toml).

### Option A — Netlify UI (recommended)
1. Push this repo to GitHub (already done on your branch).
2. In Netlify: **Add new site → Import from Git → pick this repo**.
3. Netlify reads `netlify.toml` automatically:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Plugin: `@netlify/plugin-nextjs` (installed automatically)
4. **Site settings → Environment variables**, add:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-host
   ```
5. **Deploy**. Netlify gives you a URL like `https://your-site.netlify.app`.

### Option B — Netlify CLI
```bash
npm install -g netlify-cli
cd frontend
netlify init          # link to a site
netlify env:set NEXT_PUBLIC_API_URL https://your-backend-host
netlify deploy --build --prod
```

---

## 3. Connect the two
1. Set the frontend's `NEXT_PUBLIC_API_URL` → backend URL (step 2.4).
2. Set the backend's `FRONTEND_ORIGIN` → Netlify site URL (step 1).
3. Redeploy both. Register an account on the live site and run an assessment. ✅

---

## Local development still works unchanged
With no `NEXT_PUBLIC_API_URL` set, the frontend defaults to
`http://localhost:8000`, so `npm run dev` + a local `uvicorn` work out of the box.
