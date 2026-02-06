# Agent Frameworks for the Job Application Assistant

This project’s AI “agents” (Resume–JD scoring, Tailored Answer, Job scraping) are implemented as **tools + LLM calls**. You can rebuild or extend them using **agent frameworks** such as **Google Agent Development Kit (ADK)** or **SmolAgents**.

---

## How This Project Uses “Agents”

| Concept | In this repo |
|--------|---------------|
| **Agent** | A goal (e.g. “analyze resume vs JD”) + tools (scraper, profile) + LLM (OpenAI/Azure/DeepSeek). |
| **Tools** | `scrape_job_description`, `analyze_resume_and_jd`, `generate_tailored_answer`, `extract_profile_from_resume` (in `model/`). |
| **LLM** | OpenAI-compatible client; config via `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` (see [AZURE_DEEPSEEK_SETUP.md](AZURE_DEEPSEEK_SETUP.md)). |
| **Structured output** | Resume analysis returns JSON (score, suggestions, strengths, missing_skills). |

You can reimplement or extend these flows using the frameworks below.

---

## 1. Google Agent Development Kit (ADK)

**What it is:** Google’s Agent Development Kit for building agents with tools, state, and structured output. Uses **Gemini** by default.

**Resources:**
- **YouTube:** [Google Launches an Agent SDK - Agent Development Kit](https://www.youtube.com/results?search_query=Google+Agent+Development+Kit)
- **YouTube:** [Google Agent Development Kit](https://www.youtube.com/results?search_query=Google+ADK+agents)
- **Code / tutorial:** [Google ADK Agents (mer.vin)](https://mer.vin/2025/05/google-adk-agents/)
- **YouTube:** [Agent Development Kit (ADK) Masterclass: Build AI Agents & Automate Workflows](https://www.youtube.com/results?search_query=ADK+Masterclass+Build+AI+Agents)
- **Docs:** [Google ADK – Get started](https://google.github.io/adk-docs/get-started/)
- **Install:** `pip install google-adk`

**Concepts (from mer.vin):**
- **Agent:** `Agent(name=..., model="gemini-2.0-flash", instruction=..., tools=[...])`
- **Tools:** Python functions (e.g. `get_stock_price(ticker)`); can use `ToolContext` for state.
- **Structured output:** `LlmAgent(..., output_schema=PydanticModel, output_key="...")`
- **Callbacks:** `before_tool_callback`, `after_tool_callback` for logging/monitoring.

**Using ADK with this project:**
- Set `GOOGLE_API_KEY` (and optionally `GOOGLE_GENAI_USE_VERTEXAI=FALSE`) in `.env`.
- Define tools that call our existing logic (e.g. a tool that calls `scrape_job_description(job_url)` or `analyze_resume_and_jd(...)`).
- Build an ADK agent whose goal is “analyze this resume against this job” and give it those tools; the agent can decide when to scrape, when to analyze, etc.

**Example (conceptual):**
```python
# Example: ADK agent with a job-scraping tool (uses Gemini)
from google.adk.agents import Agent
# Assume get_job_description(job_url) calls our existing scraper
tool_agent = Agent(
    name="job_assistant",
    model="gemini-2.0-flash",
    description="Scrapes job pages and analyzes resume vs job.",
    instruction="You are a job application assistant. Use get_job_description to fetch job text, then analyze.",
    tools=[get_job_description],
)
```

---

## 2. SmolAgents (Hugging Face)

**What it is:** A small library for building agents that use tools and optional code execution. Works with **OpenAI-compatible** APIs (including Azure/DeepSeek), so it fits this backend without changing providers.

**Resources:**
- **Docs:** [SmolAgents](https://smolagents.org/docs/smolagent-docs/) / [Hugging Face – SmolAgents](https://huggingface.co/docs/smolagents)
- **GitHub:** [huggingface/smolagents](https://github.com/huggingface/smolagents)
- **YouTube:** [SmolAgents: A Smol Library to Build Agents](https://www.youtube.com/results?search_query=SmolAgents)
- **YouTube:** [Build Multi-Agent Systems with SmolAgents](https://www.youtube.com/results?search_query=Build+Multi-Agent+SmolAgents)
- **Install:** `pip install "smolagents[openai]"` (for OpenAI/Azure-compatible APIs)

**Concepts:**
- **Tools:** Use `@tool` decorator or subclass `Tool` (name, description, inputs, output_type, forward).
- **Models:** `OpenAIModel(model_id=..., api_base=..., api_key=...)` — use `OPENAI_BASE_URL` and `OPENAI_API_KEY` for Azure/DeepSeek.
- **Agents:** `ToolCallingAgent(tools=[...], model=model)` or `CodeAgent(tools=[...], model=model)`.

**Using SmolAgents with this project:**
- Reuse existing env: `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` (e.g. Azure DeepSeek R1).
- Wrap our functions as SmolAgents tools (scrape job, analyze resume, generate answer).
- Build a `ToolCallingAgent` or `CodeAgent` that can “scrape job”, “analyze resume vs job”, “generate tailored answer” in one run.

**Optional implementation in this repo:**
- **`model/agents/`** — SmolAgents-based Job Assistant agent with tools: `scrape_job`, `analyze_resume`, `generate_answer`. Uses the same `OPENAI_*` env (Azure/DeepSeek work as-is).
- **Install:** `pip install "smolagents[openai]"` (or `pip install -r requirements-agents.txt` from `ai_job_backend/`).
- **API:** `POST /api/agent/run` with body `{"task": "Scrape <job_url> and analyze my resume: ..."}`. If SmolAgents is not installed, the route returns a message to install it.
- **Python:** `from model.agents import run_job_assistant_agent, is_smolagents_available` — see `model/agents/README.md`.

---

## 3. Building an Agent From Scratch (Python)

**Resources:**
- **YouTube:** [Build an AI Agent From Scratch in Python - Tutorial for Beginners](https://www.youtube.com/results?search_query=Build+AI+Agent+From+Scratch+Python)

**Idea:** You can implement the “agent” pattern yourself: loop (reason with LLM → choose tool → run tool → feed result back) and use our existing `model/` functions as tools. The current backend already does “single-step” agent behavior (e.g. one prompt for resume analysis); a from-scratch agent would add multi-step tool use and optional state.

---

## Summary

| Framework | Model / API | Best for |
|-----------|-------------|----------|
| **Google ADK** | Gemini (`GOOGLE_API_KEY`) | Multi-tool agents, state, structured output; separate from current OpenAI/Azure stack. |
| **SmolAgents** | OpenAI-compatible (incl. Azure/DeepSeek) | Same backend config; add tool-calling or code agents without changing provider. |
| **From scratch** | Any (e.g. existing `openai` client) | Full control; use `model/` as tools in your own loop. |

To **use these to “make” the model/agents:**  
- **ADK:** Add an ADK-based agent (e.g. in `model/agents/adk_job_agent.py`) that uses Gemini and tools that call our scrape/analyze/answer logic.  
- **SmolAgents:** Use the optional `model/agents/` SmolAgents agent (see below) or define your own tools and `ToolCallingAgent`/`CodeAgent` with `OpenAIModel(api_base=OPENAI_BASE_URL, ...)`.

---

## Optional: SmolAgents Job Assistant in This Repo

An optional **SmolAgents-based job assistant** is provided under `model/agents/`. It uses the same `OPENAI_*` env vars (so Azure/DeepSeek work as-is) and exposes tools that wrap the existing scraper, resume analyzer, and answer generator.

**Install (optional):**
```bash
pip install "smolagents[openai]"
```

**Use:** See `model/agents/README.md` (if present) or the docstrings in `model/agents/job_assistant_agent.py`. The main API continues to work without SmolAgents; this is an alternative “agent” entrypoint you can call from a route or script.
