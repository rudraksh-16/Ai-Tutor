from typing import Optional, Any
from openai import OpenAI

from src.llm.config import LLMConfig
from src.llm.query_expander.constant import QueryExpanderConstants
from src.llm.query_expander.prompt import QUERY_EXPANDER_PROMPT

client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)


def expand_query(query: str, extra: Optional[Any] = None) -> str:
    """
    Expands a base query using a single LLM call to provide richer context.
    This is a stateless utility function, not an agent.
    """
    try:
        response = client.responses.create(
            model=QueryExpanderConstants.DEFAULT_MODEL,
            temperature=QueryExpanderConstants.DEFAULT_TEMPERATURE,
            input=QUERY_EXPANDER_PROMPT.format(
                query=query,
                extra=extra or "",
            ),
        )

        return response.output_text.strip()

    except Exception as e:
        return query
