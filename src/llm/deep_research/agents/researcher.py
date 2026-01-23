from deep_research.tools.web_search import web_search
from deep_research.state import ResearchState
from deep_research.prompt import REACT_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import re

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

MAX_STEPS = 5


def research_agent(state: ResearchState) -> ResearchState:
    scratchpad = state.get("scratchpad", "")
    sources = state["sources"]
    subtopics = state["subtopics"]

    for topic in subtopics:
        for _ in range(MAX_STEPS):
            react_prompt = f"""
                Main research question:
                {state['query']}

                Current Topic:
                {topic}

                Current evidence:
                {[s['content'] for s in sources]}

                Scratchpad:
                {scratchpad}

                Decide next step.
            """

            response = llm.invoke(
                [
                    SystemMessage(content=REACT_SYSTEM_PROMPT),
                    HumanMessage(content=react_prompt),
                ]
            )

            text = response.content.strip()

            # ---- PARSE ACTION ----
            if "Action: FINISH" in text:
                scratchpad += "\n" + text
                break

            if "Action: SEARCH" in text:
                query = extract_query(text)

                results = web_search(query, max_results=5)

                scratchpad += f"\n{text}\nObservation: {results}"

                # append atomic facts
                sources.extend(extract_atomic_facts(results))

            else:
                # invalid output → force stop
                break

    return {**state, "sources": sources, "scratchpad": scratchpad}


def extract_atomic_facts(results: list[dict]) -> list[dict]:
    """
    Extracts one factual claim per result (best-effort).
    Assumes each result contains 'content' and 'url'.
    """
    facts = []

    for r in results:
        if not r.get("content") or not r.get("url"):
            continue

        facts.append(
            {
                "content": r["content"].strip(),
                "url": r["url"],
                "source": r.get("source", "web"),
            }
        )

    return facts


def extract_query(text: str) -> str:
    """
    Extracts the query string from:
    Action: SEARCH("query")
    """
    match = re.search(r'Action:\s*SEARCH\("(.+?)"\)', text)
    if not match:
        raise ValueError("SEARCH action found but query could not be parsed")
    return match.group(1)
