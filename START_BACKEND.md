# 🚀 Starting the Backend Server

## Quick Start

### Method 1: Using the Batch Script (Easiest)

```bash
cd ai_job_backend
run_backend.bat
```

### Method 2: Manual Start

**Step 1: Navigate to backend folder**
```bash
cd ai_job_backend
```

**Step 2: Activate virtual environment**
```bash
venv\Scripts\activate
```

**Step 3: Start the server**
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ What You Should See

When the backend starts successfully, you'll see:

```
INFO:     Will watch for changes in these directories: ['C:\\...\\ai_job_backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🌐 Access Points

Once running:
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## ⚠️ Common Issues

### Issue: "Module not found"
**Solution:**
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Database connection failed"
**Solution:**
- If using PostgreSQL: Make sure PostgreSQL is running and credentials in `.env` are correct
- If using SQLite: Make sure `USE_SQLITE=true` in `.env`

### Issue: "Port 8000 already in use"
**Solution:**
- Close other applications using port 8000
- Or change port in `.env`: `PORT=8001`

### Issue: "OPENAI_API_KEY not found"
**Solution:**
- Make sure `.env` file exists in `ai_job_backend/`
- Add: `OPENAI_API_KEY=your_key_here`

## 🔍 Verify Backend is Running

Open browser and visit:
- http://localhost:8000/health
- Should return: `{"status": "online"}`

Or visit:
- http://localhost:8000/docs
- Should show API documentation

---

**The backend is now running!** 🎉
