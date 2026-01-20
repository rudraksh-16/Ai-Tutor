import requests
import logging

from src.llm.curriculum_agent.utils.rate_limiter import RateLimiter
from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from src.llm.config import LLMConfig

logger = logging.getLogger(__name__)

def make_web_search_tool():
    def web_search_tool(query: str, top_k: int = 5):
        logger.debug("web_search tool invoked | query=%s | top_k=%d", query, top_k)
        return {
            "status": "success",
            "results": google_web_search(query, top_k)
        }

    return Tool(
        func=web_search_tool,
        description="Search the web using Google Custom Search API",
        args_schema=WebSearchArgs,
    )

class WebSearchArgs:
    args = [
        ("query", Args(type=str, description="Search query")),
        ("top_k", Args(type=int, description="Number of results", default=5)),
    ]

google_rate_limiter = RateLimiter(
    max_calls=5,
    period=1.0
)

def google_web_search(query: str, top_k: int = 5) -> list[dict]:
    google_rate_limiter.acquire()

    params = {
        "key": LLMConfig.GOOGLE_SEARCH_API_KEY,
        "cx": LLMConfig.GOOGLE_SEARCH_ENGINE,
        "q": query,
        "num": min(top_k, 10),
    }

    logger.debug("Sending Google search request | query=%s", query)

    response = requests.get(
        LLMConfig.GOOGLE_SEARCH_ENDPOINT,
        params=params,
        timeout=10,
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error("Google search failed | status=%s | error=%s",
                 response.status_code, e)
        raise

    data = response.json()

    if not data.get("items"):
        logger.warning("Google search returned no results | query=%s", query)
        return []

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "snippet": item.get("snippet"),
        })

    logger.info("Google search succeeded | results=%d", len(results))
    return results