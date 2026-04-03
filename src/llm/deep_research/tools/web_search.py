import logging
from typing import List, Dict, Any, Optional

from tavily import TavilyClient

from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from src.llm.config import LLMConfig
from src.llm.deep_research.tools.rate_limiter import RateLimiter


logger = logging.getLogger(__name__)


def make_web_search_tool():
    def web_search_tool(query: str, top_k: int = 5):
        logger.debug("web_search tool invoked | query=%s | top_k=%d", query, top_k)
        return {"status": "success", "results": web_search(query, top_k)}

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


rate_limiter = RateLimiter(max_calls=5, period=1.0)
tavily_client = TavilyClient(api_key=LLMConfig.TAVILY_API_KEY)


def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Production-safe web search using Tavily with rate limiting."""
    logger.debug("Web search requested | query=%r | max_results=%d", query, max_results)
    rate_limiter.acquire()

    try:
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            include_raw_content=False,
        )
        return _format_tavily_results(query, response)
    except Exception:
        logger.exception("Web search failed | query=%r", query)
        raise


def _format_tavily_results(query: str, response: dict) -> Dict[str, Any]:
    """Format the raw Tavily response into a structured dictionary."""
    results = {
        "query": query,
        "responses": [
            {
                "title": item.get("title"),
                "content": item.get("content"),
                "url": item.get("url"),
            }
            for item in response.get("results", [])
        ],
    }

    if not results["responses"]:
        logger.warning("Tavily returned no results | query=%r", query)

    logger.info("Web search completed | query=%r | results=%d", query, len(results["responses"]))
    return results
