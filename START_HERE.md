# 🚀 START HERE - Quick Run Guide

## ⚡ Fastest Way to Run (5 Minutes)

### Step 1: Setup Backend (2 min)
```bash
cd ai_job_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Add OpenAI API Key (1 min)
```bash
# Create .env file
copy env_template.txt .env

# Add your OpenAI API key (edit .env file or use):
python add_api_key.py YOUR_OPENAI_API_KEY_HERE
```

### Step 3: Configure Database

**Option A: SQLite (Easiest - No installation)**
Edit `ai_job_backend/.env`:
```env
USE_SQLITE=true
```

**Option B: PostgreSQL (Production-ready)**
1. Install PostgreSQL: https://www.postgresql.org/download/
2. Create database: `CREATE DATABASE ai_job_assistant;`
3. Edit `ai_job_backend/.env`:
```env
USE_SQLITE=false
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_postgres_password
PG_DATABASE=ai_job_assistant
```

See `POSTGRESQL_SETUP.md` for detailed PostgreSQL setup.

### Step 4: Setup Frontend (1 min)
```bash
cd ..\ai_job_frontend
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Run Both Servers (30 sec)

**Terminal 1 - Backend:**
```bash
cd ai_job_backend
venv\Scripts\activate
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ai_job_frontend
npm run dev
```

### Step 6: Open Browser
🌐 **http://localhost:3000**

---

## 📋 Detailed Steps

See `STEP_BY_STEP_RUN.md` for complete instructions.

---

## ✅ Quick Checklist

- [ ] Python installed (`python --version`)
- [ ] Node.js installed (`node --version`)
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] API key added to `.env`
- [ ] Database configured (SQLite or PostgreSQL)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000

---

## 🆘 Need Help?

1. Run `check_setup.bat` to verify setup
2. Check `STEP_BY_STEP_RUN.md` for detailed guide
3. Check `SETUP_GUIDE.md` for troubleshooting

---

**Ready? Start with Step 1 above! 🎯**
