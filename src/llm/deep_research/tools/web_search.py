import logging
from typing import List, Dict

from tavily import TavilyClient

from src.llm.deep_research.tools.rate_limiter import RateLimiter
from src.llm.config import LLMConfig

logger = logging.getLogger(__name__)

tavily_rate_limiter = RateLimiter(
    max_calls=5,
    period=1.0
)


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Web search tool using Tavily (production-safe).

    - Enforces rate limiting
    - Logs lifecycle events
    - Returns normalized results for agents
    """
    logger.debug("Web search requested | query=%r | max_results=%d", query, max_results)

    tavily_rate_limiter.acquire()

    try:
        search_client = TavilySearch()
        results = search_client.search(query, max_results)

        logger.info(
            "Web search completed | provider=tavily | query=%r | results=%d",
            query,
            len(results),
        )

        return results

    except Exception as exc:
        logger.exception(
            "Web search failed | provider=tavily | query=%r | error=%s",
            query,
            exc,
        )
        raise


class TavilySearch:
    """
    Tavily search client wrapper.

    Keeps SDK usage isolated and testable.
    """

    def __init__(self):
        self.client = TavilyClient(api_key=LLMConfig.TAVILY_API_KEY)
        logger.debug("TavilySearch client initialized")

    def search(self, query: str, max_results: int) -> List[Dict]:
        logger.debug(
            "Sending Tavily search request | query=%r | max_results=%d",
            query,
            max_results,
        )

        response = self.client.search(
            query=query,
            max_results=max_results,
            include_raw_content=False,
        )

        results = [
            {
                "title": item.get("title"),
                "content": item.get("content"),
                "url": item.get("url"),
                "source": "tavily",
            }
            for item in response.get("results", [])
        ]

        if not results:
            logger.warning("Tavily returned no results | query=%r", query)

        return results