"""
Mock AI Responses for Demo/Presentation
Provides sample responses when OpenAI API is not available
"""

from typing import Dict, List


def get_mock_resume_analysis(resume_text: str, job_description: str) -> Dict:
    """
    Generate a mock resume analysis for demonstration purposes.
    
    Args:
        resume_text: User's resume text
        job_description: Job description text
        
    Returns:
        Dictionary with mock analysis results
    """
    # Simple keyword matching for demo
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()
    
    # Extract some keywords from job description
    common_skills = ['python', 'javascript', 'java', 'sql', 'aws', 'docker', 
                     'kubernetes', 'react', 'node', 'django', 'flask', 'postgresql',
                     'mongodb', 'git', 'agile', 'scrum', 'api', 'rest', 'microservices']
    
    found_skills = [skill for skill in common_skills if skill in resume_lower]
    missing_skills = [skill for skill in common_skills if skill in jd_lower and skill not in resume_lower][:5]
    
    # Calculate a mock score
    match_score = min(85, 60 + len(found_skills) * 3)
    
    return {
        "score": match_score,
        "suggestions": [
            f"Highlight your experience with {missing_skills[0] if missing_skills else 'relevant technologies'}",
            "Quantify your achievements with specific metrics",
            "Tailor your resume to match the job description keywords",
            "Include relevant projects that demonstrate required skills"
        ] if missing_skills else [
            "Your resume shows good alignment with the job requirements",
            "Consider adding more quantifiable achievements",
            "Highlight leadership and collaboration experiences"
        ],
        "strengths": [
            f"Strong background in {found_skills[0] if found_skills else 'relevant technologies'}",
            "Relevant work experience",
            "Good technical foundation"
        ],
        "missing_skills": missing_skills[:5],
        "match_percentage": float(match_score)
    }


def get_mock_tailored_answer(question: str, user_profile: Dict, job_description: str) -> str:
    """
    Generate a mock tailored answer for demonstration purposes.
    
    Args:
        question: Application question
        user_profile: User profile dictionary
        job_description: Job description text
        
    Returns:
        Mock generated answer text
    """
    work_history = user_profile.get('work_history', '')
    skills = user_profile.get('skills', [])
    education = user_profile.get('education', '')
    
    skills_str = ', '.join(skills) if isinstance(skills, list) else str(skills)
    
    answer = f"""Based on my background and experience, I believe I am an excellent fit for this position.

{work_history if work_history else 'With my professional experience,'} I have developed strong expertise in {skills_str if skills_str else 'relevant technologies'}. My {education if education else 'educational background'} has provided me with a solid foundation that aligns well with the requirements of this role.

What particularly excites me about this opportunity is how it combines [relevant aspect from job description]. I am confident that my skills in {skills_str if skills_str else 'the required technologies'} and my passion for [relevant field] make me a strong candidate who can contribute meaningfully to your team.

I am eager to bring my experience and enthusiasm to this role and help drive success for your organization."""

    return answer
