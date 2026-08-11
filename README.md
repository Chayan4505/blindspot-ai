# BlindSpot.AI

**Industrial-grade synthetic data generation for AI robustness**

BlindSpot.AI solves the Edge-Case Crisis in modern AI. It generates photorealistic, physics-grounded synthetic training data targeting the exact blind spots of your model — without staging dangerous real-world events.

---

## Deployment (Render + Vercel + Supabase)

### Prerequisites

- [Render](https://render.com) account
- [Vercel](https://vercel.com) account
- [Supabase](https://supabase.com) project (with a Storage bucket named `blindspot` set to **Public**)

---

### 1. Supabase setup

1. Go to **Storage** → create a bucket named `blindspot`, set it to **Public**
2. Go to **Settings → Database** → copy the **Session mode** connection string (port 5432)
3. Go to **Settings → API** → copy:
   - `Project URL` → `SUPABASE_URL`
   - `service_role` key → `SUPABASE_SERVICE_KEY` (keep secret)
   - `anon` public key → `REACT_APP_SUPABASE_ANON_KEY`

---

### 2. Deploy backend to Render

1. Push this repo to GitHub
2. In Render → **New Web Service** → connect your repo
3. Set **Root Directory** to `backend`
4. Render auto-detects `render.yaml` — confirm the settings
5. Add these **environment variables** in the Render dashboard:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Supabase Postgres URI (Session mode, port 5432) |
| `SUPABASE_URL` | `https://<ref>.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Your `service_role` key |
| `SUPABASE_STORAGE_BUCKET` | `blindspot` |
| `API_BASE_URL` | `https://<your-app>.onrender.com` |
| `GOOGLE_API_KEY` | Your Gemini API key |

6. Deploy — wait for the health check at `/api/health` to go green
7. Copy the service URL (e.g. `https://blindspot-api.onrender.com`)

---

### 3. Deploy frontend to Vercel

1. In Vercel → **New Project** → import your repo
2. Set **Root Directory** to `frontend`
3. Vercel detects Create React App automatically
4. Add these **environment variables** in Vercel:

| Variable | Value |
|---|---|
| `REACT_APP_API_URL` | Your Render backend URL |
| `REACT_APP_SUPABASE_URL` | `https://<ref>.supabase.co` |
| `REACT_APP_SUPABASE_ANON_KEY` | Your Supabase `anon` key |

5. Deploy — your frontend is live

---

### 4. Post-deploy checklist

- [ ] Supabase Storage bucket `blindspot` exists and is set to **Public**
- [ ] Render service health check passes: `GET /api/health`
- [ ] Frontend can reach backend: open the app and create a project
- [ ] Seed image upload stores files in Supabase Storage (check the bucket)
- [ ] Running a generation pipeline produces images visible in the simulation view

---

## Local development

```bash
git clone https://github.com/yourname/blindspot-ai.git
cd blindspot-ai

# Backend
cd backend
cp .env.example .env        # fill in your values
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
cp .env.example .env.local  # set REACT_APP_API_URL=http://localhost:8000
npm install --legacy-peer-deps
npm start
```

Or run the full stack with Docker:

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:3001

---

## Mock mode (default)

`MOCK_ML=true` (default) runs the full pipeline without a GPU — generates placeholder images with physics stressors applied for testing and demo.

Set `MOCK_ML=false` for real Stable Diffusion XL inference (requires NVIDIA GPU with 16GB+ VRAM).

---

## What it does

1. Upload 5–10 seed images of your target object
2. **Adversarial Scan** — probes your model to find confidence drop zones
3. **Generate** — SDXL + LoRA + ControlNet creates targeted synthetic images
4. **Physics Refine** — applies accurate rain, fog, night, lens flare, occlusion
5. **Auto-Label** — Mask R-CNN generates COCO JSON + YOLO labels automatically
6. **Export** — download ready-to-train dataset ZIP

---

## Project structure

```
blindspot-ai/
├── backend/
│   ├── main.py                   # FastAPI + all endpoints
│   ├── models.py                 # SQLAlchemy models (SQLite / Postgres)
│   ├── tasks.py                  # Celery pipeline tasks
│   ├── storage.py                # Supabase Storage / local fallback
│   └── services/
│       ├── adversarial_agent.py  # Model probing
│       ├── generative_engine.py  # Image generation (SDXL / mock)
│       ├── physics_layer.py      # Physics stressors
│       ├── auto_labeler.py       # COCO / YOLO labeling
│       └── gemini_service.py     # Scenario brainstorming
├── frontend/
│   └── src/
│       ├── pages/                # All page components
│       ├── components/           # Shared UI
│       ├── hooks/useProject.ts   # Auto-polling hook
│       └── api/
│           ├── client.ts         # Axios API client
│           └── supabase.ts       # Supabase auth client
├── render.yaml                   # Render one-click deploy config
├── vercel.json                   # Vercel deploy config
├── docker-compose.yml            # Full local stack
└── .env.example
```

---

## Key environment variables

| Variable | Where | Description |
|---|---|---|
| `DATABASE_URL` | Render | Supabase Postgres URI |
| `SUPABASE_URL` | Render | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Render | `service_role` key (secret) |
| `SUPABASE_STORAGE_BUCKET` | Render | Storage bucket name |
| `API_BASE_URL` | Render | Public Render service URL |
| `MOCK_ML` | Render | `true` to skip GPU inference |
| `REACT_APP_API_URL` | Vercel | Render backend URL |
| `REACT_APP_SUPABASE_URL` | Vercel | Supabase project URL |
| `REACT_APP_SUPABASE_ANON_KEY` | Vercel | Supabase `anon` key |
