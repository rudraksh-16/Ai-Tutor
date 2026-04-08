from src.llm.curriculum_agent.agent import CurriculumAgent
from src.llm.curriculum_agent.constant import CurriculumConstants
from src.llm.curriculum_agent.tools.upsert_curriculum import make_upsert_curriculum_tool
from src.llm.curriculum_agent.tools.get_curriculum import make_get_curriculum_tool
from src.llm.curriculum_agent.tools.web_search import make_web_search_tool
from src.llm.teacher_agent.agent import TeacherAgent
from src.llm.teacher_agent.constant import TeacherConstants


async def run_curriculum_agent(user_id: str, topic_id: str, chat_history: list):
    agent = CurriculumAgent(
        user_id=user_id,
        topic_id=topic_id,
        model=CurriculumConstants.MODEL,
        temperature=CurriculumConstants.TEMPERATURE,
        max_iteration=CurriculumConstants.MAX_ITERATION,
    )
    agent.add_tool(make_upsert_curriculum_tool(user_id, topic_id))
    agent.add_tool(make_get_curriculum_tool(topic_id))
    agent.add_tool(make_web_search_tool())
    async for event in agent.astream(chat_history):
        yield event


async def run_teacher_agent(chapter_id: str, chat_history: list):
    """Create and stream a TeacherAgent. chat_history already contains user message."""
    agent = TeacherAgent(
        chapter_id=chapter_id,
        model=TeacherConstants.MODEL,
        max_iteration=TeacherConstants.MAX_ITERATION,
        temperature=TeacherConstants.TEMPERATURE,
    )
    async for event in agent.run(chat_history=chat_history):
        yield event
