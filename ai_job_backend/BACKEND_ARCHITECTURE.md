# Backend Architecture – AI Job Assistant

This document describes the high-level backend architecture, data flow, and production operations for the AI Job Assistant backend (Phase 1 & 2 of the Backend Engineer assignment).

---

## 1. System Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        FE[Frontend / Web App]
    end

    subgraph API["API Layer"]
        GW[FastAPI Application]
        GW --> R_auth["/auth (register, token, me)"]
        GW --> R_users["/api/users (create, get)"]
        GW --> R_resume["/api/resume/analyze"]
        GW --> R_generate["/api/generate/answer"]
        GW --> R_health["/health, /api/health"]
        GW --> R_status["/api/status"]
    end

    subgraph Core["Core Logic (Agent / Data Science)"]
        Agent[Agent Orchestration]
        Agent --> Scraper[Job Scraper]
        Agent --> ResumeAnalyzer[Resume Analyzer]
        Agent --> AnswerGen[Answer Generator]
        ResumeAnalyzer --> LLM_Call[LLM Call]
        AnswerGen --> LLM_Call
    end

    subgraph Data["Data Layer"]
        DB[(PostgreSQL / SQLite)]
    end

    subgraph External["External Services"]
        LLM[LLM API\n(OpenAI / Azure / DeepSeek)]
        Browserless[Browserless.io\n(optional, for scraping)]
    end

    FE --> GW
    R_resume --> Agent
    R_generate --> Agent
    R_auth --> DB
    R_users --> DB
    LLM_Call --> LLM
    Scraper --> Browserless
    Agent --> DB
```

**Components:**

| Layer | Component | Role |
|-------|-----------|------|
| **Client** | Frontend | React/Next.js app; calls API for auth, users, resume analysis, answer generation. |
| **API** | FastAPI | Single application; no separate API Gateway. Routes: auth, users, resume, generate, health, status. |
| **Core** | Agent logic | Lives inside the backend repo (`model/`). Resume analyzer, answer generator, scraper; orchestrated by `model/agents.py` and `model/api_integration.py`. |
| **Database** | PostgreSQL or SQLite | SQLAlchemy; `User`, `Job` (and future tables). Connection via `api/database`. |
| **External** | LLM API | OpenAI-compatible (OpenAI, Azure AI Foundry, DeepSeek). Config: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`. |
| **External** | Browserless | Optional; used by scraper for JS-heavy job pages when `BROWSERLESS_URL` is set. |

**Design choice:** The “agent” logic is **integrated** in the same process as the API (not a separate microservice). This keeps deployment simple and latency low; the Data Science modules plug in via `model/api_integration` and `model/agents`.

---

## 2. Data Flow (High Level)

1. **User registration / profile**
   - Frontend → `POST /auth/register` or `POST /api/users` → API → Database (create `User`).
   - Fetch profile: `GET /api/users/{userId}` → API → Database → return user (no password).

2. **Resume analysis**
   - Frontend → `POST /api/resume/analyze` (resume_text, job_url or job_description) → API → Core (scrape if needed, then resume analyzer) → LLM → parse/validate → response.

3. **Tailored answer**
   - Frontend → `POST /api/generate/answer` (question, user_profile, job_url or job_description) → API → Core (answer generator) → LLM → response.

4. **Health & status**
   - Load balancer / ops → `GET /health` or `GET /api/health` → API → `{"status": "online"}`.
   - Config check → `GET /api/status` → API → LLM/scraper config (no secrets).

---

## 3. Technology Stack

| Concern | Choice |
|---------|--------|
| Backend | Python 3.x, FastAPI |
| Database | PostgreSQL (production) or SQLite (local); SQLAlchemy 2.x |
| Auth | JWT (python-jose), bcrypt (passlib) |
| LLM | OpenAI-compatible client; env-based (OpenAI, Azure, DeepSeek) |
| Scraping | Beautiful Soup, requests; optional Playwright/Browserless |
| Logging | Python `logging`; optional JSON to file (see env `LOG_LEVEL`, `LOG_FILE`) |
| Rate limiting | slowapi |
| CORS | FastAPI CORSMiddleware; env `ALLOWED_ORIGINS`, Vercel regex |

---

## 4. Production Operations (Summary)

### 4.1 Local Development

- **Run:** From `ai_job_backend/`: `python main.py` or `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`.
- **Database:** Set `USE_SQLITE=true` or configure `PG_*` / `DATABASE_URL` in `.env`. Run migrations via `Base.metadata.create_all(bind=engine)` on startup (current behavior).
- **Check DB:** Run `python scripts/check_db.py` to verify connection.

### 4.2 Logging & Observability

- **Logging:** Request logging middleware logs method, path, status code, and duration. Application logs use `logging` (see `model/utils/logging_config.py`). Env: `LOG_LEVEL`, `LOG_FILE`.
- **Health:** `GET /health` and `GET /api/health` for liveness/readiness.
- **Status:** `GET /api/status` for service and config (OpenAI configured, Playwright/Selenium flags, model name).
- **Errors:** Exceptions return JSON error payloads; errors are logged with stack traces in development.

### 4.3 Future Deployment (Documented)

- **Packaging:** Docker image (Dockerfile) and optional docker-compose for API + DB.
- **Platform:** Render, Heroku, AWS (ECS/App Runner), or similar; use `DATABASE_URL` or `PG_*` for DB.
- **CI/CD:** GitHub Actions for tests and optional deploy.
- **Monitoring:** Optional Sentry for errors; optional metrics endpoint (e.g. `/api/metrics`) and APM.

---

## 5. API Endpoints (Assignment Alignment)

| Assignment endpoint | Implementation | Notes |
|---------------------|----------------|-------|
| `POST /api/users` | Create user profile | Same semantics as `POST /auth/register`; returns user id. |
| `GET /api/users/{userId}` | Fetch user profile | Returns id, email, full_name (no password). Auth: JWT. |
| `POST /api/resume/analyze` | Resume scorer | Request: resume_text, job_url or job_description. Returns score, suggestions, keywords. |
| `POST /api/generate/answer` | Tailored answer agent | Request: question, user_profile, job_url or job_description. Returns answer. |
| Health check | `GET /health`, `GET /api/health` | Returns `{"status": "online", "service": "ai-job-assistant"}`. |

Database schemas (SQLAlchemy) are defined in `api/models`; Pydantic request/response models in `api/schemas` and route modules. Data contracts for resume scoring and tailored answers are in `model/contracts.py` and documented in `DATA_SCIENCE_DESIGN.md`.
