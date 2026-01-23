from deep_research.state import ResearchState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
from deep_research.prompt import SYSTEM_PROMPT

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

def evaluator_agent(state: ResearchState) -> ResearchState:
    draft = state["draft"]
    subtopics = state["subtopics"]
    current_coverage = state.get("subtopic_coverage", {})

    user_prompt = f"""
Planned subtopics:
{subtopics}

Current subtopic coverage:
{current_coverage}

Research draft:
{draft}

Evaluate completeness and quality.

Instructions:
- Identify missing or weak subtopics
- Decide how much each subtopic's coverage improved (0.0–0.5)
- Approve ONLY if all subtopics are sufficiently covered (>= 0.85)
- Output valid JSON ONLY
"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])

    evaluation = json.loads(response.content)

    # ---- APPLY COVERAGE UPDATES (EVALUATOR CONTROL) ----
    updated_coverage = current_coverage.copy()

    for subtopic, delta in evaluation.get("coverage_updates", {}).items():
        updated_coverage[subtopic] = min(
            1.0,
            updated_coverage.get(subtopic, 0.0) + float(delta)
        )

    return {
        **state,
        "evaluation": evaluation,
        "critique": evaluation["critique"],
        "missing": evaluation["missing"],
        "improvement_instructions": evaluation["improvement_instructions"],
        "approved": evaluation["approved"],
        "subtopic_coverage": updated_coverage,
        "iteration": state["iteration"] + 1
    }
