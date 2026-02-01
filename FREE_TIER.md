# Free Tier Demo Setup

Optimized for **Vercel** (frontend), **Render** (backend), and **Supabase** free tiers. Keeps resource usage low for demo use.

---

## What Gets Reduced

| Resource | Free Tier Setting | Saves |
|----------|-------------------|-------|
| **Render RAM** | Skip Playwright when `FREE_TIER=true` | ~150MB (Chromium) |
| **Render build** | Faster deploy (no Playwright install) | ~1–2 min |
| **DB connections** | Pool 2+3 instead of 5+10 | Supabase connection quota |
| **Backend workers** | 1 thread instead of 2 | ~50MB RAM |
| **Rate limits** | 20/min default | Fewer API calls, lower quota use |
| **Vercel build** | 2GB Node memory | Fits free tier limits |

---

## Environment Variables

### Render

| Variable | Value | Notes |
|----------|-------|-------|
| `FREE_TIER` | `true` | **Set in render.yaml** – skips Playwright, uses lighter pool |
| `SCRAPER_API_KEY` | *(optional)* | Use for scraping (1000 free/mo). Without it, use **paste job description** |
| `DATABASE_URL` | *(from Supabase or Render Postgres)* | Supabase free: 60 connections total |
| `OPENAI_API_KEY` | your key | Required for AI features |

**Scraping on free tier:** Use **paste job description** or add `SCRAPER_API_KEY`. Playwright is skipped when `FREE_TIER=true`.

### Vercel

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | Your Render URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key |

### Supabase

- Use default limits: 500MB DB, 2GB bandwidth, 50K auth users/month.
- One backend instance with `FREE_TIER=true` uses ~2–5 connections.

---

## Build Memory (Vercel)

`vercel.json` uses `--max-old-space-size=2048` (2GB). If builds fail with OOM:

1. In Vercel → Project → Settings → Environment Variables, add:
   - Name: `NODE_OPTIONS`
   - Value: `--max-old-space-size=3072`
2. Clear build cache and redeploy.

---

## When You Move Off Free Tier

1. **Render:** Set `FREE_TIER=false` in env.
2. Redeploy so Playwright is installed again.
3. Pool, workers, and rate limits will use production values.

---

## Quick Checklist

- [ ] Render: `FREE_TIER=true` (in render.yaml or dashboard)
- [ ] Render: `SCRAPER_API_KEY` optional – use paste if not set
- [ ] Vercel: `NEXT_PUBLIC_BACKEND_URL` = Render URL
- [ ] Supabase: credentials in Vercel
- [ ] Redeploy after any env change
