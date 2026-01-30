import time
import logging
import threading
from tavily import TavilyClient

from src.llm.agent_core.args_schema import ArgsSchema as Args
from src.llm.agent_core.tool import Tool
from src.llm.config import LLMConfig


logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()

    def acquire(self):
        while True:
            with self.lock:
                now = time.monotonic()
                self.calls = [t for t in self.calls if now - t < self.period]

                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return

                sleep_time = self.period - (now - self.calls[0])

            if sleep_time > 0:
                time.sleep(sleep_time)


class WebSearchArgs:
    args = [
        ("query", Args(type=str, description="Search query")),
        ("top_k", Args(type=int, description="Number of results", default=5)),
    ]

rate_limiter = RateLimiter(max_calls=5, period=1.0)
tavily_client = TavilyClient(api_key=LLMConfig.TAVILY_API_KEY)

def make_web_search_tool():
    def web_search_tool(query: str, top_k: int = 5):
        logger.debug("web_search tool invoked | query=%s | top_k=%d", query, top_k)
        rate_limiter.acquire()

        try:
            response = tavily_client.search(
                query=query,
                max_results=top_k,
                include_raw_content=False,
            )

            results = [
                {
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "url": item.get("url"),
                }
                for item in response.get("results", [])
            ]

            if not results:
                logger.warning("Tavily returned no results | query=%r", query)

            logger.info(
                "Web search completed | query=%r | results=%d",
                query,
                len(results),
            )
            return {
                "status": "success",
                "results": results,
            }
        except Exception:
            logger.exception("Web search failed | query=%r", query)
            raise

    return Tool(
        func=web_search_tool,
        description="Search the web using Google Custom Search API",
        args_schema=WebSearchArgs,
    )
