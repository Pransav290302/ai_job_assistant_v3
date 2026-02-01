# 🚀 Quick PostgreSQL Setup Guide

## ⚡ Fast Setup (5 Steps)

### Step 1: Install PostgreSQL

**Windows:**
- Download: https://www.postgresql.org/download/windows/
- Run installer
- **Remember the password** you set for `postgres` user
- Default port `5432` is fine

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database

Open terminal/command prompt and run:

```bash
psql -U postgres
```

Enter your PostgreSQL password, then:

```sql
CREATE DATABASE ai_job_assistant;
\q
```

### Step 3: Update .env File

Edit `ai_job_backend/.env` and set:

```env
# Disable SQLite, use PostgreSQL
USE_SQLITE=false

# PostgreSQL Connection (replace with your actual password!)
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_actual_postgres_password
PG_DATABASE=ai_job_assistant
```

**Important:** Replace `your_actual_postgres_password` with the password you set during PostgreSQL installation!

### Step 4: Verify PostgreSQL is Running

**Windows:**
- Open Services (services.msc)
- Find "PostgreSQL" service
- Make sure it's "Running"

**Linux/Mac:**
```bash
sudo systemctl status postgresql
# or
brew services list
```

### Step 5: Start Backend

```bash
cd ai_job_backend
python -m uvicorn api.main:app --reload
```

If you see "Application startup complete" → ✅ Success!

## ✅ Quick Checklist

- [ ] PostgreSQL installed
- [ ] PostgreSQL service running
- [ ] Database `ai_job_assistant` created
- [ ] `.env` has `USE_SQLITE=false`
- [ ] `.env` has correct `PG_PASSWORD`
- [ ] Backend starts without errors

## 🆘 Common Issues

**"password authentication failed"**
- Check password in `.env` matches PostgreSQL password

**"database does not exist"**
- Run: `CREATE DATABASE ai_job_assistant;`

**"connection refused"**
- Make sure PostgreSQL service is running

---

**See `POSTGRESQL_SETUP.md` for detailed guide!**
