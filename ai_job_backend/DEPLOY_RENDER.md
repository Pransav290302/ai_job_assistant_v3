# Deploy Backend to Render

## 1. Push your code

Ensure your repo (with `render.yaml` at the **root** and `ai_job_backend/` folder) is pushed to GitHub or GitLab.

## 2. Create a Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. **New** → **Web Service**
3. Connect your repository (`ai_job_assistant_v3` or your repo name)
4. Render may **auto-detect** the service from `render.yaml`. If so, confirm:
   - **Root Directory:** leave empty (render.yaml is at repo root)
   - Or set **Root Directory:** `ai_job_backend` only if you're configuring manually without render.yaml

### If using render.yaml (recommended)

5. Render will use the **Blueprint** from `render.yaml`:
   - **Name:** ai-job-backend
   - **Root Directory:** ai_job_backend
   - **Build Command:** `pip install -r requirements.txt && ( [ "$FREE_TIER" = "true" ] || playwright install chromium )`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`

### If configuring manually (no render.yaml)

- **Environment:** Python 3
- **Root Directory:** `ai_job_backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

## 3. Set environment variables

In the Render service → **Environment** tab, add:

| Key | Required | Notes |
|-----|----------|--------|
| `OPENAI_API_KEY` | Yes | Your Azure/OpenAI/DeepSeek API key |
| `OPENAI_BASE_URL` | If using Azure | e.g. `https://YOUR-RESOURCE.services.ai.azure.com/openai/v1` |
| `SUPABASE_URL` | Yes (for matches) | e.g. `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes (for matches) | From Supabase → Settings → API |
| `AUTH_SECRET_KEY` | Yes | Generate a long random string (e.g. `openssl rand -hex 32`) |
| `FRONTEND_URL` | Yes | Your frontend URL, e.g. `https://your-app.vercel.app` or `http://localhost:3000` |
| `ALLOWED_ORIGINS` | Optional | Comma-separated origins; defaults to FRONTEND_URL |
| `FREE_TIER` | Optional | Set to `true` to skip Playwright install (saves RAM; use paste/ScraperAPI for job scrape) |
| `BROWSERLESS_URL` | Optional | For scraping; e.g. `wss://chrome.browserless.io?token=YOUR_TOKEN` |

Database (only if you use Postgres on Render):

- `DATABASE_URL` — or use `PG_HOST`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE`, `PG_PORT` if you prefer.

## 4. Deploy

- Click **Create Web Service** (or **Save** if editing). Render will build and deploy.
- After deploy, your API URL will be like: `https://ai-job-backend.onrender.com`
- Test: open `https://ai-job-backend.onrender.com/health` — should return `{"status":"online",...}`

## 5. Use the backend URL in the frontend

In your frontend (e.g. Vercel env or `.env.local`):

```env
NEXT_PUBLIC_BACKEND_URL=https://ai-job-backend.onrender.com
```

(or whatever URL Render shows for your service).

## Troubleshooting

- **Build fails:** Check the build log; often a missing dependency or wrong Python version. Render uses `PYTHON_VERSION=3.12` from render.yaml.
- **Health check fails:** Ensure `PORT` is not set manually; Render injects `$PORT`. Start command must use `--port $PORT`.
- **CORS errors from frontend:** Set `FRONTEND_URL` and `ALLOWED_ORIGINS` to your real frontend URL(s).
- **Cold starts:** Free tier spins down after inactivity; first request may take 30–60 seconds.
