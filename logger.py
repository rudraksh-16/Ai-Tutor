import logging
from src.llm.config import LLMConfig


def setup_logging():
    logging.basicConfig(
        level="ERROR",
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
