import requests
import logging
from src.llm.deep_research.tools.rate_limiter import RateLimiter
from src.llm.config import LLMConfig

logger = logging.getLogger(__name__)

tavily_rate_limiter = RateLimiter(
    max_calls=5,
    period=1.0
)


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Tavily web search tool (agent-friendly)
    """
    tavily_rate_limiter.acquire()

    payload = {
        "api_key": LLMConfig.TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }

    logger.debug("Sending Tavily search request | query=%s", query)

    response = requests.post(
        LLMConfig.TAVILY_SEARCH_ENDPOINT,
        json=payload,
        timeout=15,
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            "Tavily search failed | status=%s | error=%s",
            response.status_code, e
        )
        raise

    data = response.json()

    if not data.get("results"):
        logger.warning("Tavily search returned no results | query=%s", query)
        return []

    results = []
    for item in data["results"]:
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("content"),
        })

    logger.info("Tavily search succeeded | results=%d", len(results))
    return results
