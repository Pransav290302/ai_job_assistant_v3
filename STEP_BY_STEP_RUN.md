# Step-by-Step Guide to Run the Project

Follow these steps in order to successfully run the full project.

## ✅ Step 1: Verify Prerequisites

### Check Python Installation
```bash
python --version
```
**Expected:** Python 3.8 or higher  
**If not installed:** Download from https://www.python.org/downloads/

### Check Node.js Installation
```bash
node --version
npm --version
```
**Expected:** Node.js 18+ and npm  
**If not installed:** Download from https://nodejs.org/

---

## ✅ Step 2: Setup Backend

### 2.1 Navigate to Backend Folder
```bash
cd ai_job_backend
```

### 2.2 Create Virtual Environment
```bash
python -m venv venv
```

### 2.3 Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**You should see `(venv)` in your terminal prompt.**

### 2.4 Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.5 Install Playwright Browsers
```bash
playwright install chromium
```

**This may take a few minutes. Wait for it to complete.**

---

## ✅ Step 3: Configure Backend Environment

### 3.1 Create .env File
```bash
# If you're in ai_job_backend folder:
copy env_template.txt .env
```

**Or manually create `.env` file in `ai_job_backend/` folder**

### 3.2 Add Your API Key

**Option A: Using the helper script**
```bash
python add_api_key.py YOUR_API_KEY_HERE
```

**Option B: Manually edit .env file**
Open `ai_job_backend/.env` and set:
```env
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

**To get an OpenAI API key:**
- Visit: https://platform.openai.com
- Sign up or log in
- Go to: https://platform.openai.com/api-keys
- Create a new secret key

### 3.3 Configure Database (Choose One)

**Option A: Use SQLite (Easiest - Recommended for Development) ✅**

SQLite is already configured! Just set this in your `.env` file:

```env
USE_SQLITE=true
```

**That's it!** No installation, no setup needed. The database file will be created automatically when you start the backend.

**Quick Setup Script:**
```bash
cd ai_job_backend
setup_sqlite.bat
```

Or manually:
1. Open `.env` file
2. Make sure `USE_SQLITE=true` is set
3. Start backend - database will be created automatically!

**Database file location:** `ai_job_backend/job_assistant.db` (created automatically)

**Option B: Use PostgreSQL (For Production)**

1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create database:
   ```sql
   CREATE DATABASE ai_job_assistant;
   ```
3. Update `.env` file:
   ```env
   USE_SQLITE=false
   PG_HOST=localhost
   PG_PORT=5432
   PG_USER=postgres
   PG_PASSWORD=your_postgres_password
   PG_DATABASE=ai_job_assistant
   ```

---

## ✅ Step 4: Setup Frontend

### 4.1 Navigate to Frontend Folder
```bash
# From project root:
cd ai_job_frontend
```

### 4.2 Install Frontend Dependencies
```bash
npm install
```

**This may take 2-5 minutes. Wait for it to complete.**

### 4.3 Create Frontend Environment File

Create `.env.local` file in `ai_job_frontend/` folder:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** If using Supabase for auth, also add:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
```

---

## ✅ Step 5: Verify Setup

### 5.1 Check Backend Setup
```bash
cd ai_job_backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac

python -c "import fastapi; print('Backend OK')"
```

### 5.2 Check Frontend Setup
```bash
cd ai_job_frontend
npm list next
```

---

## ✅ Step 6: Start the Backend Server

### 6.1 Open Terminal 1

```bash
cd ai_job_backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Backend is running! Keep this terminal open.**

### 6.2 Test Backend (Optional)

Open browser and visit:
- http://localhost:8000/docs - API documentation
- http://localhost:8000/health - Health check

---

## ✅ Step 7: Start the Frontend Server

### 7.1 Open Terminal 2 (New Terminal Window)

```bash
cd ai_job_frontend
npm run dev
```

**You should see:**
```
  ▲ Next.js 16.x.x
  - Local:        http://localhost:3000
  - Ready in X seconds
```

**✅ Frontend is running! Keep this terminal open.**

---

## ✅ Step 8: Access the Application

### 8.1 Open Your Browser

Visit: **http://localhost:3000**

You should see the AI Job Assistant frontend!

### 8.2 Test the Integration

1. **Check Backend API:**
   - Visit http://localhost:8000/docs
   - Try the `/health` endpoint
   - Try the `/api/status` endpoint

2. **Test Data Science Features:**
   - Visit http://localhost:8000/docs
   - Try `POST /api/job/scrape` with a job URL
   - Try `POST /api/resume/analyze` with resume text and job URL

---

## 🎉 Success! Your Project is Running!

### What You Should See:

✅ **Backend Terminal:**
- Server running on port 8000
- No error messages
- "Application startup complete"

✅ **Frontend Terminal:**
- Next.js dev server running
- "Ready" status
- No build errors

✅ **Browser:**
- Frontend loads at http://localhost:3000
- Can navigate pages
- Can make API calls

---

## 🔧 Troubleshooting Common Issues

### Issue: Backend won't start

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
cd ai_job_backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Error: "Database connection failed"**
- If using PostgreSQL: Make sure PostgreSQL is running
- Or switch to SQLite (see Step 3.3)

**Error: "Port 8000 already in use"**
```bash
# Find and kill the process using port 8000
# Or change port in .env: PORT=8001
```

### Issue: Frontend won't start

**Error: "Port 3000 already in use"**
```bash
# Kill the process or use different port
npm run dev -- -p 3001
```

**Error: "Cannot connect to backend"**
- Check backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`

### Issue: API calls fail

**Error: "API key not found"**
- Check `.env` file exists in `ai_job_backend/`
- Verify `OPENAI_API_KEY` is set
- Restart backend after adding API key

---

## 📝 Quick Reference Commands

### Start Backend:
```bash
cd ai_job_backend
venv\Scripts\activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend:
```bash
cd ai_job_frontend
npm run dev
```

### Stop Servers:
- Press `Ctrl+C` in each terminal

---

## 🚀 Next Steps After Running

1. **Test API Endpoints:**
   - Visit http://localhost:8000/docs
   - Try all the endpoints

2. **Explore Frontend:**
   - Navigate through all pages
   - Test user registration/login
   - Try job analysis features

3. **Integrate Features:**
   - Connect frontend to new datascientist APIs
   - Test resume analysis
   - Test answer generation

---

## ✅ Checklist

Before running, make sure:
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] `.env` file created with API key
- [ ] `.env.local` file created for frontend
- [ ] Database configured (PostgreSQL or SQLite)
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000

---

**You're all set! Follow these steps and your project will be running! 🎉**
