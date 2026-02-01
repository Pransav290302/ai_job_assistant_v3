# PostgreSQL Database Setup Guide

Complete guide to set up PostgreSQL for the AI Job Assistant project.

## 📋 Prerequisites

- Windows, macOS, or Linux
- Admin/root access for installation

## 🚀 Step-by-Step Setup

### Step 1: Install PostgreSQL

#### Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation:
   - Remember the password you set for the `postgres` user
   - Default port: `5432` (keep this)
   - Default installation location is fine
4. Complete the installation

#### macOS:
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 2: Verify PostgreSQL Installation

```bash
# Check if PostgreSQL is running
psql --version

# On Windows, you can also check Services:
# Services → PostgreSQL → Should be "Running"
```

### Step 3: Create Database

#### Option A: Using psql Command Line

1. **Open PostgreSQL command line:**
   ```bash
   # Windows: Open "SQL Shell (psql)" from Start Menu
   # Or use:
   psql -U postgres
   ```

2. **Enter your password** (the one you set during installation)

3. **Create the database:**
   ```sql
   CREATE DATABASE ai_job_assistant;
   ```

4. **Verify it was created:**
   ```sql
   \l
   ```
   You should see `ai_job_assistant` in the list.

5. **Exit:**
   ```sql
   \q
   ```

#### Option B: Using pgAdmin (GUI - Windows/Mac)

1. Open **pgAdmin** (installed with PostgreSQL)
2. Connect to your PostgreSQL server
3. Right-click on **Databases** → **Create** → **Database**
4. Name: `ai_job_assistant`
5. Click **Save**

### Step 4: Configure .env File

Edit `ai_job_backend/.env` file:

```env
# Database Configuration - PostgreSQL
USE_SQLITE=false

# PostgreSQL Connection Settings
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_postgres_password_here
PG_DATABASE=ai_job_assistant
```

**Important:** Replace `your_postgres_password_here` with the actual password you set during PostgreSQL installation!

### Step 5: Test Connection

1. **Start the backend:**
   ```bash
   cd ai_job_backend
   python -m uvicorn api.main:app --reload
   ```

2. **Check for errors:**
   - If you see "Application startup complete" → ✅ Success!
   - If you see connection errors → Check your password and database name

3. **Verify tables were created:**
   ```bash
   psql -U postgres -d ai_job_assistant -c "\dt"
   ```
   You should see `users` and `jobs` tables.

## 🔧 Configuration Details

### .env File Settings

```env
# Disable SQLite
USE_SQLITE=false

# PostgreSQL Connection
PG_HOST=localhost          # Usually localhost
PG_PORT=5432               # Default PostgreSQL port
PG_USER=postgres           # Default superuser
PG_PASSWORD=your_password  # Your PostgreSQL password
PG_DATABASE=ai_job_assistant  # Database name
```

### Connection String Format

The code automatically builds this connection string:
```
postgresql://postgres:password@localhost:5432/ai_job_assistant
```

## ✅ Verification Checklist

- [ ] PostgreSQL is installed
- [ ] PostgreSQL service is running
- [ ] Database `ai_job_assistant` is created
- [ ] `.env` file has `USE_SQLITE=false`
- [ ] `.env` file has correct PostgreSQL credentials
- [ ] Backend starts without database errors
- [ ] Tables are created automatically

## 🧪 Test the Connection

### Method 1: Using Python

```bash
cd ai_job_backend
python
```

```python
from api.database import engine
from sqlalchemy import text

# Test connection
with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone())
```

### Method 2: Using psql

```bash
psql -U postgres -d ai_job_assistant
```

Then:
```sql
SELECT version();
\dt  -- List tables
```

## 🆘 Troubleshooting

### Error: "password authentication failed"

**Solution:**
1. Check your password in `.env` matches PostgreSQL password
2. Try resetting PostgreSQL password:
   ```sql
   ALTER USER postgres PASSWORD 'new_password';
   ```
3. Update `.env` with the new password

### Error: "database does not exist"

**Solution:**
1. Create the database:
   ```sql
   CREATE DATABASE ai_job_assistant;
   ```

### Error: "connection refused"

**Solution:**
1. Check PostgreSQL is running:
   - Windows: Services → PostgreSQL → Start
   - Linux/Mac: `sudo systemctl start postgresql`
2. Check port 5432 is not blocked by firewall
3. Verify `PG_HOST` and `PG_PORT` in `.env`

### Error: "role does not exist"

**Solution:**
1. Use the default `postgres` user
2. Or create a new user:
   ```sql
   CREATE USER your_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ai_job_assistant TO your_user;
   ```

### Error: "could not connect to server"

**Solution:**
1. Make sure PostgreSQL service is running
2. Check if port 5432 is correct
3. Verify `PG_HOST=localhost` (not 127.0.0.1)

## 🔄 Switching from SQLite to PostgreSQL

If you were using SQLite and want to switch:

1. **Stop the backend server**

2. **Update .env:**
   ```env
   USE_SQLITE=false
   PG_HOST=localhost
   PG_PORT=5432
   PG_USER=postgres
   PG_PASSWORD=your_password
   PG_DATABASE=ai_job_assistant
   ```

3. **Create PostgreSQL database** (see Step 3 above)

4. **Start backend** - tables will be created in PostgreSQL

5. **Note:** Data from SQLite won't automatically transfer. You'll need to export/import if needed.

## 📊 Database Management

### View Tables
```sql
\dt
```

### View Users Table
```sql
SELECT * FROM users;
```

### View Jobs Table
```sql
SELECT * FROM jobs;
```

### Backup Database
```bash
pg_dump -U postgres ai_job_assistant > backup.sql
```

### Restore Database
```bash
psql -U postgres ai_job_assistant < backup.sql
```

## 🎯 Quick Setup Script

Create `setup_postgresql.bat` (Windows):

```batch
@echo off
echo Setting up PostgreSQL configuration...
echo.
echo Please enter your PostgreSQL password:
set /p PG_PASSWORD="Password: "

(
echo USE_SQLITE=false
echo PG_HOST=localhost
echo PG_PORT=5432
echo PG_USER=postgres
echo PG_PASSWORD=%PG_PASSWORD%
echo PG_DATABASE=ai_job_assistant
) >> .env

echo.
echo PostgreSQL configuration added to .env file!
echo Make sure the database 'ai_job_assistant' exists.
pause
```

## ✅ Success Indicators

When PostgreSQL is working correctly:

1. ✅ Backend starts without database errors
2. ✅ You see "Application startup complete"
3. ✅ Tables are created automatically
4. ✅ You can register users via API
5. ✅ Jobs are saved to database

---

**PostgreSQL is now configured!** 🎉
