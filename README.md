# TobaccoNet — WiFi Subscription Manager

Dark Excel-style web app for managing WiFi subscriptions across tobacco auction warehouses.

**Stack:** FastAPI · PostgreSQL · Vanilla HTML/JS · Deployed on Render.com

---

## Repo Structure

```
tobacconet/
├── backend/
│   ├── main.py           # FastAPI routes
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # DB connection (reads DATABASE_URL env var)
│   └── requirements.txt
├── frontend/
│   └── index.html        # Full single-page app
├── render.yaml           # One-click Render deployment
└── README.md
```

---

## Deploy to Render — Step by Step

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/tobacconet.git
git push -u origin main
```

### 2. Create Render account

Go to https://render.com and sign up (free tier is fine).

### 3. Deploy with render.yaml (Blueprint)

1. In Render dashboard → **New** → **Blueprint**
2. Connect your GitHub repo
3. Render will detect `render.yaml` and create:
   - `tobacconet-api` — Python web service (FastAPI)
   - `tobacconet` — Static site (frontend)
   - `tobacconet-db` — PostgreSQL database
4. Click **Apply** — wait ~3 minutes for first deploy

### 4. Update the API URL in the frontend

After deploy, Render gives your API a URL like:
`https://tobacconet-api.onrender.com`

Edit `frontend/index.html` line ~155:
```js
const API_BASE = window.TOBACCONET_API || 'https://tobacconet-api.onrender.com';
```
Replace with your actual API URL, commit and push — Render auto-redeploys.

### 5. Update CORS in render.yaml

Edit `render.yaml` and set `FRONTEND_URL` to your static site URL
(e.g. `https://tobacconet.onrender.com`), then push again.

### 6. Load demo data (first run)

1. Open the frontend URL
2. Log in as **Jeremiah** (PIN: 7392) — Administrator role required
3. Click ⚙ **Settings** → **Load Demo Data**
4. All 8 warehouses, 10 subscriptions, 3 ISPs load instantly

---

## Users & PINs

| Name     | Role          | PIN  |
|----------|---------------|------|
| Jeremiah | Administrator | 7392 |
| Obert    | IT Manager    | 4817 |
| Lloyd    | Finance Lead  | 6254 |
| Ryan     | Operations    | 9031 |

> PINs are validated server-side. To change them, edit the `USERS` dict in `backend/main.py`.

---

## Features

- **Dashboard** — Summary cards, expiry timeline, cost-by-warehouse bar chart
- **Warehouses** — Full CRUD with ISP assignment, search, status indicators
- **Subscriptions** — Full CRUD with plan type, price, expiry, pay-by, and season end date
- **Budget Planner** — Monthly spend, season remaining cost, YTD spend, progress bars
- **Reminders** — Colour-coded alerts (Expired / Urgent ≤3d / Expiring ≤7d), email button
- **ISP Providers** — Manage TelOne, ZOL, NetOne etc.
- **Settings** — Finance email, reminder threshold, season dates
- **Email Reminders** — Opens pre-drafted email to finance department via mailto:
- **CSV Export** — One-click download of all subscription data

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
DATABASE_URL=sqlite:///./tobacconet.db uvicorn main:app --reload --port 8000

# Frontend — just open in browser
# But update API_BASE in index.html to http://localhost:8000 first
```

API docs available at: `http://localhost:8000/docs`

---

## Changing PINs

Edit `USERS` in `backend/main.py`:

```python
USERS = {
    "jeremiah": {"name": "Jeremiah", "role": "Administrator", "pin": "YOUR_NEW_PIN", ...},
    ...
}
```

Commit and push — Render redeploys automatically.

---

## Free Tier Notes

- Render free tier **spins down** after 15 minutes of inactivity
- First request after idle takes ~30 seconds (cold start) — the login screen shows "Connecting to server…" during this time
- PostgreSQL free tier: 256MB storage, 1GB RAM — more than enough for this use case
- To avoid cold starts, upgrade to Render Starter ($7/mo)
