# Deploy Your Full App 100% Free (No Blueprint, No Paid Plans)

You can run the whole app on **free tiers** only:

| Part | Where | Free tier |
|------|--------|-----------|
| **Frontend** | **Vercel** | Free (Hobby) – Next.js deploy |
| **Backend** | **Render** | Free Web Service (1 free service; sleeps after ~15 min inactivity) |
| **Auth + DB** | **Supabase** | Free tier (you already use it in the frontend) |

**Do not use Blueprint** (it can be paid). Use **Web Service** on Render — that’s free.

---

# Step 1: Deploy Backend on Render (Free Web Service)

Your repo must be on **GitHub** first.

---

## 1. Open Render and sign in

1. Go to **https://render.com**
2. Click **Get Started** or **Sign In**
3. Sign in with **GitHub**

---

## 2. Create a free Web Service (not Blueprint)

1. Click **New +** (top right)
2. Click **Web Service** (do **not** choose Blueprint)
3. If your repo isn’t connected yet:
   - Click **Connect a repository** or **Connect account**
   - Authorize Render for GitHub and select your **ai_job_assistant_v3** repo
4. After connecting, you’ll see **Create a new Web Service**:
   - **Repository**: select **ai_job_assistant_v3** (or your repo name)
   - **Name**: e.g. **ai-job-backend**
   - **Region**: pick one close to you
   - **Branch**: **main** (or your default branch)
   - **Root Directory**: click **Edit** and enter **`ai_job_backend`**
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Scroll to **Instance Type**
   - Select **Free** (0 USD/month)
6. Click **Create Web Service**

Render will build and deploy. The first deploy may take a few minutes.

---

## 3. Add environment variables

1. After the service is created, go to the **Environment** tab (left sidebar)
2. Click **Add Environment Variable** and add:

| Key | Value |
|-----|--------|
| `OPENAI_API_KEY` | Your OpenAI API key (starts with `sk-...`) |
| `AUTH_SECRET_KEY` | Random string (e.g. run `openssl rand -base64 32` in a terminal) |
| `FRONTEND_URL` | For now use `http://localhost:3000` — change to your Vercel URL after you deploy the frontend |
| `ALLOWED_ORIGINS` | Same as `FRONTEND_URL` — update to your Vercel URL later |

**Database (choose one):**

- **Easiest for free:**  
  Add **`USE_SQLITE`** = **`true`**  
  (No PostgreSQL; data may not persist forever on free tier, but the app will run.)

- **If you want PostgreSQL later:**  
  Create a free PostgreSQL database on Render (New + → PostgreSQL), then add `USE_SQLITE=false` and the `PG_*` vars from your backend’s `env_template.txt`.

3. Click **Save Changes**. Render will redeploy with the new env vars.

---

## 4. Copy your backend URL

1. When the deploy is **Live** (green), the URL is at the top of the page, e.g.  
   **https://ai-job-backend-xxxx.onrender.com**
2. **Copy this URL** — you’ll use it in Vercel as **NEXT_PUBLIC_API_URL**.

**Free tier note:** The service sleeps after ~15 minutes of no traffic. The first request after that may take 30–60 seconds (cold start). That’s normal on the free plan.

---

# Step 2: Deploy Frontend on Vercel (Free)

1. Go to **https://vercel.com** and sign in with GitHub.
2. **Add New → Project** → import your **ai_job_assistant_v3** repo.
3. **Root Directory**: click **Edit** → choose **`ai_job_frontend`** → **Continue**.
4. **Environment Variables** — add (use your real values):

   | Name | Value |
   |------|--------|
   | `NEXT_PUBLIC_API_URL` | Your Render backend URL (e.g. `https://ai-job-backend-xxxx.onrender.com`) |
   | `NEXT_PUBLIC_SUPABASE_URL` | From Supabase dashboard |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | From Supabase dashboard |
   | `SUPABASE_SERVICE_ROLE_KEY` | From Supabase (keep secret) |
   | `NEXTAUTH_SECRET` | Random string (e.g. `openssl rand -base64 32`) |
   | `NEXTAUTH_URL` | Your Vercel URL (e.g. `https://your-app.vercel.app`) |

5. Click **Deploy**. Wait for the build to finish.
6. Copy your Vercel URL (e.g. **https://your-app.vercel.app**).

---

# Step 3: Connect backend and frontend

1. **Render** (backend):  
   - **Environment** tab → set **FRONTEND_URL** and **ALLOWED_ORIGINS** to your Vercel URL (e.g. `https://your-app.vercel.app`).  
   - Save so the backend allows requests from your frontend (CORS).

2. **Supabase** (if you use auth):  
   - Dashboard → Authentication → URL Configuration.  
   - Add your Vercel URL to **Site URL** and **Redirect URLs** (e.g. `https://your-app.vercel.app/auth/callback`).

---

## Quick checklist (all free)

- [ ] Render: **Web Service** (not Blueprint), **Free** instance, Root Directory **ai_job_backend**
- [ ] Render env vars: **OPENAI_API_KEY**, **AUTH_SECRET_KEY**, **FRONTEND_URL**, **ALLOWED_ORIGINS**, **USE_SQLITE=true** (or PG vars)
- [ ] Backend URL copied from Render
- [ ] Vercel: Root Directory **ai_job_frontend**, env vars including **NEXT_PUBLIC_API_URL** = Render URL
- [ ] **FRONTEND_URL** / **ALLOWED_ORIGINS** on Render set to your Vercel URL

That’s it — full app deployed for free.
