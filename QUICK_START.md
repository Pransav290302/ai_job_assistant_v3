# Quick Start Guide

## 🚀 Fastest Way to Run the Project

### Step 1: Initial Setup (One-time)

```bash
# 1. Setup Backend
setup_backend.bat

# 2. Setup Frontend  
setup_frontend.bat

# 3. Initialize Environment Files
init_env.bat
```

### Step 2: Configure API Keys

Edit `ai_job_backend/.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

Or use the helper script:
```bash
cd ai_job_backend
python add_api_key.py YOUR_API_KEY_HERE
```

### Step 3: Run the Project

**Option A: Run Both Together**
```bash
run_full_project.bat
```

**Option B: Run Separately**

Terminal 1 - Backend:
```bash
run_backend.bat
```

Terminal 2 - Frontend:
```bash
run_frontend.bat
```

## 📍 Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## ✅ Verify Setup

Run the setup checker:
```bash
check_setup.bat
```

## 🔧 Troubleshooting

### Backend won't start
- Check Python is installed: `python --version`
- Activate virtual environment: `ai_job_backend\venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Check Node.js is installed: `node --version`
- Install dependencies: `npm install`

### Database connection error
- For development, you can use SQLite (modify `api/database/__init__.py`)
- Or set up PostgreSQL and update `.env` with credentials

### API key errors
- Make sure `.env` file exists in `ai_job_backend/`
- Verify `OPENAI_API_KEY` is set correctly

## 📚 Full Documentation

See `SETUP_GUIDE.md` for detailed instructions.
