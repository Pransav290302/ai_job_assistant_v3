from typing import Any, Dict, List, Optional, TypedDict, Union


class WorkHistoryEntry(TypedDict, total=False):
    company: str
    position: str
    duration: str
    responsibilities: List[str]
    achievements: List[str]


class EducationEntry(TypedDict, total=False):
    institution: str
    degree: str
    field: str
    graduation_year: int


class UserProfile(TypedDict, total=False):
    work_history: Union[List[WorkHistoryEntry], str]
    skills: Union[List[str], str]
    education: Union[List[EducationEntry], str]
    certifications: List[str]
    summary: str
    additional_info: str




class SuggestionItem(TypedDict):
    category: str   
    suggestion: str
    priority: str   


class ResumeScoreOutput(TypedDict, total=False):
    score: int                    
    match_percentage: float       
    suggestions: List[Union[SuggestionItem, str]]  
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]         
    missing_skills: List[str]    



def scraper_output_schema() -> Dict[str, Any]:
    return {
        "title": "str (optional)",
        "company": "str (optional)",
        "description": "str (main content)",
        "requirements": "str (optional)",
        "url": "str",
    }
