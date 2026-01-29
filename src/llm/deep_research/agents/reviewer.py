import logging
import json

from src.llm.agent_core.agent import Agent
from src.llm.deep_research.state import ResearchState
from src.llm.deep_research.constant import DeepResearchConstants
from src.llm.deep_research.prompt import REVIEWER_SYSTEM_PROMPT, REVIEWER_USER_PROMPT

logger = logging.getLogger(__name__)


class Reviewer(Agent):
    def __init__(
        self,
        state: ResearchState,
        model=DeepResearchConstants.DEFAULT_MODEL,
        temperature=DeepResearchConstants.DEFAULT_TEMPERATURE,
        max_iteration=DeepResearchConstants.DEFAULT_MAX_RETRIES,
    ):
        self.state = state
        logger.info("Initializing Reviewer Agent")

        super().__init__(
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            user_prompt=REVIEWER_USER_PROMPT.format(
                current_subtopic=state["current_subtopic"],
                current_coverage=state.get("covered_subtopics", {}),
                scratchpad=state.get("scratchpad", ""),
                sources=state.get("sources",[]),
            ),
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )

        logger.info("Reviewer Agent initialized successfully")


def reviewer_node(state: ResearchState) -> ResearchState:
    reviewer_agent = Reviewer(
        state=state,
        model=DeepResearchConstants.MODEL,
        temperature=DeepResearchConstants.TEMPERATURE,
        max_iteration=DeepResearchConstants.MAX_RETRIES,
    )

    ai_response, _ = reviewer_agent.invoke([])

    try:
        data = json.loads(ai_response)
    except json.JSONDecodeError:
        logger.exception("Reviewer returned invalid JSON")
        return state

    final_score = sum(data["scores"].values()) / 4

    state["approved"] = final_score >= 0.65

    state["scores"] = data["scores"]
    state["final_score"] = final_score
    state["critique"] = data["critique"]
    state["missing"] = data["missing"]
    state["improvement_instructions"] = data["improvement_instructions"]

    logger.info(f"final_score: {final_score}")
    logger.info(f"Approved: {state["approved"]}")
    
    state["reviewer_attempts"] = state.get("reviewer_attempts", 0) + 1
    if state["reviewer_attempts"] >= DeepResearchConstants.MAX_RETRIES:
        state["forced_progress"] = True

    if state["approved"]:
        state["missing"] = None
        state["improvement_instructions"] = None

    return state

def route_after_reviewer(state: ResearchState) -> str:
    if state.get("approved") or state.get("forced_progress"):
        return "set_next_query"
    return "researcher"
