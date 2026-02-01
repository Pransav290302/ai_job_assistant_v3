# SQLite Database Setup Guide

SQLite is already configured in the project! It's the easiest database option for development - no installation required.

## ✅ Quick Setup (1 Step!)

### Step 1: Enable SQLite in .env

Edit your `ai_job_backend/.env` file and set:

```env
USE_SQLITE=true
```

That's it! SQLite is now enabled.

## 📋 Complete .env Configuration for SQLite

Your `.env` file should have:

```env
# Database Configuration
USE_SQLITE=true

# PostgreSQL variables are ignored when USE_SQLITE=true
# But you can leave them in the file
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
PG_DATABASE=ai_job_assistant
```

## 🚀 How It Works

1. **Database File Location:**
   - SQLite database file: `ai_job_backend/job_assistant.db`
   - Created automatically on first run
   - No setup needed!

2. **Automatic Creation:**
   - Tables are created automatically when you start the backend
   - No manual database creation required
   - No migrations needed

3. **Zero Configuration:**
   - No database server to install
   - No database to create
   - No credentials to configure
   - Just set `USE_SQLITE=true`

## 📝 Step-by-Step Setup

### Option 1: Using the Template (Recommended)

1. **Copy template to .env:**
   ```bash
   cd ai_job_backend
   copy env_template.txt .env
   ```

2. **Verify SQLite is enabled:**
   - Open `.env` file
   - Make sure `USE_SQLITE=true` is set

3. **Add your API key:**
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Start the backend:**
   ```bash
   python -m uvicorn api.main:app --reload
   ```

   The database file `job_assistant.db` will be created automatically!

### Option 2: Manual Setup

1. **Create .env file:**
   ```bash
   cd ai_job_backend
   # Create .env file manually
   ```

2. **Add this line:**
   ```env
   USE_SQLITE=true
   ```

3. **Add other required variables:**
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   PORT=8000
   ```

4. **Start the backend** - database will be created automatically!

## ✅ Verify SQLite is Working

### 1. Check Database File

After starting the backend, check if the database file was created:

```bash
cd ai_job_backend
dir job_assistant.db
```

You should see `job_assistant.db` file.

### 2. Check Backend Logs

When you start the backend, you should see:
```
INFO:     Application startup complete.
```

No database connection errors means SQLite is working!

### 3. Test API Endpoints

Visit http://localhost:8000/docs and try:
- `GET /health` - Should work
- `POST /auth/register` - Should create user in SQLite
- `POST /jobs/analyze` - Should save job to SQLite

## 🔄 Switching Between SQLite and PostgreSQL

### Use SQLite (Development):
```env
USE_SQLITE=true
```

### Use PostgreSQL (Production):
```env
USE_SQLITE=false
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
PG_DATABASE=ai_job_assistant
```

## 📁 Database File Location

- **File:** `ai_job_backend/job_assistant.db`
- **Location:** Same directory as your backend code
- **Size:** Grows as you add data
- **Backup:** Just copy the `.db` file!

## 🗑️ Reset Database (If Needed)

To start fresh:

1. **Stop the backend server**

2. **Delete the database file:**
   ```bash
   cd ai_job_backend
   del job_assistant.db
   ```

3. **Restart the backend:**
   ```bash
   python -m uvicorn api.main:app --reload
   ```

   A new empty database will be created automatically!

## 🔍 View Database Contents (Optional)

### Using SQLite Command Line

1. **Install SQLite** (if not already installed):
   - Download from: https://www.sqlite.org/download.html
   - Or use: `pip install sqlite3` (usually pre-installed with Python)

2. **Open database:**
   ```bash
   cd ai_job_backend
   sqlite3 job_assistant.db
   ```

3. **View tables:**
   ```sql
   .tables
   ```

4. **View users:**
   ```sql
   SELECT * FROM users;
   ```

5. **View jobs:**
   ```sql
   SELECT * FROM jobs;
   ```

6. **Exit:**
   ```sql
   .exit
   ```

### Using Python Script

Create `view_db.py`:
```python
import sqlite3

conn = sqlite3.connect('job_assistant.db')
cursor = conn.cursor()

# View tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# View users
cursor.execute("SELECT * FROM users;")
print("Users:", cursor.fetchall())

# View jobs
cursor.execute("SELECT * FROM jobs;")
print("Jobs:", cursor.fetchall())

conn.close()
```

## ⚠️ Important Notes

1. **File-based Database:**
   - SQLite stores everything in a single file
   - Keep backups of `job_assistant.db`
   - Don't delete it while the server is running

2. **Concurrent Access:**
   - SQLite works great for development
   - For production with many users, consider PostgreSQL

3. **No Server Required:**
   - SQLite doesn't need a separate database server
   - Perfect for local development
   - Easy to deploy (just include the .db file)

4. **Automatic Setup:**
   - Tables are created automatically
   - No manual SQL needed
   - Just start the server!

## 🎯 Quick Checklist

- [ ] Create `.env` file in `ai_job_backend/`
- [ ] Set `USE_SQLITE=true` in `.env`
- [ ] Add `OPENAI_API_KEY=your_key` in `.env`
- [ ] Start backend server
- [ ] Verify `job_assistant.db` file is created
- [ ] Test API endpoints

## 🆘 Troubleshooting

### Database file not created?

**Check:**
1. Is `USE_SQLITE=true` in `.env`?
2. Is the backend server running?
3. Check for errors in terminal output
4. Make sure you're in the `ai_job_backend` directory

### "Database is locked" error?

**Solution:**
- Make sure only one instance of the backend is running
- Close any database viewers
- Restart the backend server

### Want to use PostgreSQL instead?

**Change in .env:**
```env
USE_SQLITE=false
# Then configure PG_* variables
```

---

**That's it! SQLite is the easiest option - just set `USE_SQLITE=true` and you're done!** 🎉
