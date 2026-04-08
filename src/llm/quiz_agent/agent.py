import logging
from typing import Any, AsyncGenerator, Dict, List

from src.llm.agent_core.agent import Agent
from src.llm.quiz_agent.constant import QuizConstants
from src.llm.quiz_agent.prompt import SYSTEM_PROMPT, USER_PROMPT
from src.llm.quiz_agent.tools.get_outline_content import make_get_section_content

logger = logging.getLogger(__name__)


class QuizAgent(Agent):
    """LLM Agent responsible for generating section-level quiz questions.

    This agent focuses on a single sub-chapter (ChapterPlan) and produces
    2-3 multiple choice questions for mastery verification.
    """

    def __init__(
        self,
        section_id: str,
        model: str = QuizConstants.MODEL,
        temperature: float = QuizConstants.TEMPERATURE,
        max_iteration: int = QuizConstants.MAX_ITERATION,
    ) -> None:
        """Initialize the agent with section-specific context.

        Args:
            section_id: The UUID of the ChapterPlan to quiz.
            model: Model identifier.
            temperature: Sampling temperature.
            max_iteration: Max research loops.
        """
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT,
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )
        self.section_id = section_id
        self._register_tools()

    def _register_tools(self) -> None:
        """Add specialized tools for fetching section content."""
        self.add_tool(make_get_section_content(self.section_id))

    async def run(self, chat_history: List[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """Stream the quiz generation process.

        Args:
            chat_history: Optional prior interaction.

        Yields:
            Chunks of the generated JSON output.
        """
        async for event in self.astream(chat_history or []):
            yield event
