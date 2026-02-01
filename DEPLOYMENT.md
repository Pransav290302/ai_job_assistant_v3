# Deployment Guide – Render (Backend) + Vercel (Frontend)

> **Full step-by-step guide:** See [FULL_DEPLOYMENT.md](./FULL_DEPLOYMENT.md)

## Project Structure

- `ai_job_backend/` → Deploy to **Render**
- `ai_job_frontend/` → Deploy to **Vercel**

---

## 1. Render (Backend)

### Connect Repo
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. **New** → **Web Service**
3. Connect your Git repo
4. Configure:
   - **Root Directory**: `ai_job_backend`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables (Render Dashboard → Environment)

| Variable | Required | Value |
|----------|----------|-------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `DATABASE_URL` | Yes | From Render Postgres (connect DB to service) or paste connection string |
| `AUTH_SECRET_KEY` | Yes | Random secret: `node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"` |
| `FRONTEND_URL` | Yes | `https://your-app.vercel.app` |
| `ALLOWED_ORIGINS` | Yes | `https://your-app.vercel.app` |
| `USE_SELENIUM` | No | `false` |
| `USE_PLAYWRIGHT` | No | `true` (default) |
| `BROWSERLESS_URL` | No | Optional: `wss://chrome.browserless.io?token=XXX` |

### Add PostgreSQL
- **New** → **PostgreSQL**
- Connect it to your web service
- `DATABASE_URL` is set automatically

---

## 2. Vercel (Frontend)

### Connect Repo
1. Go to [vercel.com](https://vercel.com)
2. **Add New** → **Project**
3. Import your repo
4. **Root Directory**: set to `ai_job_frontend`
5. Framework: Next.js (auto-detected)

### Environment Variables (Vercel → Settings → Environment Variables)

| Variable | Required | Value |
|----------|----------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | `https://your-backend.onrender.com` (from Render dashboard) |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | From Supabase dashboard |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | From Supabase dashboard |

### Optional
- `NEXTAUTH_URL` – `https://your-app.vercel.app`
- `NEXTAUTH_SECRET` – Random secret

---

## 3. After Deployment

1. Copy your **Render** backend URL (e.g. `https://ai-job-backend-xxxx.onrender.com`)
2. In **Vercel**, set `NEXT_PUBLIC_BACKEND_URL` to that URL
3. In **Render**, set `FRONTEND_URL` and `ALLOWED_ORIGINS` to your Vercel URL
4. **Redeploy** both services after changing env vars
5. Render free tier cold start: first request after ~15 min can take ~1 min

---

## 4. Verify

**Backend:**
```bash
curl https://your-backend.onrender.com/api/status
```

**Frontend:** Open `https://your-app.vercel.app/assistant` and test scrape/analyze.
