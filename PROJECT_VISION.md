# AI-Powered Job Application Assistant — Project Vision & Gap Analysis

This document maps the **assignment vision** to the current codebase, lists what exists, and what remains to reach the full end product.

---

## Vision (Assignment)

> Build a tool that fundamentally streamlines the job application process, giving users back their time and providing them with an **AI-powered co-pilot** to land their dream job.  
> **Preferred:** browser extension or **web application** (this repo is a web app).

---

## Core Features vs Current State

### 1. Autofill Agent

| Requirement | Current state | Gap |
|-------------|----------------|-----|
| Securely store profile (name, contact, work history, education, etc.) | **Done:** Supabase auth + `user_preferences`; profile pages (Personal, Preferences, Documents); onboarding steps (roles, skills, location, salary, etc.) | Profile is stored; not yet used for autofill. |
| Intelligently fill application forms across different websites | **Not implemented** | Need either: (a) **Browser extension** that injects into job sites and fills from profile API, or (b) **Web-only**: “Copy to clipboard” / pre-filled snippets per field that user pastes. No cross-site DOM autofill without an extension. |

**Next steps:**  
- Backend: API to return user profile in a structured, autofill-friendly format (e.g. `GET /api/profile/autofill`).  
- Frontend: Profile page section “For autofill” with copy buttons per field or JSON export.  
- Optional: Chrome/Edge extension (separate repo or `/extension`) that reads profile from your API and fills forms on supported sites.

---

### 2. Resume-to-JD Scoring Agent

| Requirement | Current state | Gap |
|-------------|----------------|-----|
| Analyze resume vs job description | **Done:** `model/resume_analyzer.py` + `api/routes/model.py` → `POST /api/resume/analyze` (resume_text + job_url or job_description) | — |
| Match score + actionable insights | **Done:** Returns `score`, `suggestions`, `strengths`, `missing_skills`, `match_percentage` (structured) | — |
| UI to use it | **Done:** Assistant page (`/assistant`) → “Analyze Resume” tab: paste/upload resume, job URL, then “Analyze resume vs job” | Optional: move or duplicate into Dashboard “Resume” or “Matches” for logged-in flow. |

**Next steps:**  
- Optional: Show match score on job cards in Matches/Jobs and link to full analysis.  
- Optional: Persist “last analysis” per job in DB for quick recall.

---

### 3. Tailored Answer Agent

| Requirement | Current state | Gap |
|-------------|----------------|-----|
| Use JD + user profile to generate answers to application questions | **Done:** `model/answer_generator.py` + `POST /api/generate/answer` (question, user_profile, job_url or job_description) | — |
| Questions like “Why are you a good fit?” / “What is your biggest strength?” | **Done:** Prompt and API support any question text | — |
| UI | **Done:** Assistant page → “Generate Answer” tab; profile can come from resume extract or manual fields | Optional: Prefill profile from Supabase profile for logged-in users. |

**Next steps:**  
- Optional: Pull profile from Supabase (personal + preferences) when user is logged in so they don’t re-enter.  
- Optional: List of “common questions” as quick buttons.

---

### 4. Dashboard — “Where has my application been?”

| Requirement | Current state | Gap |
|-------------|----------------|-----|
| Single screen to walk user through application pipeline | **Done:** Job Tracker page (`/job_tracker`) with columns by status | Status set was minimal. |
| Status values: Not Submitted yet, Submitted, Initial Response, Interview Requested, Rejected after Interview, Onsite/Video Interview Requested, etc. | **Updated:** `types/jobTracker.ts` and JobTracker UI now use an expanded status set (see below) | Backend/Supabase `jobs.status` is free-form; frontend can map to this set. |

**Status pipeline (implemented in Job Tracker):**  
`not_submitted` → `submitted` → `initial_response` → `interview_requested` → `onsite_video_requested` → `offer`  
and terminal: `rejected`, `rejected_after_interview`.

**Next steps:**  
- Persist jobs in Supabase `jobs` table with `status` in this set; Job Tracker fetches and groups by status.  
- Allow drag-and-drop or dropdown to move a job from one column to another (update `status` via API or Supabase client).

---

## Role-Oriented Checklist

### Frontend (User’s Champion)

- [x] Intuitive dashboard layout (Dashboard, Matches, Jobs, Job Tracker, Documents, Profile).  
- [x] Assistant page: Scrape Job, Analyze Resume, Generate Answer with clear tabs and feedback.  
- [x] Job Tracker columns aligned with assignment status pipeline.  
- [ ] **Agentic UX:** “Show the work” (e.g. “Analyzing resume…”, “Scraping job page…”) — partially done with loading states; can add step-by-step progress.  
- [ ] **Intervention:** Let user edit or reject AI suggestions (e.g. edit generated answer before copy; optional thumbs up/down).  
- [ ] **Feedback:** Simple feedback (e.g. “Was this helpful?”) on analysis and answers.  
- [ ] Optional: Add “Assistant” to logged-in nav so users can open Scrape / Analyze / Answer from dashboard.

