# Vercel Deployment

> **Demo / free tier?** See [FREE_TIER.md](../FREE_TIER.md) for lighter resource usage.

## Root Directory (Monorepo)

If your repo has both `ai_job_backend` and `ai_job_frontend`, set **Root Directory** to `ai_job_frontend` in Vercel → Project Settings → General.

## Build Configuration

The project uses Webpack (instead of Turbopack) and memory optimizations to avoid "JS heap out of memory" on Vercel. Configured in `vercel.json`, `package.json`, and `next.config.ts`.

**If build still fails with OOM:**
1. Add **NODE_OPTIONS** in Vercel → Settings → Environment Variables: `--max-old-space-size=3072` (or `6144` for large projects)
2. **Clear build cache:** Redeploy → uncheck "Use existing Build Cache"
3. Or add **VERCEL_FORCE_NO_BUILD_CACHE** = `1` temporarily

## Environment Variables Setup

When deploying to Vercel, you need to set the following environment variables in your Vercel project settings:

### Required Variables

1. **NEXT_PUBLIC_API_URL** or **NEXT_PUBLIC_BACKEND_URL**
   - Your Render backend service URL (either variable works; both are supported)
   - Example: `https://ai-job-backend.onrender.com`

2. **NEXT_PUBLIC_SUPABASE_URL**
   - Your **Supabase Cloud** project URL (not local Supabase)
   - Example: `https://your-project.supabase.co`
   - ⚠️ Do not use `localhost` or `127.0.0.1` – Vercel must use the hosted Supabase

3. **NEXT_PUBLIC_SUPABASE_ANON_KEY**
   - Your Supabase anonymous/public key
   - Found in Supabase Dashboard → Settings → API

4. **SUPABASE_SERVICE_ROLE_KEY** (required for auth callback, profile sync)
   - From Supabase Dashboard → Settings → API → `service_role` key
   - ⚠️ Server-side only – never expose to the browser

5. **NEXT_PUBLIC_SITE_URL** (recommended for OAuth)
   - Your production URL: `https://your-app.vercel.app`
   - Ensures Google/LinkedIn OAuth redirects work correctly on Vercel

### How to Set Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add each variable:
   - **Key**: Variable name (e.g., `NEXT_PUBLIC_API_URL`)
   - **Value**: Your actual value
   - **Environment**: Select which environments (Production, Preview, Development)
4. Click **Save**

### Important Notes

- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- Never commit `.env.local` to git (it's already in `.gitignore`)
- After adding environment variables, redeploy your application
- Vercel automatically provides `VERCEL_URL` environment variable

### Supabase: Use Cloud (Not Local)

Vercel does **not** use your local `.env.local`. It only uses variables from **Vercel Dashboard → Settings → Environment Variables**. Set:

- `NEXT_PUBLIC_SUPABASE_URL` = `https://your-project-ref.supabase.co` (from [Supabase Dashboard](https://supabase.com/dashboard))
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = anon key from Supabase
- `SUPABASE_SERVICE_ROLE_KEY` = service_role key from Supabase

Your local Supabase (`supabase start` / `localhost:54321`) is for development only. On Vercel, you must use the hosted project.

### Quick Setup Checklist

- [ ] Set `NEXT_PUBLIC_API_URL` or `NEXT_PUBLIC_BACKEND_URL` to your Render backend URL
- [ ] Set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` from **Supabase Cloud** (not localhost)
- [ ] Set `SUPABASE_SERVICE_ROLE_KEY` from Supabase Dashboard
- [ ] Set `NEXT_PUBLIC_SITE_URL` to your Vercel production URL (for Google/LinkedIn OAuth)
- [ ] Configure Supabase URL Configuration and Google/LinkedIn providers – see [OAUTH_SETUP.md](./OAUTH_SETUP.md)
- [ ] Redeploy after changing env vars
