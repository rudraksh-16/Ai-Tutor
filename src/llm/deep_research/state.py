from typing import List, Dict
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    topic_title:str
    user_summary: str
    all_chapters: List[str]
    current_chapter_title: str
    subtopics: List[str]
    iteration:int
    max_iterations: int
    query: str
    success_criteria: Dict
    sources: List[Dict]
    scratchpad: str
    output: str
