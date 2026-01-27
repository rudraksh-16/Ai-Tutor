from typing import List, Dict, Optional, Any
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    query: str
    subtopics: List[str]
    success_criteria: Dict
    sources: List[Dict]
    scratchpad: str
    covered_subtopics: Dict[str, int]
    current_subtopic: str
    approved: bool
    reviewer_attempts: int
    extra: Optional[Any]
    scores: Dict
    final_score: float
    index: int
    draft: str
    critique: Optional[str]
    missing: str
    improvement_instructions: str
