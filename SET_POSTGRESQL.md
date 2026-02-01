# Quick PostgreSQL Configuration

## Option 1: Using Python Script (Easiest)

Run this command with your PostgreSQL password:

```bash
cd ai_job_backend
python set_postgresql_env.py YOUR_POSTGRES_PASSWORD
```

**Example:**
```bash
python set_postgresql_env.py mypassword123
```

This will automatically configure your `.env` file for PostgreSQL.

## Option 2: Manual Configuration

Edit `ai_job_backend/.env` file and add/update these lines:

```env
# Database Configuration - PostgreSQL
USE_SQLITE=false
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_actual_postgres_password_here
PG_DATABASE=ai_job_assistant
```

**Important:** Replace `your_actual_postgres_password_here` with your actual PostgreSQL password!

## Option 3: Using Batch Script (Interactive)

Run:
```bash
cd ai_job_backend
configure_postgresql.bat
```

Then enter your PostgreSQL password when prompted.

## After Configuration

1. **Make sure PostgreSQL is running**
2. **Create the database:**
   ```bash
   psql -U postgres
   CREATE DATABASE ai_job_assistant;
   \q
   ```
3. **Start the backend** - it will connect to PostgreSQL automatically!
