from typing import List, Dict, Optional
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    # User input
    query: str

    # Planning
    subtopics: List[str]
    success_criteria: Dict

    # Research tracking
    sources: List[Dict]
    queries_used: List[str]
    subtopic_coverage: Dict[str, float]
    scratchpad: str

    # Synthesis
    draft: Optional[str]

    # Evaluation
    evaluation: Optional[Dict]
    approved: bool

    # Control
    iteration: int
    max_iterations: int
    critique: Optional[str]
    missing: List[str]
    improvement_instructions: List[str]
