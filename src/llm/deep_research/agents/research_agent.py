import logging

from src.llm.deep_research.state import ResearchState
from src.llm.deep_research.prompt import REACT_SYSTEM_PROMPT, REACT_HUMAN_PROMPT
from src.llm.agent_core.agent import Agent
from src.llm.deep_research.tools.web_search import make_web_search_tool
from src.llm.deep_research.constant import DeepResearchConstants

logger = logging.getLogger(__name__)


class Researcher(Agent):
    def __init__(
        self,
        state: ResearchState,
        model: str = DeepResearchConstants.DEFAULT_MODEL,
        temperature: float = DeepResearchConstants.DEFAULT_TEMPERATURE,
        max_iteration: int = DeepResearchConstants.DEFAULT_MAX_RETRIES,
    ):
        self.state = state

        logger.info("Initializing Researcher Agent")

        logger.info(
            "Researcher received %d subtopics | existing_sources=%d",
            len(state.get("subtopics", [])),
            len(state.get("sources", [])),
        )

        missing = state.get("missing")
        logger.info(
            "Researcher received missing feedback: %s | existing_sources=%d",
            "YES" if missing else "NO",
            len(state.get("sources", [])),
        )

        if missing is not None and not isinstance(missing, str):
            raise TypeError(f"missing must be str or None, got {type(missing)}")

        current = state.get("current_subtopic")
        if not current:
            raise ValueError("Researcher invoked without current_subtopic")

        super().__init__(
            system_prompt=REACT_SYSTEM_PROMPT,
            user_prompt=REACT_HUMAN_PROMPT.format(
                query=state["query"],
                topic=current,
                subtopics=state.get("subtopics", []),
                missing=missing,
                improvement_instructions=state.get("improvement_instructions"),
                evidence=[
                    s["content"]
                    for s in state.get("sources", [])
                    if s.get("subtopic") == current
                ],
                scratchpad=state.get("scratchpad", ""),
            ),
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )

    def on_tool_result(self, tool_name: str, args: dict, result: dict):
        scratchpad = self.state.setdefault("scratchpad", "")
        sources = self.state.setdefault("sources", [])
        covered = self.state.setdefault("covered_subtopics", {})
        search_count = self.state.setdefault("search_count", {})

        executed = set(self.state.setdefault("executed_searches", []))

        subtopic = self.state["current_subtopic"]
        query = args.get("query")
        print(f"### query: {query}")

        if query in executed:
            logger.info("Skipping duplicate search: %s", query)
            return

        executed.add(query)
        self.state["executed_searches"] = list(executed)

        count = search_count.get(subtopic, 0)
        if count >= 5:
            logger.warning("Max searches reached for subtopic: %s", subtopic)
            return
        search_count[subtopic] = count + 1

        payload = result.get("results", {})
        responses = payload.get("responses", [])

        if not responses:
            logger.warning("No responses returned for subtopic: %s", subtopic)
            return

        existing_urls = {s["url"] for s in sources}

        facts = []
        for r in responses:
            url = r.get("url")
            content = r.get("content")
            if not url or not content or url in existing_urls:
                continue

            facts.append(
                {
                    "content": content.strip(),
                    "url": url,
                    "source": r.get("source", "web"),
                    "subtopic": subtopic,
                    "query": query,
                    "year": r.get("year"),
                }
            )

        if not facts:
            return

        sources.extend(facts)
        covered[subtopic] = covered.get(subtopic, 0) + len(facts)

        scratchpad += f"\nSEARCH executed for subtopic: {subtopic}"
        for f in facts:
            claim_block = (
                f"\nClaim: {f['content']}\n"
                f"Source: {f['url']}\n"
                f"Dimension: definition\n"
            )
            if claim_block not in scratchpad:
                scratchpad += claim_block

        self.state.update(
            {
                "sources": sources,
                "covered_subtopics": covered,
                "scratchpad": scratchpad,
            }
        )


def research_node(state: ResearchState) -> ResearchState:

    research_agent = Researcher(
        state=state,
        model=DeepResearchConstants.MODEL,
        temperature=DeepResearchConstants.TEMPERATURE,
        max_iteration=DeepResearchConstants.MAX_RETRIES,
    )
    logger.info("Researcher Agent object created sucessfully")
    chat_history = []
    research_agent.add_tool(make_web_search_tool())
    _, _ = research_agent.invoke(chat_history)
    logger.info("Researcher Agent invoke completed sucessfully")
    return state


def extract_atomic_facts(results: list, subtopic: str) -> list[dict]:
    facts = []

    for r in results:
        if not isinstance(r, dict):
            continue

        content = r.get("content")
        url = r.get("url")

        if not content or not url:
            continue

        facts.append(
            {
                "content": content.strip(),
                "url": url,
                "source": r.get("source", "web"),
                "subtopic": subtopic,
            }
        )

    return facts
