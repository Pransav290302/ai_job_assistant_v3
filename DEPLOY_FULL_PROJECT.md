# Deploy Full Project (Vercel + Backend)

This guide walks you through deploying the **entire** AI Job Assistant: the Next.js frontend on **Vercel** and the Python FastAPI backend on **Render** (or another host). The frontend and Supabase work with the backend for job analysis and auth.

---

## Overview

| Part        | Where to deploy | Purpose                          |
|------------|------------------|----------------------------------|
| **Frontend** | Vercel           | Next.js app (Supabase, UI)       |
| **Backend**  | Render (or Railway, Fly.io) | FastAPI (jobs, auth, AI) |

You will:

1. Deploy the **backend** first and get its URL.
2. Deploy the **frontend** on Vercel and point it to that URL.
3. Set **environment variables** on both sides (and in Supabase if needed).

---

## Step 1: Deploy the backend (Render) — free tier

The backend runs on Python (FastAPI). Use a **free Web Service** (do **not** use Blueprint — that can be paid).

1. Push your repo to **GitHub** (if you haven’t already).
2. Go to [render.com](https://render.com) and sign in with GitHub.
3. **New + → Web Service** (not Blueprint). Connect your GitHub repo and select **ai_job_assistant_v3**.
4. Configure the service:
   - **Root Directory**: `ai_job_backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free** (0 USD/month)
5. In the Render service **Environment** tab, add at least:
   - `OPENAI_API_KEY` – your OpenAI API key
   - `FRONTEND_URL` – your Vercel URL (e.g. `https://your-app.vercel.app`). You can set this after deploying the frontend, then redeploy the backend.
   - `ALLOWED_ORIGINS` – same as `FRONTEND_URL`, or comma-separated list if you use multiple Vercel URLs (e.g. production + preview):
     - `https://your-app.vercel.app,https://your-app-git-branch-xxx.vercel.app`
   - Database and auth vars as in `ai_job_backend/env_template.txt` (e.g. `USE_SQLITE`, PostgreSQL vars, `AUTH_SECRET_KEY`).
6. Deploy. When it’s live, copy the backend URL (e.g. `https://ai-job-backend-xxxx.onrender.com`).

---

## Step 2: Deploy the frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. **Add New → Project** and import your GitHub repo.
3. **Important – Root Directory**
   - Click **Edit** next to “Root Directory”.
   - Choose **`ai_job_frontend`** (not the repo root).
   - Confirm so the Next.js app is built from that folder.
4. **Environment variables** (Settings → Environment Variables). Add for **Production** (and Preview/Development if you want):

   | Name                         | Value / where to get it |
   |-----------------------------|---------------------------|
   | `NEXT_PUBLIC_API_URL`       | Backend URL from Step 1 (e.g. `https://ai-job-backend-xxxx.onrender.com`) |
   | `NEXT_PUBLIC_SUPABASE_URL`  | Supabase project URL (Dashboard → Settings → API) |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon/public key (same place) |
   | `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (keep secret) |
   | `NEXTAUTH_SECRET`           | Random string (e.g. `openssl rand -base64 32`) |
   | `NEXTAUTH_URL`              | Your Vercel app URL (e.g. `https://your-app.vercel.app`) – optional; Vercel often sets this |

5. Click **Deploy**. Vercel will build and deploy the frontend.
6. Copy your Vercel URL (e.g. `https://your-app.vercel.app`).

---

## Step 3: Connect backend and frontend

1. **Backend (Render)**  
   - Set `FRONTEND_URL` to your Vercel URL (e.g. `https://your-app.vercel.app`).  
   - Set `ALLOWED_ORIGINS` to the same value, or a comma-separated list of all Vercel URLs you use (production + preview).  
   - Save and redeploy the backend so CORS allows your Vercel domain(s).

2. **Supabase (if you use auth)**  
   - In Supabase Dashboard → Authentication → URL Configuration, add your Vercel URL to **Site URL** and **Redirect URLs** (e.g. `https://your-app.vercel.app`, `https://your-app.vercel.app/auth/callback`).

---

## Checklist

- [ ] Backend deployed on Render (or other host) and URL copied
- [ ] Backend env vars set: `OPENAI_API_KEY`, `FRONTEND_URL`, `ALLOWED_ORIGINS`, DB and auth vars
- [ ] Frontend deployed on Vercel with **Root Directory** = `ai_job_frontend`
- [ ] Vercel env vars set: `NEXT_PUBLIC_API_URL`, Supabase keys, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`
- [ ] `FRONTEND_URL` / `ALLOWED_ORIGINS` on backend point to your Vercel URL(s)
- [ ] Supabase Site URL and Redirect URLs include your Vercel URL

---

## Notes

- **Backend on Vercel?** The Python backend uses Playwright and heavier dependencies; it’s meant for a long-running server (Render, Railway, etc.). Deploying it as Vercel serverless functions would require significant changes and limits; the recommended setup is frontend on Vercel, backend on Render (or similar).
- **Preview deployments**: Each Vercel preview gets its own URL. To use the same backend from previews, add those URLs to `ALLOWED_ORIGINS` on the backend (comma-separated), or use one main production URL for now.
- **Secrets**: Never commit `.env` or `.env.local`. All secrets go in Render Environment and Vercel Environment Variables (and Supabase for DB/auth).