### Backend (Engine & Infrastructure)

- [x] APIs: `/jobs/analyze`, `/api/resume/analyze`, `/api/generate/answer`, `/api/job/scrape`, `/api/resume/extract`, `/api/status`.  
- [x] Scraper tool (Playwright/Selenium) for job URL → JD text.  
- [x] DB: Postgres (FastAPI) for jobs; Supabase for auth + user_preferences (+ jobs if unified).  
- [ ] **Profile for agents:** Endpoint or internal function to get “user profile” (from Supabase or Postgres) for Tailored Answer and future Autofill.  
- [ ] Optional: Rate limiting, logging, and monitoring (partially present via limiter).

### Data Science (Intelligence)

- [x] Resume vs JD: structured prompt + JSON output (score, suggestions, strengths, missing_skills).  
- [x] Tailored answers: prompt that uses JD + user profile.  
- [x] Resume extraction: text → work_history, skills, education (for profile).  
- [x] Job scraping: URL → JD text (tool for the agent).  
- [ ] Optional: **Azure AI Foundry / DeepSeek** — swap `OPENAI_BASE_URL` + `OPENAI_API_KEY` (or add `AZURE_*` / `DEEPSEEK_*`) so the same APIs work with DeepSeek R1; no change to contract (still JSON/text).

---

## Key Concepts (Assignment) — Where They Live

| Concept | Where in codebase |
|--------|--------------------|
| **AI Agent** | Each “agent” = backend service (e.g. `resume_analyzer`, `answer_generator`) + API route; perceives input (resume, JD, question), reasons via LLM, returns structured output. |
| **LLM** | OpenAI-compatible client in backend (`OPENAI_API_KEY`, `OPENAI_BASE_URL`); can point to Azure/DeepSeek. |
| **Prompt engineering** | `model/resume_analyzer.py`, `model/answer_generator.py`, `model/resume_extractor.py`, and `api/routes/jobs.py` (analyze prompt). |
| **Tool use** | Scraper (`job_scraper` / Playwright in `jobs.py` and `api_integration`) = tool; DB/profile = future tool for autofill and answers. |
| **Structured output (JSON)** | Resume analysis returns JSON; answer returns text (could add JSON wrapper if needed). |
| **API** | FastAPI routes under `/jobs` and `/api`; frontend uses `/api/backend` proxy to avoid CORS. |

---

## Helpful Resources (Assignment)

- **Azure:** $200 credit for new customers; [Azure account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account); [billing for free trial](https://learn.microsoft.com/en-us/answers/questions/2283380/billing-for-free-trial-account).  
- **DeepSeek R1 on Azure AI Foundry:** [Announcement](https://azure.microsoft.com/en-us/blog/deepseek-r1-is-now-available-on-azure-ai-foundry-and-github/); [YouTube: Deploy DeepSeek R1, build web chatbot](https://www.youtube.com/watch?v=pj2knBX4S1w).  
- **Agents:** Google ADK, SmolAgents, “Build an AI Agent From Scratch” — useful for future multi-step or tool-calling agents; current agents are single-call (scrape → LLM → response).

---

## Suggested Roadmap (Priority)

1. **Job Tracker + Supabase:** Store and update `jobs.status` in Supabase; Job Tracker page fetches and displays jobs by status; allow status updates (dropdown or drag).  
2. **Profile API for agents:** Backend (or Next API route) returns current user’s profile (from Supabase) for Tailored Answer and future Autofill.  
3. **Autofill:** Either “copy fields” UI from profile, or a small browser extension that calls your API and fills forms on selected job sites.  
4. **Agentic UX:** Progress indicators, editable AI answers, and a simple “Was this helpful?” feedback.  
5. **Optional:** Add Assistant link to dashboard nav; optionally switch LLM to Azure/DeepSeek via env.

---

## Summary

| Feature | Status | Notes |
|--------|--------|-------|
| Autofill Agent | Profile stored; autofill not built | Need extension or “copy profile” UI + optional API. |
| Resume–JD Scoring | Done (API + Assistant UI) | Optional: surface in Matches; persist per job. |
| Tailored Answer | Done (API + Assistant UI) | Optional: prefill profile from Supabase. |
| Dashboard (application pipeline) | Done (expanded statuses in Job Tracker) | Next: persist jobs in DB and update status from UI. |

The codebase already implements most of the “what”; the main gaps are **Autofill** (extension or copy-from-profile), **Job Tracker persistence and status updates**, and **agentic UX** (show work, allow intervention, collect feedback).
