# Full Deployment Guide: Render + Vercel + Supabase

Step-by-step guide to deploy the AI Job Assistant on Render (backend), Vercel (frontend), and Supabase (auth + database).

---

## Prerequisites

- [ ] Git repo pushed to GitHub/GitLab
- [ ] [Render](https://render.com) account
- [ ] [Vercel](https://vercel.com) account
- [ ] [Supabase](https://supabase.com) account (cloud)
- [ ] OpenAI API key
- [ ] (Optional) ScraperAPI key for job scraping (1000 free/month)

---

## Part 1: Supabase (Auth + Database)

### 1.1 Create Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. **New Project** → Name it, set password, choose region
3. Wait for project to be ready

### 1.2 Get Credentials

**Settings** → **API**:

- **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
- **anon public** key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **service_role** key → `SUPABASE_SERVICE_ROLE_KEY` (keep secret!)

### 1.3 URL Configuration (do this after Vercel is deployed)

**Authentication** → **URL Configuration**:

- **Site URL:** `https://YOUR-VERCEL-APP.vercel.app`
- **Redirect URLs** (add each):
  - `https://YOUR-VERCEL-APP.vercel.app/auth/callback`
  - `http://localhost:3000/auth/callback`
  - `https://*.vercel.app/auth/callback`

Replace `YOUR-VERCEL-APP` with your actual Vercel project name.

---

## Part 2: Render (Backend)

### 2.1 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. **New** → **Web Service**
3. Connect your Git repo (GitHub/GitLab)
4. Configure:

| Field | Value |
|-------|-------|
| **Name** | `ai-job-backend` (or any name) |
| **Root Directory** | `ai_job_backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && ( [ "$FREE_TIER" = "true" ] || playwright install chromium )` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

> Or use **render.yaml** (Blueprint): Connect repo → New → Blueprint → select `render.yaml`

### 2.2 Add PostgreSQL

1. **New** → **PostgreSQL**
2. Create database, note the connection details
3. In your Web Service → **Environment** → **Add Environment Variable**
4. Add **Linked** variable: `DATABASE_URL` → link to your Postgres

Or use **Supabase Postgres**: Copy connection string from Supabase → Settings → Database → Connection string (URI).

### 2.3 Render Environment Variables

**Environment** tab → Add:

| Variable | Value | Required |
|----------|-------|----------|
| `PYTHON_VERSION` | `3.12` | Yes |
| `DATABASE_URL` | *(from Postgres or Supabase)* | Yes |
| `OPENAI_API_KEY` | Your OpenAI key | Yes |
| `AUTH_SECRET_KEY` | Generate: `node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"` | Yes |
| `FRONTEND_URL` | `https://YOUR-VERCEL-APP.vercel.app` | Yes |
| `ALLOWED_ORIGINS` | `https://YOUR-VERCEL-APP.vercel.app` | Yes |
| `FREE_TIER` | `true` | For demo (skips Playwright) |
| `SCRAPER_API_KEY` | *(optional)* ScraperAPI key | No |

### 2.4 Deploy

Click **Create Web Service**. Wait for build. Copy your backend URL, e.g. `https://ai-job-backend-xxxx.onrender.com`.

---

## Part 3: Vercel (Frontend)

### 3.1 Create Project

1. Go to [Vercel](https://vercel.com)
2. **Add New** → **Project**
3. Import your Git repo
4. Configure:

| Field | Value |
|-------|-------|
| **Root Directory** | `ai_job_frontend` |
| **Framework Preset** | Next.js (auto) |

### 3.2 Vercel Environment Variables

**Settings** → **Environment Variables** → Add:

| Variable | Value | Environments |
|----------|-------|--------------|
| `NEXT_PUBLIC_BACKEND_URL` | `https://ai-job-backend-xxxx.onrender.com` | Production, Preview |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://YOUR-PROJECT.supabase.co` | Production, Preview |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | *(from Supabase)* | Production, Preview |
| `SUPABASE_SERVICE_ROLE_KEY` | *(from Supabase)* | Production, Preview |
| `NEXT_PUBLIC_SITE_URL` | `https://YOUR-VERCEL-APP.vercel.app` | Production, Preview |

Replace placeholders with your actual URLs.

### 3.3 Deploy

Click **Deploy**. Wait for build. Your app will be at `https://YOUR-VERCEL-APP.vercel.app`.

---

## Part 4: Link Render ↔ Vercel

1. **Render**: Set `FRONTEND_URL` and `ALLOWED_ORIGINS` to your Vercel URL
2. **Vercel**: Set `NEXT_PUBLIC_BACKEND_URL` to your Render URL
3. **Redeploy both** after changing env vars

---

## Part 5: Google & LinkedIn OAuth (Optional)

### 5.1 Google

1. [Google Cloud Console](https://console.cloud.google.com/) → Create OAuth Client (Web)
2. **Authorized redirect URI:** `https://YOUR-PROJECT.supabase.co/auth/v1/callback`
3. **Supabase** → Authentication → Providers → Google → Enable, paste Client ID + Secret

### 5.2 LinkedIn

1. [LinkedIn Developer](https://www.linkedin.com/developers/apps) → Create app
2. Products → Request **Sign In with LinkedIn using OpenID Connect**
3. **Auth** → Redirect URLs: `https://YOUR-PROJECT.supabase.co/auth/v1/callback`
4. **Supabase** → Authentication → Providers → **LinkedIn (OIDC)** → Enable, paste Client ID + Secret

See [OAUTH_SETUP.md](ai_job_frontend/OAUTH_SETUP.md) for details.

---

## Checklist

- [ ] Supabase project created, credentials saved
- [ ] Supabase URL Configuration (Site URL, Redirect URLs)
- [ ] Render Web Service deployed, `DATABASE_URL` set
- [ ] Render: `FRONTEND_URL`, `ALLOWED_ORIGINS`, `OPENAI_API_KEY`, `AUTH_SECRET_KEY`
- [ ] Vercel project deployed, Root = `ai_job_frontend`
- [ ] Vercel: `NEXT_PUBLIC_BACKEND_URL`, Supabase vars, `NEXT_PUBLIC_SITE_URL`
- [ ] Render ↔ Vercel URLs linked, both redeployed
- [ ] (Optional) Google + LinkedIn OAuth configured in Supabase

---

## Verify

**Backend:**
```bash
curl https://YOUR-BACKEND.onrender.com/health
```

**Frontend:** Open `https://YOUR-APP.vercel.app`, try login and assistant.

---

## Free Tier Notes

- **Render**: Spins down after ~15 min; first request can take 50–90 seconds (cold start)
- **FREE_TIER=true**: Skips Playwright; use **paste job description** or `SCRAPER_API_KEY` for scraping
- See [FREE_TIER.md](FREE_TIER.md) for lighter resource usage
