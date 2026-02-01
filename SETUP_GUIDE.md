# AI Job Assistant - Complete Setup Guide

This guide will help you set up and run the full project end-to-end.

## Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download Node.js](https://nodejs.org/)
3. **PostgreSQL** (optional - can use SQLite for development)
4. **API Key** - OpenAI API key

## Quick Start (Windows)

### Option 1: Automated Setup (Recommended)

1. **Setup Backend:**
   ```bash
   setup_backend.bat
   ```

2. **Setup Frontend:**
   ```bash
   setup_frontend.bat
   ```

3. **Run Full Project:**
   ```bash
   run_full_project.bat
   ```

### Option 2: Manual Setup

## Step-by-Step Setup

### 1. Backend Setup

```bash
cd ai_job_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Backend Environment

Create a `.env` file in `ai_job_backend/` folder:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
# Optional: Use a different base URL if using OpenAI-compatible API
# OPENAI_BASE_URL=https://api.openai.com/v1

# Database Configuration (PostgreSQL)
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
PG_DATABASE=ai_job_assistant

# Or use SQLite for development (modify database/__init__.py)

# Server Configuration
PORT=8000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000

# Auth Configuration
AUTH_SECRET_KEY=your-secret-key-change-in-production
AUTH_ALGORITHM=HS256

# Optional: Scraper Configuration
USE_SELENIUM=false
SELENIUM_HEADLESS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/job_assistant.log
```

**Quick OpenAI API Key Setup:**
```bash
cd ai_job_backend
python add_api_key.py YOUR_OPENAI_API_KEY_HERE
```

### 3. Database Setup

#### Option A: PostgreSQL (Production)

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Create database:
   ```sql
   CREATE DATABASE ai_job_assistant;
   ```
3. Update `.env` with your PostgreSQL credentials

#### Option B: SQLite (Development - Easier)

Modify `ai_job_backend/api/database/__init__.py`:

```python
# Change line 22 from:
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# To:
SQLALCHEMY_DATABASE_URL = "sqlite:///./job_assistant.db"
```

### 4. Frontend Setup

```bash
cd ai_job_frontend

# Install dependencies
npm install
```

### 5. Configure Frontend

Create a `.env.local` file in `ai_job_frontend/` folder:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration (for authentication)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Note:** The frontend uses Supabase for authentication. You can:
- Set up a free Supabase account at https://supabase.com
- Or modify the frontend to use the FastAPI JWT auth instead

### 6. Run the Project

#### Start Backend:
```bash
cd ai_job_backend
venv\Scripts\activate  # Windows
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend (in a new terminal):
```bash
cd ai_job_frontend
npm run dev
```

## Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## API Endpoints

### Data Science Endpoints (New)
- `POST /api/resume/analyze` - Analyze resume against job
- `POST /api/generate/answer` - Generate tailored answer
- `POST /api/job/scrape` - Scrape job description
- `GET /api/status` - Service status

### Existing Endpoints
- `POST /auth/register` - User registration
- `POST /auth/token` - User login
- `GET /auth/me` - Get current user
- `POST /jobs/analyze` - Analyze job posting
- `GET /health` - Health check

## Troubleshooting

### Backend Issues

1. **Database Connection Error:**
   - Check PostgreSQL is running
   - Verify credentials in `.env`
   - Or switch to SQLite for development

2. **API Key Error:**
   - Make sure `.env` file exists
   - Verify `AZURE_DEEPSEEK_API_KEY` is set
   - Run `python add_api_key.py YOUR_KEY`

3. **Import Errors:**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` again

### Frontend Issues

1. **Cannot connect to backend:**
   - Check backend is running on port 8000
   - Verify `NEXT_PUBLIC_API_URL` in `.env.local`
   - Check CORS settings in backend

2. **Build Errors:**
   - Delete `node_modules` and `.next` folder
   - Run `npm install` again

## Testing the Integration

1. **Test Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Data Science Status:**
   ```bash
   curl http://localhost:8000/api/status
   ```

3. **Test Resume Analysis (example):**
   ```bash
   curl -X POST http://localhost:8000/api/resume/analyze \
     -H "Content-Type: application/json" \
     -d '{"resume_text": "Software Engineer with 5 years experience...", "job_url": "https://linkedin.com/jobs/..."}'
   ```

## Next Steps

- Configure your API keys
- Set up database (PostgreSQL or SQLite)
- Run both servers
- Access the frontend at http://localhost:3000
- Test the API at http://localhost:8000/docs

## Support

If you encounter issues:
1. Check logs in `ai_job_backend/logs/` (if configured)
2. Check browser console for frontend errors
3. Check terminal output for backend errors
4. Verify all environment variables are set correctly
