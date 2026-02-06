"""
Agent implementations: orchestration (scrape + LLM workflows) and optional SmolAgents.
- analyze_resume_and_jd, generate_tailored_answer: Full workflows (scrape -> prompt -> LLM -> parse)
- run_job_assistant_agent: Optional SmolAgents multi-tool agent (pip install "smolagents[openai]")
"""

from model.orchestration import analyze_resume_and_jd, generate_tailored_answer
from model.agents.job_assistant_agent import (
    run_job_assistant_agent,
    is_smolagents_available,
)

__all__ = [
    "analyze_resume_and_jd",
    "generate_tailored_answer",
    "run_job_assistant_agent",
    "is_smolagents_available",
]
