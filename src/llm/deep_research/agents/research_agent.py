import logging

from src.llm.deep_research.state import ResearchState
from src.llm.deep_research.prompt import REACT_SYSTEM_PROMPT, REACT_HUMAN_PROMPT
from src.llm.agent_core.agent import Agent
from src.llm.deep_research.tools.web_search import make_web_search_tool
from src.llm.query_expander import expand_query
from src.llm.config import LLMConfig
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
        """Initialize the Researcher Agent with state and LLM parameters."""
        self.state = state
        logger.info("Initializing Researcher Agent | Subtopics count: %d", len(state.get("subtopics", [])))

        query = self._prepare_research_query(state)
        super().__init__(
            system_prompt=REACT_SYSTEM_PROMPT,
            user_prompt=self._format_research_prompt(query, state),
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )

    def _prepare_research_query(self, state: ResearchState) -> str:
        """Construct and optionally expand the research query."""
        current = state.get("current_subtopic")
        if not current:
            raise ValueError("Researcher invoked without current_subtopic")
        
        base_query = f"{state['query']} - {current}"
        if not LLMConfig.ENABLE_QUERY_EXPANSION:
            return base_query
        
        expanded = expand_query(query=base_query, extra=state.get("success_criteria", {}))
        return expanded if expanded is not None else base_query

    def _format_research_prompt(self, query: str, state: ResearchState) -> str:
        """Format the React human prompt with current state context."""
        current = state["current_subtopic"]
        missing = state.get("missing")
        evidence = [s["content"] for s in state.get("sources", []) if s.get("subtopic") == current]
        
        return REACT_HUMAN_PROMPT.format(
            query=query,
            topic=current,
            subtopics=state.get("subtopics", []),
            missing=missing,
            improvement_instructions=state.get("improvement_instructions"),
            evidence=evidence,
            scratchpad=state.get("scratchpad", ""),
        )

    def on_tool_result(self, tool_name: str, args: dict, result: dict) -> None:
        """Handle incoming search results and update the research state."""
        subtopic = self.state["current_subtopic"]
        query = args.get("query")

        if self._is_duplicate_search(query):
            return

        if self._check_search_limit(subtopic):
            return

        payload = result.get("results", {})
        responses = payload.get("responses", [])
        if responses:
            self._process_search_results(responses, subtopic)

    def _is_duplicate_search(self, query: str) -> bool:
        """Check and record unique searches."""
        executed = set(self.state.setdefault("executed_searches", []))
        if query in executed:
            logger.info("Skipping duplicate search: %s", query)
            return True
        executed.add(query)
        self.state["executed_searches"] = list(executed)
        return False

    def _check_search_limit(self, subtopic: str) -> bool:
        """Enforce maximum search limit per subtopic."""
        search_count = self.state.setdefault("search_count", {})
        count = search_count.get(subtopic, 0)
        
        if count >= 5:
            logger.warning("Max searches reached for subtopic: %s", subtopic)
            exhausted = set(self.state.get("search_exhausted", []))
            exhausted.add(subtopic)
            self.state["search_exhausted"] = list(exhausted)
            
            msg = f"\n[INFO] Max search limit reached for subtopic: {subtopic}."
            self.state["scratchpad"] = self.state.get("scratchpad", "") + msg
            return True
        
        search_count[subtopic] = count + 1
        return False

    def _process_search_results(self, responses: list, subtopic: str) -> None:
        """Extract facts and update state with new evidence."""
        facts = extract_atomic_facts(responses, subtopic)
        sources = self.state.setdefault("sources", [])
        existing_urls = {s["url"] for s in sources}
        
        new_facts = [f for f in facts if f["url"] not in existing_urls]
        if not new_facts:
            return

        sources.extend(new_facts)
        covered = self.state.setdefault("covered_subtopics", {})
        covered[subtopic] = covered.get(subtopic, 0) + len(new_facts)
        
        self._update_scratchpad(subtopic, new_facts)

    def _update_scratchpad(self, subtopic: str, facts: list) -> None:
        """Append fresh findings to the agent's scratchpad."""
        scratchpad = self.state.get("scratchpad", "")
        scratchpad += f"\nSEARCH executed for subtopic: {subtopic}"
        for f in facts:
            claim = f"\nClaim: {f['content']}\nSource: {f['url']}\nDimension: definition\n"
            if claim not in scratchpad:
                scratchpad += claim
        self.state["scratchpad"] = scratchpad


def research_node(state: ResearchState) -> ResearchState:

    current = state.get("current_subtopic")

    if current in state.get("search_exhausted", []):
        logger.info(
            "Skipping Researcher: subtopic '%s' search already exhausted",
            current,
        )
        return state

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
