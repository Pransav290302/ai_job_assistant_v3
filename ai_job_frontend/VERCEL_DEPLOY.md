# Deploy Frontend to Vercel

## 1. Push your code

Push your repo (with `ai_job_frontend/` in it) to GitHub, GitLab, or Bitbucket.

---

## 2. Import project on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in (GitHub/GitLab/Bitbucket).
2. Click **Add New…** → **Project**.
3. **Import** your repository (`ai_job_assistant_v3` or your repo name).

---

## 3. Configure the project

### Root Directory (important)

If your repo **root** is the whole project (backend + frontend):

- Set **Root Directory** to: **`ai_job_frontend`**
- Click **Edit** next to the repo name and set the root to `ai_job_frontend` so Vercel builds the Next.js app.

If your repo contains **only** the frontend, leave Root Directory **empty**.

### Build & Output

- **Framework Preset:** Next.js (auto-detected from `vercel.json` / `package.json`).
- **Build Command:** `npm run build` or `next build --webpack` (use what’s in `package.json`).
- **Output Directory:** leave default (Next.js sets it).
- **Install Command:** `npm install`.

---

## 4. Environment variables

In **Project → Settings → Environment Variables**, add these for **Production** (and optionally Preview/Development):

| Variable | Value | Notes |
|----------|--------|--------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://toyjqdqblstypruacwtm.supabase.co` | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbG...` (your anon key) | From Supabase → Settings → API |
| `NEXT_PUBLIC_BACKEND_URL` | `https://ai-job-backend.onrender.com` | Your Render backend URL (no trailing slash) |
| `NEXT_PUBLIC_SITE_URL` | `https://your-app.vercel.app` | Your Vercel app URL (after first deploy) |

Optional (for server-side Supabase and OAuth):

| Variable | Value |
|----------|--------|
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service_role key (keep secret) |
| `NEXTAUTH_URL` | `https://your-app.vercel.app` |
| `NEXTAUTH_SECRET` | Random string (e.g. `openssl rand -base64 32`) |

Use **one** of `NEXT_PUBLIC_BACKEND_URL` or `NEXT_PUBLIC_API_URL`; the app uses whichever is set.

---

## 5. Deploy

1. Click **Deploy**.
2. Wait for the build to finish. If it fails, check the build logs (often Node/Next or memory limits).
3. Your app will be at `https://your-project.vercel.app` (or your custom domain).

---

## 6. Backend CORS (Render)

So the Vercel frontend can call the Render backend:

- In **Render** → your backend service → **Environment**:
  - `FRONTEND_URL` = `https://your-project.vercel.app`
  - `ALLOWED_ORIGINS` = `https://your-project.vercel.app` (or leave blank to use FRONTEND_URL)
- Save and redeploy the backend if you change these.

---

## 7. Supabase auth redirect (optional)

If you use Supabase OAuth (Google, etc.):

1. Supabase Dashboard → **Authentication** → **URL Configuration**.
2. Add to **Redirect URLs**: `https://your-project.vercel.app/**` and `https://your-project.vercel.app/auth/callback`.
3. Set **Site URL** to `https://your-project.vercel.app`.

---

## Quick checklist

- [ ] Repo connected to Vercel  
- [ ] **Root Directory** = `ai_job_frontend` (if repo is monorepo)  
- [ ] `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` set  
- [ ] `NEXT_PUBLIC_BACKEND_URL` = your Render backend URL  
- [ ] `NEXT_PUBLIC_SITE_URL` = your Vercel URL (after first deploy)  
- [ ] Render backend has `FRONTEND_URL` / `ALLOWED_ORIGINS` pointing to Vercel URL  
