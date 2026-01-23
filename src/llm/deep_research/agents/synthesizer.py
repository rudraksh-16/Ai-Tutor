from deep_research.state import ResearchState
from deep_research.prompt import SYNTHESIS_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


def synthesizer_agent(state: ResearchState) -> ResearchState:
    sources = state["sources"]
    subtopics = state["subtopics"]
    scratchpad = state.get("scratchpad", "")

    user_prompt = f"""
Research question:
{state['query']}

Planned subtopics:
{subtopics}

Evaluator critique:
{state.get("critique", "")}

Missing elements identified by evaluator:
{state.get("missing", [])}

Researcher scratchpad (notes and reasoning — NOT for direct copying):
{scratchpad}

Collected verified evidence:
{json.dumps(sources, indent=2)}

Instructions:
- Use the scratchpad to understand context and intent
- Use the evidence as the ONLY factual source
- Produce a final, polished research report
- Explicitly address missing elements
"""

    response = llm.invoke(
        [
            SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ],
        config={"run_name": "Synthesizer → Final Report"},
    )

    return {
        **state,
        "draft": response.content,
        "final": response.content,  # optional alias if you want a clear terminal field
    }
