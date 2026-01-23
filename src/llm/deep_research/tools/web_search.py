import requests
import logging
from deep_research.tools.rate_limiter import RateLimiter
from config import Config

logger = logging.getLogger(__name__)

google_rate_limiter = RateLimiter(max_calls=5, period=1.0)


def web_search(query: str, max_results: int = 5) -> str:
    """
    Web search tool (Google can be plugged here).
    """
    print(f"-------- search tool called for query: {query}\n")
    google_rate_limiter.acquire()

    params = {
        "key": Config.GOOGLE_SEARCH_API_KEY,
        "cx": Config.GOOGLE_SEARCH_ENGINE,
        "q": query,
        "num": min(max_results, 10),
    }

    logger.debug("Sending Google search request | query=%s", query)

    response = requests.get(
        Config.GOOGLE_SEARCH_ENDPOINT,
        params=params,
        timeout=10,
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            "Google search failed | status=%s | error=%s", response.status_code, e
        )
        raise

    data = response.json()

    if not data.get("items"):
        logger.warning("Google search returned no results | query=%s", query)
        return []

    results = []
    for item in data.get("items", []):
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet"),
            }
        )

    logger.info("Google search succeeded | results=%d", len(results))
    return results
