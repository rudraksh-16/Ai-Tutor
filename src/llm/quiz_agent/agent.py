from src.llm.quiz_agent.constant import QuizConstants
from src.llm.quiz_agent.prompt import SYSTEM_PROMPT, USER_PROMPT
from src.llm.agent_core.agent import Agent


class QuizAgent(Agent):
    def __init__(
        self,
        chapter_id: str,
        model: str = QuizConstants.DEFAULT_MODEL_NAME,
        temperature: float = QuizConstants.DEFAULT_MODEL_TEMPERATURE,
        max_iteration: int = QuizConstants.DEFAULT_MAX_ITERATION,
    ):
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT,
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )
        self.chapter_id = chapter_id
