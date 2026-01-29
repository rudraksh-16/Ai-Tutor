from dotenv import load_dotenv
import os

load_dotenv()


class LLMConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    USE_HYDE = os.getenv("USE_HYDE", "false").lower() == "true"