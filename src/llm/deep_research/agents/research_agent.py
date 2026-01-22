import re
import logging

from src.llm.deep_research.tools.web_search import web_search
from src.llm.deep_research.state import ResearchState
from src.llm.deep_research.prompt import REACT_SYSTEM_PROMPT, REACT_HUMAN_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

MAX_STEPS = 5
logger = logging.getLogger(__name__)

def research_agent(state: ResearchState) -> ResearchState:
    logger.info("Researcher started")
    scratchpad = state.get("scratchpad", "")
    sources = state["sources"]
    subtopics = state["subtopics"]
    logger.info(
        "Researcher received %d subtopics | existing_sources=%d",
        len(subtopics),
        len(sources),
    )

    
    for topic in subtopics:
        for _ in range(MAX_STEPS):
            react_prompt = REACT_HUMAN_PROMPT.format(
                query=state["query"],
                topic=topic,
                evidence=[s["content"] for s in sources],
                scratchpad=scratchpad,
            )

            response = llm.invoke([
                SystemMessage(content=REACT_SYSTEM_PROMPT),
                HumanMessage(content=react_prompt)
            ])

            text = response.content.strip()
            logger.debug("ReAct output: %s", text)

            if "Action: FINISH" in text:
                scratchpad += "\n" + text
                logger.info("Finished researching topic: %s", topic)
                break

            if "Action: SEARCH" in text:
                try:
                    query = extract_query(text)
                except ValueError:
                    logger.error(
                        "Failed to parse SEARCH action | output=%s",
                        text,
                    )
                    break

                logger.info("Executing web search | query=%s", query)

                try:
                    results = web_search(query, max_results=5)
                except Exception:
                    logger.exception(
                        "Web search failed | query=%s",
                        query,
                    )
                    break

                logger.info(
                    "Search completed | results=%d",
                    len(results),
                )

                scratchpad += f"\n{text}\nObservation: {results}"

                facts = extract_atomic_facts(results)
                sources.extend(facts)

                logger.debug(
                    "Extracted %d atomic facts from search results",
                    len(facts),
                )

            else:
                logger.warning(
                    "Unexpected ReAct output | output=%s",
                    text,
                )
                break

    logger.info(
        "Researcher completed | total_sources=%d | scratchpad_length=%d",
        len(sources),
        len(scratchpad),
    )

    return {
        **state,
        "sources": sources,
        "scratchpad": scratchpad,
    }


def extract_atomic_facts(results: list[dict]) -> list[dict]:
    """
    Extracts one factual claim per result (best-effort).
    Assumes each result contains 'content' and 'url'.
    """
    facts = []

    for r in results:
        if not r.get("content") or not r.get("url"):
            continue

        facts.append({
            "content": r["content"].strip(),
            "url": r["url"],
            "source": r.get("source", "web"),
        })

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