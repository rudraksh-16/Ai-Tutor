from src.llm.teacher_agent.constant import TeacherConstants
from src.llm.teacher_agent.prompt import SYSTEM_PROMPT
from src.llm.agent_core.agent import Agent

from src.llm.teacher_agent.tools.get_outline_content import make_get_outline_content
from src.llm.teacher_agent.tools.get_user_curriculum import make_get_user_curriculum
from src.llm.teacher_agent.tools.get_chapter import make_get_chapter
from src.llm.teacher_agent.tools.update_status import make_update_status
from src.llm.teacher_agent.tools.create_quiz import make_create_quiz


class TeacherAgent(Agent):
    def __init__(
        self,
        chapter_id: str,
        model: str = TeacherConstants.DEFAULT_MODEL_NAME,
        temperature: float = TeacherConstants.DEFAULT_MODEL_TEMPERATURE,
        max_iteration: int = TeacherConstants.DEFAULT_MAX_ITERATION,
    ):
        super().__init__(
            system_prompt=SYSTEM_PROMPT,
            model=model,
            temperature=temperature,
            max_iteration=max_iteration,
        )
        self.chapter_id = chapter_id

    def run(self, chat_history, user_message):
        self.add_tool(make_get_user_curriculum(self.chapter_id))
        self.add_tool(make_get_chapter(self.chapter_id))
        self.add_tool(make_get_outline_content(self.chapter_id))
        self.add_tool(make_update_status(self.chapter_id))
        self.add_tool(make_create_quiz(self.chapter_id))
        if user_message == "":
            raise ValueError("Looks like no input was entered")
        user_input = {"role": "user", "content": user_message}
        chat_history.append(user_input)
        return self.stream(chat_history)
