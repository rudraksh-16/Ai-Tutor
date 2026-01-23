from deep_research.state import ResearchState
from deep_research.prompt import PLANNER_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage
import json

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.6)

from deep_research.state import ResearchState


def planner_agent(state: ResearchState) -> ResearchState:
    query = state["query"]

    response = llm.invoke(
        [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Research question: {query}"),
        ]
    )

    plan = json.loads(response.content)

    subtopics = plan["subtopics"]

    return {
        **state,
        "subtopics": subtopics,
        "subtopic_coverage": {t: 0.0 for t in subtopics},
        "success_criteria": plan["success_criteria"],
    }
