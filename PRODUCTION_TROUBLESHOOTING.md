# Production Troubleshooting (Vercel + Render)

If the **AI Assistant** (scrape, analyze, generate) throws errors on production, check this checklist.

## Quick Checklist

### Vercel (Frontend)
| Variable | Required | Example |
|----------|----------|---------|
| `NEXT_PUBLIC_BACKEND_URL` or `NEXT_PUBLIC_API_URL` | ✅ Yes | `https://ai-job-backend.onrender.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ Yes | From Supabase Dashboard |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ Yes | From Supabase Dashboard |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ Yes | From Supabase Dashboard |

**Important:** Use your **actual** Render URL (from Render Dashboard → your service → URL).

### Render (Backend)
| Variable | Required | Example |
|----------|----------|---------|
| `FRONTEND_URL` | ✅ Yes | `https://your-app.vercel.app` |
| `ALLOWED_ORIGINS` | ✅ Yes | `https://your-app.vercel.app` (or comma-separated) |
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI key |
| `AUTH_SECRET_KEY` | ✅ Yes | Random secret (e.g. `openssl rand -base64 32`) |
| `BROWSERLESS_URL` | ✅ For LinkedIn | `wss://chrome.browserless.io?token=YOUR_TOKEN` from browserless.io |
| `FREE_TIER` | Auto | `true` = Playwright skipped, ScraperAPI required for LinkedIn |

## Common Errors

### 1. "Backend unreachable" / "Request timed out" / 502
- **Cause:** `NEXT_PUBLIC_BACKEND_URL` not set on Vercel, or Render backend is down/cold.
- **Fix:**
  - Set `NEXT_PUBLIC_BACKEND_URL` in Vercel → Settings → Environment Variables
  - Redeploy Vercel
  - Render free tier cold-starts in ~50–90s — wait 1 min and try again

### 2. LinkedIn URL scraping fails
- **Cause:** `BROWSERLESS_URL` not set on Render.
- **Fix:** Add `BROWSERLESS_URL=wss://chrome.browserless.io?token=YOUR_TOKEN` in Render → Environment (get token at browserless.io, 6 hrs free/month)
- **Workaround:** Paste the job description manually (80+ chars) and click "Scrape job description"

### 3. Paste description also fails
- **Cause:** If both scrape and paste fail, the backend is likely unreachable.
- **Fix:** Same as #1 — ensure `NEXT_PUBLIC_BACKEND_URL` is set on Vercel and Render is running
- **Test backend directly:**
  ```bash
  curl -X POST https://YOUR-RENDER-URL.onrender.com/api/job/scrape \
    -H "Content-Type: application/json" \
    -d '{"job_description": "Paste a long job description here (200+ chars) to test..."}'
  ```

### 4. "Analysis failed" / "Answer generation failed"
- **Cause:** `OPENAI_API_KEY` missing on Render, or API quota/rate limit.
- **Fix:** Add `OPENAI_API_KEY` in Render → Environment

### 5. CORS / "Failed to fetch"
- **Cause:** `ALLOWED_ORIGINS` on Render doesn't include your Vercel URL.
- **Fix:** Set `ALLOWED_ORIGINS=https://your-app.vercel.app` (and add preview URLs if needed)

## Test Backend Health

```bash
curl https://YOUR-RENDER-URL.onrender.com/health
# Should return: {"status":"ok"} or similar
```

## Redeploy After Changes

- **Vercel:** Deployments → Redeploy
- **Render:** Manual Deploy or push to trigger auto-deploy

Environment variables require a redeploy to take effect.
