import logging

from src.llm.deep_research.state import ResearchState

logger = logging.getLogger(__name__)


def set_next_query_node(state: ResearchState) -> ResearchState:
    subtopics = state.get("subtopics", [])
    idx = state.get("index", 0)

    if idx < len(subtopics):
        state["current_subtopic"] = subtopics[idx]
        state["index"] = idx + 1
        state["reviewer_attempts"] = 0
        logger.info(
            "Set next subtopic | index=%s | subtopic=%s",
            idx,
            state["current_subtopic"],
        )
    else:
        state["current_subtopic"] = None
        logger.info("No more subtopics to set")

    return state


def route_after_set_next_query(state: ResearchState) -> str:
    if state.get("current_subtopic") is None:
        return "synthesizer"
    return "researcher"
