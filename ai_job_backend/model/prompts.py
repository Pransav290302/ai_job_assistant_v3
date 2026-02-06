"""
Prompt templates for the AI Job Assistant (Senior Data Scientist todo).
Centralized prompts for resume scoring and tailored answers.
"""

RESUME_SCORER_PROMPT = """
You are an expert ATS (Applicant Tracking System) and resume analyzer.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

TASK: Analyze how well this resume matches the job description.

Provide your analysis in the EXACT JSON format below. Use only valid JSON. No markdown, no code block wrapper.

FEW-SHOT EXAMPLE 1 (strong match):
{{
  "score": 85,
  "match_percentage": 0.85,
  "suggestions": [
    {{"category": "skills", "suggestion": "Add 'React.js' to your skills section", "priority": "high"}},
    {{"category": "experience", "suggestion": "Quantify impact: 'Led team of 5' instead of 'Led team'", "priority": "medium"}},
    {{"category": "keywords", "suggestion": "Include 'machine learning' from the job description", "priority": "high"}}
  ],
  "matched_keywords": ["Python", "Machine Learning", "SQL"],
  "missing_keywords": ["Docker", "Kubernetes"]
}}

FEW-SHOT EXAMPLE 2 (weaker match):
{{
  "score": 52,
  "match_percentage": 0.52,
  "suggestions": [
    {{"category": "experience", "suggestion": "Highlight years of experience explicitly", "priority": "high"}},
    {{"category": "keywords", "suggestion": "Add 'Agile' and 'Scrum' if applicable", "priority": "medium"}}
  ],
  "matched_keywords": ["Java", "REST API"],
  "missing_keywords": ["Kubernetes", "AWS", "Microservices"]
}}

RULES:
- score: integer 0-100 (objective match based on keywords, experience, skills)
- match_percentage: float 0.0-1.0 (score/100)
- suggestions: 2-5 actionable items; category in ["skills","experience","keywords"]; priority in ["high","medium","low"]
- matched_keywords: JD terms found in resume
- missing_keywords: important JD terms NOT in resume

Output ONLY the JSON object.
"""

TAILORED_ANSWER_PROMPT = """
You are an expert career coach helping a candidate write compelling application answers.

CANDIDATE PROFILE:
{user_profile}

JOB DESCRIPTION:
{job_description}

APPLICATION QUESTION:
{question}

TASK: Write a compelling, personalized answer that:
- Demonstrates specific relevant experience from the profile
- Uses concrete examples and metrics where possible
- Matches the company's tone and values suggested by the JD
- Is 150-250 words

Guidelines:
1. Be authentic and specific - reference actual experiences from the profile.
2. Connect their background directly to the job requirements.
3. Show enthusiasm and genuine interest.
4. Keep the tone professional but personable.

Write the answer (plain text, no JSON):
"""


def format_resume_scorer_prompt(resume_text: str, job_description: str) -> str:
    """Format RESUME_SCORER_PROMPT with truncated inputs to avoid token limits."""
    max_resume = 4000
    max_jd = 4000
    return RESUME_SCORER_PROMPT.format(
        resume_text=resume_text[:max_resume],
        job_description=job_description[:max_jd],
    )


def format_tailored_answer_prompt(
    user_profile: str, job_description: str, question: str
) -> str:
    """Format TAILORED_ANSWER_PROMPT. user_profile should be a string representation of the profile."""
    max_jd = 4000
    return TAILORED_ANSWER_PROMPT.format(
        user_profile=user_profile,
        job_description=job_description[:max_jd],
        question=question,
    )


# Profile Extraction (for resume → structured profile)

PROFILE_EXTRACT_PROMPT = """
Extract structured information from this resume. Return valid JSON only. No markdown, no code block.

RESUME:
{resume_text}

OUTPUT FORMAT - exact keys required:

EXAMPLE (for a software engineer resume):
{{
  "work_history": "Senior Engineer at Acme Corp (2020-2024): Built APIs, led team. Junior Dev at Startup (2018-2020): Full-stack development.",
  "skills": "Python, JavaScript, React, SQL, AWS, Docker",
  "education": "BS Computer Science, State University, 2018, GPA 3.7",
  "additional_info": "AWS Certified, Open source contributor"
}}

EXAMPLE (for a data analyst resume):
{{
  "work_history": "Data Analyst at Finance Co (2019-present): Dashboard design, SQL queries.",
  "skills": "SQL, Tableau, Excel, Python, statistics",
  "education": "MS Data Science, 2019",
  "additional_info": ""
}}

Return a JSON object with exactly: work_history, skills, education, additional_info. All string values.
"""


def format_profile_extract_prompt(resume_text: str) -> str:
    """Format PROFILE_EXTRACT_PROMPT with truncated resume to avoid token limits."""
    max_resume = 6000
    return PROFILE_EXTRACT_PROMPT.format(resume_text=resume_text[:max_resume])
