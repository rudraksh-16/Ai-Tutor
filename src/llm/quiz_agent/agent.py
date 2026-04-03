import logging
from src.llm.agent_core.agent import Agent
from src.llm.quiz_agent.constant import QuizConstants
from src.llm.quiz_agent.prompt import SYSTEM_PROMPT, USER_PROMPT

logger = logging.getLogger(__name__)


class QuizAgent(Agent):
    def __init__(
        self,
        chapter_id: str,
        model: str = QuizConstants.MODEL,
        temperature: float = QuizConstants.TEMPERATURE,
        max_iteration: int = QuizConstants.MAX_ITERATION,
    ) -> None:
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT,
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )
        self.chapter_id = chapter_id
