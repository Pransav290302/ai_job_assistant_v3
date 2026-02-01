# Render Backend Deployment (Vercel Frontend Integration)

> See [DEPLOYMENT.md](./DEPLOYMENT.md) for a full deployment checklist.

This guide helps you fix **"Failed to fetch"** when your Vercel frontend calls your Render backend.

## Why "Failed to fetch" Happens

1. **CORS** – Backend blocks requests from your Vercel origin  
2. **Wrong backend URL** – `NEXT_PUBLIC_BACKEND_URL` not set or incorrect in Vercel  
3. **Render cold start** – Free tier spins down after ~15 min; first request can take 50–90 seconds  
4. **Selenium on Render** – Default Python env does not include Chrome; Selenium will fail unless you use a custom Docker build  

---

## Render Environment Variables (Required)

Set these in **Render Dashboard** → your web service → **Environment**:

| Variable | Value | Notes |
|----------|-------|-------|
| `FRONTEND_URL` | `https://ai-job-assistant-v3.vercel.app` | Your Vercel frontend URL |
| `ALLOWED_ORIGINS` | `https://ai-job-assistant-v3.vercel.app` | Same as above, or comma-separated if multiple |
| `DATABASE_URL` | *(auto if PostgreSQL connected)* | Or paste your Postgres connection string |
| `OPENAI_API_KEY` | your OpenAI key | Required for AI features |
| `AUTH_SECRET_KEY` | random secret | Generate with `openssl rand -base64 32` or Node |
| `USE_SELENIUM` | `false` | Render has no Chrome; use Playwright |
| `USE_PLAYWRIGHT` | `true` | LinkedIn, Glassdoor (Chromium in build) |
| `BROWSERLESS_URL` | *(optional)* | `wss://chrome.browserless.io?token=XXX` – 6 hrs free/month, different IPs |

### LinkedIn & Glassdoor on Render Free Tier

- Render’s **Playwright + Chromium** – Build runs `playwright install chromium` + **playwright-stealth** (anti-detection) (~150MB).  
- Works for LinkedIn, Glassdoor, Indeed, Greenhouse.  
- **USE_PLAYWRIGHT=true** – Default. No extra env var needed.  
- **Browserless** – If blocked, add BROWSERLESS_URL (6 hrs free/month) for different IPs.

---

## Vercel Environment Variables (Required)

In **Vercel** → Project → **Settings** → **Environment Variables**:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_BACKEND_URL` or `NEXT_PUBLIC_API_URL` | `https://ai-job-backend.onrender.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key |

Use your **actual** Render URL from the Render dashboard (e.g. `https://ai-job-backend-xxxx.onrender.com`).

---

## Checklist

- [ ] Render: `FRONTEND_URL` = your Vercel URL  
- [ ] Render: `ALLOWED_ORIGINS` = your Vercel URL (or comma-separated list)  
- [ ] Render: `USE_SELENIUM=false`, `USE_PLAYWRIGHT=true` (default)  
- [ ] Vercel: `NEXT_PUBLIC_BACKEND_URL` = your Render backend URL  
- [ ] Redeploy both Render and Vercel after changing env vars  
- [ ] Wait ~1 minute on first request (Render cold start)  

---

## Test Backend Directly

```bash
curl -X POST https://ai-job-backend.onrender.com/api/job/scrape \
  -H "Content-Type: application/json" \
  -d '{"job_url": "https://example.com/job"}'
```

If this works, the backend is fine and the problem is CORS or the frontend URL config.

