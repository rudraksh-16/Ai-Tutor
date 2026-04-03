import logging
from typing import List, Dict, Any
from tavily import TavilyClient

from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from src.llm.config import LLMConfig
from src.llm.deep_research.tools.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class WebSearchArgs:
    args = [
        ("query", Args(type=str, description="Search query")),
        ("top_k", Args(type=int, description="Number of results", default=5)),
    ]

# Common rate limiter for search tools to avoid API exhaustion
search_rate_limiter = RateLimiter(max_calls=5, period=1.0)
tavily_client = TavilyClient(api_key=LLMConfig.TAVILY_API_KEY)

def make_web_search_tool() -> Tool:
    """Factory to create a search tool with rate limiting and error handling."""
    
    async def web_search_tool(query: str, top_k: int = 5) -> Dict[str, Any]:
        logger.debug("web_search tool invoked | query=%s | top_k=%d", query, top_k)
        search_rate_limiter.acquire()

        try:
            results = _perform_tavily_search(query, top_k)
            return {"status": "success", "results": results}
        except Exception as e:
            logger.exception("Web search failed | query=%r", query)
            raise RuntimeError(f"Search failed: {e}")

    return Tool(
        func=web_search_tool,
        description="Search the web for up-to-date information on any topic.",
        args_schema=WebSearchArgs,
    )

def _perform_tavily_search(query: str, top_k: int) -> List[Dict[str, str]]:
    """Isolated search logic using the Tavily client."""
    response = tavily_client.search(
        query=query,
        max_results=top_k,
        include_raw_content=False,
    )

    results = [
        {
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "url": item.get("url", ""),
        }
        for item in response.get("results", [])
    ]

    if not results:
        logger.warning("Tavily returned no results | query=%r", query)
    
    return results
