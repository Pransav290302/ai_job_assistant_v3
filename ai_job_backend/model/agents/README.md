# Optional: SmolAgents-based Job Assistant

This folder implements a **SmolAgents**-based agent that uses the same LLM config as the rest of the app (OpenAI or Azure AI Foundry / DeepSeek R1). The agent has three tools:

- **scrape_job(job_url)** — Fetch job description text from a URL.
- **analyze_resume(resume_text, job_description)** — Resume vs JD match score and suggestions.
- **generate_answer(question, work_history, skills, education, job_description)** — Tailored application answer.

## Install

```bash
pip install "smolagents[openai]"
```

## Use from Python

```python
from model.agents import run_job_assistant_agent, is_smolagents_available

if is_smolagents_available():
    result = run_job_assistant_agent(
        "Scrape https://linkedin.com/jobs/... and analyze my resume against it. "
        "My resume: [paste text]"
    )
    print(result)  # {"success": True, "output": "..."} or {"success": False, "error": "..."}
else:
    print("Install: pip install \"smolagents[openai]\"")
```

## Environment

Uses the same env as the rest of the backend:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (optional; for Azure/DeepSeek)
- `OPENAI_MODEL` (e.g. `DeepSeek-R1` for Azure)
- `BROWSERLESS_URL` (required for LinkedIn/Glassdoor in `scrape_job`)

See [AZURE_DEEPSEEK_SETUP.md](../../../AZURE_DEEPSEEK_SETUP.md) and [AGENT_FRAMEWORKS.md](../../../AGENT_FRAMEWORKS.md).
