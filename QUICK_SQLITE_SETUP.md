# 🚀 Quick SQLite Setup (30 Seconds!)

SQLite is the **easiest** database option - no installation needed!

## ⚡ One-Line Setup

### Method 1: Automated Script
```bash
cd ai_job_backend
setup_sqlite.bat
```

### Method 2: Manual (Even Faster!)

1. **Open `ai_job_backend/.env` file**

2. **Add or verify this line:**
   ```env
   USE_SQLITE=true
   ```

3. **Done!** ✅

## 🎯 That's It!

When you start the backend:
- ✅ Database file (`job_assistant.db`) will be created automatically
- ✅ Tables will be created automatically
- ✅ No configuration needed
- ✅ No installation required

## 📝 Complete .env for SQLite

```env
# Database - SQLite (Easiest!)
USE_SQLITE=true

# API Key (Required)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Server
PORT=8000
FRONTEND_URL=http://localhost:3000
```

## ✅ Verify It's Working

1. **Start backend:**
   ```bash
   cd ai_job_backend
   python -m uvicorn api.main:app --reload
   ```

2. **Check for database file:**
   ```bash
   dir job_assistant.db
   ```
   You should see the file created!

3. **Test API:**
   - Visit http://localhost:8000/docs
   - Try `POST /auth/register` - should save to SQLite!

## 🆘 Troubleshooting

**Database not created?**
- Make sure `USE_SQLITE=true` in `.env`
- Check backend started without errors
- Look for `job_assistant.db` in `ai_job_backend/` folder

**Want more details?**
- See `SQLITE_SETUP.md` for complete guide

---

**SQLite = Zero Setup, Just Works!** 🎉
