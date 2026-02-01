# 🚀 PostgreSQL Quick Start

## Step 1: Install PostgreSQL

**Windows:**
1. Download: https://www.postgresql.org/download/windows/
2. Install (remember your password!)
3. Default port 5432 is fine

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt install postgresql
sudo systemctl start postgresql
```

## Step 2: Create Database

```bash
psql -U postgres
```

Then:
```sql
CREATE DATABASE ai_job_assistant;
\q
```

## Step 3: Configure .env

Edit `ai_job_backend/.env`:

```env
USE_SQLITE=false
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_postgres_password
PG_DATABASE=ai_job_assistant
```

**Or use the helper script:**
```bash
cd ai_job_backend
configure_postgresql.bat
```

## Step 4: Start Backend

```bash
python -m uvicorn api.main:app --reload
```

✅ Done! Tables created automatically.

---

**See `POSTGRESQL_SETUP.md` for detailed guide!**
