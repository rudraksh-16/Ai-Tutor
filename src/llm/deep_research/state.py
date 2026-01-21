from typing import List, Dict, Optional
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    topic_title:str
    user_summary: str
    all_chapters: List[str]
    current_chapter_title: str
    sources: List[str]
    subtopics: List[str]
    iteration:int
    max_iterations: int
    query: str
    subtopics: List[str]
    success_criteria: Dict
    sources: List[Dict]
    queries_used: List[str]
    subtopic_coverage: Dict[str, float]
    scratchpad: str
    draft: Optional[str]
    iteration: int
    max_iterations: int
    output: str
