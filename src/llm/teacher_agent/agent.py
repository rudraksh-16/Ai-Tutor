import logging
from typing import List, Dict, Any, AsyncGenerator

from src.llm.agent_core.agent import Agent
from src.llm.teacher_agent.constant import TeacherConstants
from src.llm.teacher_agent.prompt import SYSTEM_PROMPT
from src.llm.teacher_agent.tools.create_quiz import make_create_quiz
from src.llm.teacher_agent.tools.get_chapter import make_get_chapter
from src.llm.teacher_agent.tools.get_outline_content import make_get_outline_content
from src.llm.teacher_agent.tools.get_user_curriculum import make_get_user_curriculum
from src.llm.teacher_agent.tools.update_status import make_update_status

logger = logging.getLogger(__name__)


class TeacherAgent(Agent):
    def __init__(
        self,
        chapter_id: str,
        model: str = TeacherConstants.MODEL,
        temperature: float = TeacherConstants.TEMPERATURE,
        max_iteration: int = TeacherConstants.MAX_ITERATION,
    ) -> None:
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )
        self.chapter_id = chapter_id
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all tools at init time — not per-call."""
        self.add_tool(make_get_user_curriculum(self.chapter_id))
        self.add_tool(make_get_chapter(self.chapter_id))
        self.add_tool(make_get_outline_content(self.chapter_id))
        self.add_tool(make_update_status(self.chapter_id))
        self.add_tool(make_create_quiz(self.chapter_id))

    async def run(self, chat_history: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        """Stream the agent response. chat_history already contains the user message."""
        async for event in self.astream(chat_history):
            yield event
