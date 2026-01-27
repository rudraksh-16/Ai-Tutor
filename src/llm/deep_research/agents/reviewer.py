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
                previously_sufficient=state.get("previously_sufficient", []),
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
        state["approved"] = False
        return state

    final_score = (
        data["scores"]["coverage"]
        + data["scores"]["depth"]
        + data["scores"]["source_quality"]
        + data["scores"]["clarity"]
    ) / 4
    if final_score > 0.70:
        state["approved"] = True

    logger.info("Reviewer approved: %s", state["approved"])
    logger.info("Reviewer scores: %s", data["scores"])
    logger.info("Reviewer missing feedback: %s", data.get("missing"))
    logger.info("Reviewer final score: %s", final_score)

    state["scores"] = data["scores"]
    state["final_score"] = final_score
    state["critique"] = data["critique"]

    state["missing"] = data.get("missing")

    state["improvement_instructions"] = data.get("improvement_instructions")

    state["reviewer_attempts"] = state.get("reviewer_attempts", 0) + 1
    if state["reviewer_attempts"] >= DeepResearchConstants.MAX_RETRIES:
        logger.warning("Reviewer max attempts reached; forcing approval")
        state["approved"] = True
        state["missing"] = None
        state["improvement_instructions"] = None

    if state["approved"]:
        state["missing"] = None
        state["improvement_instructions"] = None

    return state


def route_after_reviewer(state: ResearchState) -> str:
    if not state.get("approved"):
        return "researcher"
    return "set_next_query"
