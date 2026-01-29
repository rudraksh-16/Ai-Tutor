from typing import Optional, Any

from src.llm.agent_core.agent import Agent
from src.llm.hyde.constant import HydeConstants
from src.llm.hyde.prompt import SYSTEM_PROMPT, USER_PROMPT

class HyDE(Agent):
    def __init__(
        self,
        query: str,
        extra: Optional[Any] = None,
        model: str = HydeConstants.DEFAULT_MODEL,
        temperature: float = HydeConstants.DEFAULT_TEMPERATURE,
    ):
        self.query = query
        self.extra = extra
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT.format(
                query=query,
                extra=extra,
            ),
            model=model,
            temperature=temperature,
        )

def run_hyde(query: str, extra: Optional[Any]=None) -> str:
    hyde_agent = HyDE(
        query=query,
        extra=extra,
        model=HydeConstants.MODEL,
        temperature=HydeConstants.TEMPERATURE,
    )
    chat_history=[]
    response, _ = hyde_agent.invoke(chat_history)
    return response