import os
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
