import json
import logging
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage

from src.llm.deep_research.state import ResearchState
from src.llm.deep_research.prompt import PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.6)


def query_maker_agent(state: ResearchState) -> ResearchState:
    logger.info("Planner started")

    query = state.get("query")
    if not query:
        logger.error("Planner received empty query in state")
        raise ValueError("Missing 'query' in ResearchState")

    logger.debug("Planning research for query: %s", query)

    response = llm.invoke([
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"Research question: {query}")
    ])

    raw_output = response.content.strip()
    logger.debug("Planner raw LLM output: %s", raw_output)

    if not raw_output:
        logger.error("Planner returned empty output")
        raise ValueError("Planner returned empty output")

    try:
        plan = json.loads(raw_output)
    except json.JSONDecodeError:
        logger.exception("Planner returned invalid JSON")
        raise

    subtopics = plan.get("subtopics", [])
    success_criteria = plan.get("success_criteria")

    logger.info(
        "Planner generated %d subtopics",
        len(subtopics)
    )
    logger.debug("Subtopics: %s", subtopics)
    logger.debug("Success criteria: %s", success_criteria)

    return {
        **state,
        "subtopics": subtopics,
        "success_criteria": success_criteria,
    }
